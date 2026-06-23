use serde::{Deserialize, Serialize};
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ZKProof {
    pub proof_type: String,
    pub hash: String,
    pub sampled_len: usize,
    pub original_len: usize,
    pub timestamp: i64,
}
