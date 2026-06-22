pub struct SignatureGuard;

impl Default for SignatureGuard {
    fn default() -> Self {
        Self::new()
    }
}

impl SignatureGuard {
    pub fn new() -> Self {
        Self
    }

    pub fn sign(&self, _message: &[u8]) -> Vec<u8> {
        vec![0u8; 64]
    }
}
