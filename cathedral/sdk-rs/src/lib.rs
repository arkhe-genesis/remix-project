pub mod grpc_client;

use std::collections::HashMap;
use anyhow::{Result, bail};

use crate::grpc_client::{CathedralGrpcClient};
use crate::grpc_client::cathedral_v1::{Event, EventType, EventMetadata, IngestRequest, SignatureAlgorithm};

use ed25519_dalek::{SigningKey as Ed25519SigningKey, Signer as _};
use fips204::ml_dsa_65::{PrivateKey as MlDsa65PrivateKey};
use fips204::traits::{SerDes, Signer as _};

pub enum AgentKey {
    Ed25519(Ed25519SigningKey),
    MlDsa65(MlDsa65PrivateKey),
}

pub struct CathedralSdk {
    client: CathedralGrpcClient,
    project_id: String,
    agent_id: String,
    key: Option<AgentKey>,
}

impl CathedralSdk {
    pub async fn new(endpoint: String, project_id: String, agent_id: String, key: Option<AgentKey>) -> Result<Self> {
        let client = CathedralGrpcClient::connect(endpoint).await?;
        Ok(Self {
            client,
            project_id,
            agent_id,
            key,
        })
    }

    pub async fn emit_design_proposed(
        &mut self,
        design_hash: String,
        parent_hashes: Vec<String>,
        parameters: HashMap<String, f64>,
        rationale: String,
    ) -> Result<()> {
        let payload = serde_json::json!({
            "parameters": parameters,
            "rationale": rationale,
        });

        let event = Event {
            event_id: uuid::Uuid::new_v4().to_string(),
            timestamp: Some(prost_types::Timestamp {
                seconds: chrono::Utc::now().timestamp(),
                nanos: chrono::Utc::now().timestamp_subsec_nanos() as i32,
            }),
            event_type: EventType::DesignProposed.into(),
            design_hash,
            parent_hashes,
            payload_json: payload.to_string(),
            metadata: Some(EventMetadata {
                domain: "aerospace".to_string(),
                confidence: 0.5,
                compute_cost_usd: 0.0,
                tags: vec![],
            }),
        };

        // Serialize the payload for signing
        let batch_hash = {
            let mut hasher = blake3::Hasher::new();
            hasher.update(event.event_id.as_bytes());
            hasher.update(event.design_hash.as_bytes());
            hasher.finalize().as_bytes().to_vec()
        };

        let (agent_signature, signature_algorithm) = match &self.key {
            Some(AgentKey::Ed25519(sk)) => {
                let sig = sk.sign(&batch_hash);
                (Some(sig.to_bytes().to_vec()), Some(SignatureAlgorithm::Ed25519 as i32))
            },
            Some(AgentKey::MlDsa65(sk)) => {
                let sig = sk.try_sign(&batch_hash, &[]).map_err(|e| anyhow::anyhow!("ML-DSA signing failed: {}", e))?; // Sign empty context for now
                (Some(sig.to_vec()), Some(SignatureAlgorithm::MlDsa65 as i32))
            },
            None => (None, None),
        };

        let request = IngestRequest {
            project_id: self.project_id.clone(),
            agent_id: self.agent_id.clone(),
            events: vec![event],
            batch_id: None,
            agent_signature,
            batch_hash: Some(batch_hash),
            signature_algorithm,
        };

        self.client.ingest(request).await?;
        Ok(())
    }
}
