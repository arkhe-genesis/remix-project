use crc16::*;
use image::Luma;
use qrcode::QrCode;
use std::fmt::Write;

pub struct PixQrData {
    pub merchant_name: String,
    pub merchant_city: String,
    pub pix_key: String,
    pub amount: Option<f64>,
    pub txid: String,
}

impl PixQrData {
    pub fn to_br_code(&self) -> String {
        let mut payload = String::new();
        // Payload Format Indicator (ID 00)
        payload.push_str("000201");
        // Merchant Account Information (ID 26) – PIX key
        write!(payload, "26360014BR.GOV.BCB.PIX0105{}", self.pix_key).unwrap();
        // Merchant Category Code (ID 52) – 0000
        payload.push_str("52040000");
        // Transaction Currency (ID 53) – 986 (BRL)
        payload.push_str("5303986");
        // Transaction Amount (ID 54) – optional
        if let Some(amount) = self.amount {
            write!(payload, "54{:02}{:.2}", amount.to_string().len(), amount).unwrap();
        }
        // Country Code (ID 58) – BR
        payload.push_str("5802BR");
        // Merchant Name (ID 59)
        write!(payload, "59{:02}{}", self.merchant_name.len(), self.merchant_name).unwrap();
        // Merchant City (ID 60)
        write!(payload, "60{:02}{}", self.merchant_city.len(), self.merchant_city).unwrap();
        // Additional Data Field Template (ID 62) – TXID
        write!(payload, "62070503{}", self.txid).unwrap();
        // CRC‑16 (ID 63) over all preceding data
        payload.push_str("6304");
        let crc = State::<XMODEM>::calculate(payload.as_bytes());
        write!(payload, "{:04X}", crc).unwrap();
        payload
    }

    pub fn generate_qr_image(&self) -> Vec<u8> {
        let code = QrCode::new(self.to_br_code()).unwrap();
        let image = code.render::<Luma<u8>>().build();
        let mut png_bytes = Vec::new();
        let mut cursor = std::io::Cursor::new(&mut png_bytes);
        image::write_buffer_with_format(
            &mut cursor,
            &image,
            image.width(),
            image.height(),
            image::ColorType::L8,
            image::ImageFormat::Png,
        ).unwrap();
        png_bytes
    }
}
