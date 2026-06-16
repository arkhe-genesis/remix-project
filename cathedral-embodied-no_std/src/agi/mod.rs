pub mod picoads_integration;

pub struct AegisEvolution {}
pub struct ContextEmbedding {
    pub stagnation_rounds: u32,
    pub acceptance_rate: f64,
    pub avg_interference: f64,
}
