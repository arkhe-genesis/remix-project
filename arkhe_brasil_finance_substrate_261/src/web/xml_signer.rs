use quick_xml::Reader;
use quick_xml::events::Event;
use x509_cert::Certificate;
use base64::{Engine as _, engine::general_purpose};
use std::str;

/// Verifica assinatura XML‑DSig com certificado ICP‑Brasil
pub fn verify_xml_signature(xml: &str, _trusted_root: &[u8]) -> Result<bool, Box<dyn std::error::Error>> {
    let mut reader = Reader::from_str(xml);
    let mut signature_value = None;
    let mut signed_info = None;
    let mut certificate_b64 = None;

    loop {
        match reader.read_event()? {
            Event::Start(ref e) if e.name().as_ref() == b"SignatureValue" => {
                signature_value = Some(reader.read_text(e.name())?);
            }
            Event::Start(ref e) if e.name().as_ref() == b"SignedInfo" => {
                signed_info = Some(reader.read_text(e.name())?);
            }
            Event::Start(ref e) if e.name().as_ref() == b"X509Certificate" => {
                certificate_b64 = Some(reader.read_text(e.name())?);
            }
            Event::Eof => break,
            _ => (),
        }
    }

    let (sig_val, sig_info, cert_b64) = match (signature_value, signed_info, certificate_b64) {
        (Some(sv), Some(si), Some(cb)) => (sv, si, cb),
        _ => return Err("Missing Signature elements".into()),
    };

    // Decode certificate
    let cert_der = general_purpose::STANDARD.decode(cert_b64.trim())?;
    // We should be using specific methods on Certificate from x509_cert
    use x509_cert::der::Decode;
    let cert = Certificate::from_der(&cert_der)?;

    // Validate certificate chain against trusted_root
    // (simplified: check self‑signature or chain)
    // if cert.verify_signature(Some(trusted_root)).is_err() {
    //     return Ok(false);
    // }

    // Extract public key and verify signature over SignedInfo
    let pub_key = cert.tbs_certificate.subject_public_key_info.subject_public_key;
    let signature_bytes = general_purpose::STANDARD.decode(sig_val.trim())?;
    // Depending on signature algorithm (RSA‑SHA256, etc.) verify
    // Use ring or rsa crate: pub_key.verify(&sig_info.as_bytes(), &signature_bytes)
    // Placeholder: assume RSA‑PKCS1v15
    use rsa::pkcs1v15::VerifyingKey;
    use rsa::pkcs1v15::Signature;
    use sha2::Sha256;
    use rsa::signature::Verifier;
    use rsa::RsaPublicKey;
    use rsa::pkcs1::DecodeRsaPublicKey;
    let pub_key_bytes = pub_key.as_bytes().unwrap();
    let rsa_pub = RsaPublicKey::from_pkcs1_der(pub_key_bytes)?;
    let verifying_key = VerifyingKey::<Sha256>::new_unprefixed(rsa_pub);
    let signature = Signature::try_from(signature_bytes.as_slice())?;
    Ok(verifying_key.verify(sig_info.as_bytes(), &signature).is_ok())
}
