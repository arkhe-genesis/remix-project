use serde::{Deserialize, Serialize};

#[derive(Clone, Serialize, Deserialize, Debug)]
pub struct MemoryEntry {
    pub did: String,
    pub content: String,
    pub thinking: Option<String>,
    pub signature: Vec<u8>,
    pub timestamp: i64,
    pub embedding: Option<Vec<f32>>,
}

#[derive(Clone, Serialize, Deserialize, Debug)]
pub struct ExecutionReceipt {
    pub id: String,
    pub merkle_root: String,
    pub timestamp: i64,
}
