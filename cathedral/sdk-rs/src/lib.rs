pub mod grpc_client;

use std::collections::HashMap;
use anyhow::Result;
use serde_json::Value;

use crate::grpc_client::{CathedralGrpcClient, cathedral_v1};
use crate::grpc_client::cathedral_v1::{Event, EventType, EventMetadata, IngestRequest, GovernanceRequest, GovernanceVerdict};

pub struct CathedralSdk {
    client: CathedralGrpcClient,
    project_id: String,
    agent_id: String,
}

impl CathedralSdk {
    pub async fn new(endpoint: String, project_id: String, agent_id: String) -> Result<Self> {
        let client = CathedralGrpcClient::connect(endpoint).await?;
        Ok(Self {
            client,
            project_id,
            agent_id,
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

        let request = IngestRequest {
            project_id: self.project_id.clone(),
            agent_id: self.agent_id.clone(),
            events: vec![event],
            batch_id: None,
        };

        self.client.ingest(request).await?;
        Ok(())
    }
}
