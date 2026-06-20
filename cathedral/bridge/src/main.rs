mod grpc_service;

use tonic::transport::Server;
use grpc_service::{CathedralBridgeImpl, cathedral_v1::cathedral_bridge_server::CathedralBridgeServer};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let addr = "[::1]:50051".parse()?;
    let bridge = CathedralBridgeImpl::default();

    println!("CathedralBridgeServer listening on {}", addr);

    Server::builder()
        .add_service(CathedralBridgeServer::new(bridge))
        .serve(addr)
        .await?;

    Ok(())
}
