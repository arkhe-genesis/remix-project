import os

base_dir = "cathedral-agi-omega-v13"

structure = {
    "": [
        "README.md",
        "LICENSE",
        "pyproject.toml",
        "requirements.txt",
        "LINKS.md"
    ],
    "cathedral_agi": [
        "__init__.py",
        "hermes_agent.py",
        "mcts_planner.py",
        "discourse_detector.py",
        "protocolo_corte.py",
        "self_amendment_engine.py"
    ],
    "cathedral_agi/memory": [
        "episodic_memory.py",
        "semantic_memory.py",
        "encrypted_space_backend.py"
    ],
    "cathedral_crypto": [
        "bls_utils.py",
        "ml_kem_hybrid.py",
        "ml_dsa_hybrid.py",
        "tpm_wrapper.py"
    ],
    "cathedral_execution": [
        "ona_runner_adapter.py",
        "mxc_wrapper.py",
        "proof_carrying_task.py",
        "veto_plugin_stub.py"
    ],
    "cathedral_security": [
        "vvah_skill.py",
        "sarif_parser.py",
        "cwe_mapper.py"
    ],
    "cathedral_storage": [
        "encrypted_space_client.py",
        "fast_forward_verifier.py",
        "log_anchor.py"
    ],
    "cathedral_governance": [
        "ic_agi_governance.py",
        "rbb_chain_client.py",
        "governance_contract.sol",
        "mobile_notifier.py"
    ],
    "cathedral_verification/lean4_proofs": [
        "CathedralAGI.lean",
        "OntologyConsistency.lean",
        "MutationValidator.lean"
    ],
    "cathedral_verification": [
        "hax_pipeline.py",
        "safe_extraction_wsl.ps1"
    ],
    "tests": [
        "test_ic_agi.py",
        "test_adversarial_metacognition.py",
        "test_krum_aggregator.py",
        "test_vvah_integration.py"
    ],
    "docker": [
        "docker-compose.ona.yml",
        "docker-compose.mxc.yml",
        "Dockerfile.cathedral",
        "Dockerfile.rbb"
    ],
    "docs": [
        "architecture.md",
        "deployment_guide.md",
        "threat_model.md"
    ],
    "docs/presentations": [],
    "integrations": [
        "proof_carrying_task.json",
        "ona_webhook_listener.py",
        "encrypted_space_contract.json",
        "vvah_skill_config.yaml"
    ]
}

links_md_content = """# Referências Externas – Cathedral AGI Stack

## Tecnologias Core
- [Hermes Agent](https://github.com/NousResearch/hermes-agent)
- [Lean 4](https://lean-lang.org)
- [BLS12‑381 (blst)](https://github.com/supranational/blst)

## Camada de Execução
- [ONA (antigo Gitpod)](https://ona.dev)
- [Veto Security](https://ona.com/docs/security#veto)
- [Microsoft MXC](https://learn.microsoft.com/windows/ai/mxc)

## Análise de Vulnerabilidades
- [Visa VVAH](https://github.com/visa/visa-vulnerability-agentic-harness)
- [SARIF Specification](https://sarifweb.org)

## Memória Imutável
- [Encrypted Spaces](https://encryptedspaces.org)
- [Whitepaper PDF](https://encryptedspaces.org/whitepapers/encrypted-spaces.pdf)

## Blockchain Soberana
- [RBB Chain](https://rbbchain.gov.br)
- [Web3.py](https://web3py.readthedocs.io)
"""

def create_structure():
    for d, files in structure.items():
        dir_path = os.path.join(base_dir, d)
        os.makedirs(dir_path, exist_ok=True)
        for f in files:
            file_path = os.path.join(dir_path, f)
            with open(file_path, "w", encoding="utf-8") as f_obj:
                if f == "LINKS.md":
                    f_obj.write(links_md_content)
                elif f.endswith(".py"):
                    f_obj.write("# Selo do repositório\nseal = \"CATHEDRAL-REPO-STRUCTURE-v13.1-2026-06-11\"\n")
                elif f == "README.md":
                    f_obj.write("# Cathedral AGI Omega v13\n\nSelo do repositório: CATHEDRAL-REPO-STRUCTURE-v13.1-2026-06-11\n")
                elif f == "LICENSE":
                    f_obj.write("Apache 2.0\n")
                else:
                    pass

if __name__ == "__main__":
    create_structure()
    print("Estrutura e referências geradas. Selo: CATHEDRAL-REPO-STRUCTURE-v13.1-2026-06-11")
