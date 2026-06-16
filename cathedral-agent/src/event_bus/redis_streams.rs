//! Cathedral ARKHE v28.3 — Redis Streams for Event Replay
//! Persistência de eventos em Redis Streams com suporte a replay, consumer groups e retenção.
//!
//! Selo: CATHEDRAL-ARKHE-v28.3-REDIS-STREAMS-2026-06-16
//! Arquiteto ORCID: 0009-0005-2697-4668

use redis::{Client as RedisClient, AsyncCommands, RedisResult};
use serde::{Serialize, Deserialize};
use std::collections::HashMap;
use crate::event_bus::AcpMessage;

/// Gerenciador de Redis Streams para eventos do Event Bus.
pub struct RedisStreamManager {
    client: RedisClient,
    stream_key: String,
    consumer_group: String,
    consumer_name: String,
}

impl RedisStreamManager {
    /// Cria um novo gerenciador de streams.
    pub fn new(redis_url: &str, stream_key: &str, consumer_group: &str, consumer_name: &str) -> Result<Self, String> {
        let client = RedisClient::open(redis_url).map_err(|e| e.to_string())?;
        Ok(Self {
            client,
            stream_key: stream_key.to_string(),
            consumer_group: consumer_group.to_string(),
            consumer_name: consumer_name.to_string(),
        })
    }

    /// Adiciona um evento ao stream (produção).
    pub async fn add_event(&self, event: &AcpMessage) -> Result<String, String> {
        let mut conn = self.client.get_async_connection().await.map_err(|e| e.to_string())?;
        let serialized = serde_json::to_string(event).map_err(|e| e.to_string())?;

        // Redis Stream entry: campo "data"
        let id: String = conn.xadd(
            &self.stream_key,
            "*",
            &[("data", &serialized)],
        ).await.map_err(|e| e.to_string())?;

        Ok(id)
    }

    /// Cria o consumer group (se não existir).
    pub async fn create_consumer_group(&self) -> Result<(), String> {
        let mut conn = self.client.get_async_connection().await.map_err(|e| e.to_string())?;
        // XGROUP CREATE stream_key group_name $ MKSTREAM (cria se não existir)
        let result: RedisResult<()> = conn.xgroup_create(
            &self.stream_key,
            &self.consumer_group,
            "$", // start from end
            true, // mkstream
        ).await;
        // Ignora erro se grupo já existe
        match result {
            Ok(_) => Ok(()),
            Err(e) => if e.to_string().contains("BUSYGROUP") { Ok(()) } else { Err(e.to_string()) },
        }
    }

    /// Lê novos eventos (consumo) – útil para replay.
    pub async fn read_events(&self, count: usize, block_ms: Option<u64>) -> Result<Vec<AcpMessage>, String> {
        let mut conn = self.client.get_async_connection().await.map_err(|e| e.to_string())?;

        // XREADGROUP GROUP group consumer STREAMS stream_key > (novas mensagens)
        let result: RedisResult<Vec<(String, HashMap<String, String>)>> = conn.xread_options()
            .group(&self.consumer_group, &self.consumer_name)
            .count(count)
            .block(block_ms.unwrap_or(0))
            .read(&[&self.stream_key])
            .await;

        let entries = result.map_err(|e| e.to_string())?;
        let mut events = Vec::new();
        for (_stream, messages) in entries {
            for (_id, fields) in messages {
                if let Some(data) = fields.get("data") {
                    if let Ok(event) = serde_json::from_str(data) {
                        events.push(event);
                    }
                }
            }
        }
        Ok(events)
    }

    /// Replay de eventos antigos (desde um ID específico ou início).
    pub async fn replay_from(&self, start_id: &str, count: usize) -> Result<Vec<AcpMessage>, String> {
        let mut conn = self.client.get_async_connection().await.map_err(|e| e.to_string())?;
        // XRANGE stream_key start_id end_id
        let end = if start_id == "0" { "-" } else { "+" };
        let result: RedisResult<Vec<(String, HashMap<String, String>)>> = conn.xrange(
            &self.stream_key,
            start_id,
            end,
            Some(count),
        ).await;

        let entries = result.map_err(|e| e.to_string())?;
        let mut events = Vec::new();
        for (_id, fields) in entries {
            if let Some(data) = fields.get("data") {
                if let Ok(event) = serde_json::from_str(data) {
                    events.push(event);
                }
            }
        }
        Ok(events)
    }

    /// Acknowledge mensagens processadas (evita reprocessamento).
    pub async fn ack_events(&self, event_ids: &[String]) -> Result<(), String> {
        let mut conn = self.client.get_async_connection().await.map_err(|e| e.to_string())?;
        for id in event_ids {
            let _: () = conn.xack(&self.stream_key, &self.consumer_group, &[id])
                .await.map_err(|e| e.to_string())?;
        }
        Ok(())
    }

    /// Trim do stream (manter apenas últimos N eventos).
    pub async fn trim(&self, maxlen: usize) -> Result<(), String> {
        let mut conn = self.client.get_async_connection().await.map_err(|e| e.to_string())?;
        let _: () = conn.xtrim(&self.stream_key, maxlen).await.map_err(|e| e.to_string())?;
        Ok(())
    }
}

/// Exemplo de uso: consumir eventos continuamente (loop de replay)
pub async fn consume_events_loop(manager: &RedisStreamManager) -> Result<(), String> {
    manager.create_consumer_group().await?;
    loop {
        let events = manager.read_events(10, Some(1000)).await?;
        for event in events {
            // Processar evento (ex: reenviar para orquestrador)
            println!("[Replay] Received event: {:?}", event.msg_id);
            // ACK após processamento
            // manager.ack_events(&[event_id]).await?;
        }
        tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
    }
}
