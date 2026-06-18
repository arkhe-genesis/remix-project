use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ResourceMetadata {
    pub id: String,
    pub version: String,
    pub state: ResourceState,
    pub created_at: u64,
    pub updated_at: u64,
    pub author: String,
    pub tags: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum ResourceState {
    Active,
    Inactive,
    Deprecated,
}

pub trait Resource: Send + Sync {
    fn metadata(&self) -> &ResourceMetadata;
    fn metadata_mut(&mut self) -> &mut ResourceMetadata;
    fn as_any(&self) -> &dyn std::any::Any;
    fn as_any_mut(&mut self) -> &mut dyn std::any::Any;
    fn to_bytes(&self) -> Result<Vec<u8>, String>;
    fn from_bytes(bytes: &[u8]) -> Result<Self, String> where Self: Sized;
}
