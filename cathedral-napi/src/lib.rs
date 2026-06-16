use napi::bindgen_prelude::*;
use napi_derive::napi;
use serde::{Serialize, Deserialize};

#[derive(Serialize, Deserialize)]
struct MemoryProof {
    merkle_root: String,
    timestamp: u64,
}

#[derive(Serialize, Deserialize)]
#[napi(object)]
pub struct JsMemoryProof {
    pub merkle_root: String,
    pub timestamp: f64,
}

#[napi]
pub async fn prove_memory_state() -> napi::Result<JsMemoryProof> {
    // Call your DLA engine (replace with actual implementation)
    let proof = call_dla_prove_memory_state_impl().await
        .map_err(|e| napi::Error::from_reason(e.to_string()))?;

    Ok(JsMemoryProof {
        merkle_root: proof.merkle_root,
        timestamp: proof.timestamp as f64,
    })
}

async fn call_dla_prove_memory_state_impl() -> std::result::Result<MemoryProof, Box<dyn std::error::Error + Send + Sync>> {
    // Here you would call your DLA engine (e.g., via FFI or internal API)
    // For demonstration, return mock proof
    let merkle_root = hex::encode(blake3::hash(b"mock memory state").as_bytes());
    Ok(MemoryProof {
        merkle_root,
        timestamp: std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_secs(),
    })
}
