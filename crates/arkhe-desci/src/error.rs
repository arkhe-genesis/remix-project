use thiserror::Error;

#[derive(Error, Debug)]
pub enum DesciError {
    #[error("Invariant violation: {0}")]
    InvariantViolation(String),
    #[error("Plugin validation failed: {0}")]
    PluginValidation(String),
    #[error("PII detected: {0}")]
    PiiDetected(String),
    #[error("LLM error: {0}")]
    LlmError(String),
    #[error("IPFS error: {0}")]
    IpfsError(String),
    #[error("CCIP error: {0}")]
    CcipError(String),
    #[error("Serialization error: {0}")]
    Serialization(#[from] serde_json::Error),
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
    #[error("Parse error: {0}")]
    Parse(String),
    #[error("Not implemented: {0}")]
    NotImplemented(String),
    #[error("Internal error: {0}")]
    Internal(String),
}

pub type Result<T> = std::result::Result<T, DesciError>;
