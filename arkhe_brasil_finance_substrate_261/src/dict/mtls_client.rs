use reqwest::{Client, Identity};
use serde::Deserialize;
use std::fs;
use std::path::Path;

pub struct DictApiClient {
    client: Client,
    base_url: String,
}

impl DictApiClient {
    pub fn new(cert_path: &Path, key_path: &Path, base_url: &str) -> Result<Self, Box<dyn std::error::Error>> {
        let cert_pem = fs::read(cert_path)?;
        let key_pem = fs::read(key_path)?;
        let identity = Identity::from_pem(&[cert_pem, key_pem].concat())?;

        let client = Client::builder()
            .identity(identity)
            .use_rustls_tls()  // ou native-tls com feature
            .build()?;

        Ok(Self { client, base_url: base_url.to_string() })
    }

    pub async fn resolve_dict(&self, key: &str) -> Result<DictEntry, Box<dyn std::error::Error>> {
        let url = format!("{}/api/dict/v1/entries/{}", self.base_url, key);
        let resp = self.client.get(&url).send().await?;
        let entry = resp.json::<DictEntry>().await?;
        Ok(entry)
    }
}

#[derive(Deserialize, Debug)]
pub struct AccountInfo {
    // ...
}

#[derive(Deserialize, Debug)]
pub struct DictEntry {
    pub key: String,
    pub name: String,
    pub cpf_cnpj: String,
    pub account: AccountInfo,
    // ...
}
