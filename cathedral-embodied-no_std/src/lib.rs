pub mod agi;
pub mod policy {
    pub struct ZkMemoryProofPolicy {}
    impl ZkMemoryProofPolicy {
        pub fn should_require_memory_proof_for_recommendation(&self, _hub: Option<&str>, _value: f64) -> bool {
            false
        }
    }
}
pub mod picoads {
    pub struct PicoAdsClient {}
    impl PicoAdsClient {
        pub async fn get_recommendations(&self, _query: &str, _hub: Option<&str>, _limit: Option<u32>) -> Result<Vec<String>, String> {
            Ok(vec![])
        }
    }
}
pub mod dla {
    pub struct MemoryProof {
        pub merkle_root: String,
    }
    pub fn prove_memory_state() -> Result<MemoryProof, String> {
        Ok(MemoryProof { merkle_root: "mock_root".to_string() })
    }
}
