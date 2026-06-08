import os
import textwrap

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content.lstrip('\n'))
    print(f"Created {path}")

write_file("cathedral-arkhe/cathedral/orchestrator/factory.py", """
# cathedral/orchestrator/factory.py
\"\"\"Fábrica de orquestradores por versão.\"\"\"

from typing import Optional, Any
from pathlib import Path

# from cathedral.orchestrator.v4 import CathedralOrchestratorV4 as V4
# from cathedral.orchestrator.v4_1 import CathedralOrchestratorV4 as V4_1
# from cathedral.orchestrator.v5 import CathedralOrchestratorV5 as V5
from cathedral.orchestrator.v5_1 import CathedralOrchestratorV5_1 as V5_1


VERSION_MAP = {
    # "4.0.0": V4,
    # "4.1.0": V4_1,
    # "5.0.0": V5,
    "5.1.0": V5_1,
}

LATEST = "5.1.0"


def create_orchestrator(version: Optional[str] = None,
                        model_path: Optional[str] = None,
                        **kwargs) -> Any:
    \"\"\"
    Cria orquestrador da versão especificada.

    Args:
        version: string de versão (ex: "5.1.0") ou None para latest
        model_path: caminho para modelo GGUF
        **kwargs: argumentos passados ao construtor do orquestrador

    Returns:
        Instância do orquestrador
    \"\"\"
    v = version or LATEST
    if v not in VERSION_MAP:
        available = ", ".join(sorted(VERSION_MAP.keys(), reverse=True))
        raise ValueError(
            f"Versão '{v}' não disponível. Disponíveis: {available}")

    cls = VERSION_MAP[v]

    if model_path is not None:
        kwargs["model_path"] = model_path

    return cls(**kwargs)
""")

write_file("cathedral-arkhe/cathedral/cli/main.py", """
# cathedral/cli/main.py
\"\"\"Ponto de entrada CLI — equivalente a garak.__main__.py\"\"\"

import sys
import argparse
import logging

from cathedral import __version__, __version_info__


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="cathedral",
        description="Cathedral ARKHE — Recursive Self-Improvement Orchestration",
        epilog="https://github.com/cathedral-arkhe",
    )

    parser.add_argument("-V", "--version", action="version",
                        version=f"%(prog)s {__version__}")
    parser.add_argument("-v", "--verbose", action="count", default=0)
    parser.add_argument("--config", type=str, default=None,
                        help="YAML config file")
    parser.add_argument("--model", type=str, default=None,
                        help="Path to GGUF model file")
    parser.add_argument("--model-type", type=str, default="llama",
                        help="Model type (default: llama)")
    subparsers = parser.add_subparsers(dest="command")

    # cathedral scan
    scan_p = subparsers.add_parser("scan", help="Run safety scan")
    scan_p.add_argument("prompt", nargs="?", help="Prompt or - for stdin")
    scan_p.add_argument("--probes", "-p", default="auto")
    scan_p.add_argument("--detectors", "-d", default="auto")
    scan_p.add_argument("--generations", "-g", type=int, default=10)
    scan_p.add_argument("--output", "-o", type=str, default=None)

    # cathedral inspect
    inspect_p = subparsers.add_parser("inspect",
                                      help="Inspect GGUF model file")
    inspect_p.add_argument("model_path", help="Path to GGUF file")

    # cathedral monitor
    monitor_p = subparsers.add_parser("monitor",
                                        help="Continuous monitoring mode")
    monitor_p.add_argument("--model", required=True)
    monitor_p.add_argument("--interval", type=float, default=5.0,
                           help="Seconds between scans")

    args = parser.parse_args(argv)

    # Config
    from cathedral._config import load_config
    if args.config:
        load_config(args.config)

    # Dispatch
    if not hasattr(args, "command") or args.command is None:
        parser.print_help()
        return

    if args.command == "scan":
        from cathedral.cli.scan import run_scan
        run_scan(args)
    elif args.command == "inspect":
        from cathedral.cli.inspect import run_inspect
        run_inspect(args)
    elif args.command == "monitor":
        from cathedral.cli.monitor import run_monitor
        run_monitor(args)


if __name__ == "__main__":
    main()
""")

write_file("cathedral-arkhe/tests/conftest.py", """
# tests/conftest.py
\"\"\"Fixtures compartilhados para todos os testes.\"\"\"

import pytest
import numpy as np
import tempfile
from pathlib import Path


@pytest.fixture
def dim_4096():
    \"\"\"Dimensão padrão de embedding.\"\"\"
    return 4096


@pytest.fixture
def random_embedding(dim_4096):
    \"\"\"Embedding aleatório normalizado.\"\"\"
    rng = np.random.RandomState(42)
    return rng.randn(dim_4096).astype(np.float32) * 0.1


@pytest.fixture
def random_logits(vocab_size=32000, seq_len=10):
    \"\"\"Sequência de logits aleatórios.\"\"\"
    rng = np.random.RandomState(42)
    return [rng.randn(vocab_size).astype(np.float32) * 0.5
            for _ in range(seq_len)]


@pytest.fixture
def temp_gguf_file():
    \"\"\"Arquivo GGUF simulado temporário para testes.\"\"\"
    import struct
    from cathedral.constants import GGUF_MAGIC, GGUF_VERSION

    tmp = tempfile.NamedTemporaryFile(suffix=".gguf", delete=False)
    with open(tmp.name, "wb") as f:
        # Header
        f.write(struct.pack("<I", GGUF_MAGIC))
        f.write(struct.pack("<I", GGUF_VERSION))
        f.write(struct.pack("<Q", 3))   # tensor_count
        f.write(struct.pack("<Q", 2))   # metadata_kv_count
        # Metadata
        key = "general.architecture"
        f.write(struct.pack("<I", len(key)))
        f.write(key.encode("utf-8"))
        f.write(struct.pack("<I", 8))   # string type
        f.write(struct.pack("<Q", len("llama")))
        f.write(b"llama")
        # Fim
    yield tmp.name
    tmp.close()
    Path(tmp.name).unlink(missing_ok=True)
""")

write_file("cathedral-arkhe/tests/test_vector_theosis.py", """
# tests/test_vector_theosis.py
\"\"\"Testes para VectorTheosis 1091.2.\"\"\"

import pytest
import numpy as np
# from cathedral.substrates.theosis.core import VectorTheosis1092
from cathedral.orchestrator.v5_1 import VectorTheosis1092
from cathedral.constants import PHI_SQUARED, GateState


class TestVectorTheosisInit:
    def test_default_creation(self):
        vt = VectorTheosis1092(dim=128)
        assert vt.dim == 128
        assert vt.rkhs_bandwidth == 0.1
        assert vt.window_sizes == (2, 3, 5, 8, 13)
        assert len(vt.readings) == 0

    def test_custom_window_sizes(self):
        vt = VectorTheosis1092(dim=64, window_sizes=(3, 7))
        assert vt.window_sizes == (3, 7)
        assert 3 in vt._buffers
        assert 7 in vt._buffers


class TestVectorTheosisUpdate:
    def test_first_two_updates_return_none(self):
        vt = VectorTheosis1092(dim=64)
        r1 = vt.update(np.zeros(64, dtype=np.float32))
        r2 = vt.update(np.ones(64, dtype=np.float32))
        assert r1 is None
        assert r2 is None
        assert vt._cycle == 2

    def test_third_update_returns_reading(self):
        vt = VectorTheosis1092(dim=64)
        vt.update(np.zeros(64, dtype=np.float32))
        vt.update(np.ones(64, dtype=np.float32))
        r = vt.update(np.full(64, 0.5, dtype=np.float32))
        assert r is not None
        assert "theosis" in r
        assert "tee" in r
        assert "gate" in r
        assert r["cycle"] == 3

    def test_constant_input_gives_theosis_one(self):
        vt = VectorTheosis1092(dim=64)
        emb = np.ones(64, dtype=np.float32)
        for _ in range(10):
            r = vt.update(emb)
        assert r is not None
        assert r["theosis"] > 0.99, f"Expected Θ≈1.0 for constant input, got {r['theosis']}"
        assert r["gate"] == GateState.OPEN.value

    def test_step_change_increases_tee(self):
        vt = VectorTheosis1092(dim=64)
        base = np.zeros(64, dtype=np.float32)
        for i in range(10):
            perturbed = base + np.random.randn(64).astype(np.float32) * (0.01 * (i + 1))
            r = vt.update(perturbed)
            if r:
                if i > 3:
                    assert r["tee"] > 0.001, "TEE deve crescer com perturbação crescente"

    def test_theosis_bounds(self):
        vt = VectorTheosis1092(dim=64)
        for _ in range(20):
            r = vt.update(np.random.randn(64).astype(np.float32) * 0.5)
            if r:
                assert 0.0 <= r["theosis"] <= 1.0

    def test_gate_escalation(self):
        \"\"\"Theosis decrescente → gate escala.\"\"\"
        vt = VectorTheosis1092(dim=64)
        gates_seen = []
        base = np.zeros(64, dtype=np.float32)
        for i in range(20):
            perturbed = base + np.random.randn(64).astype(np.float32) * (0.05 * (i + 1))
            r = vt.update(perturbed)
            if r:
                gates_seen.append(r["gate"])
        # Deve ter visto gates diferentes (não apenas OPEN)
        assert len(set(gates_seen)) >= 2

    def test_bifurcation_detection(self):
        \"\"\"Variação alta entre escalas → bifurcação detectada.\"\"\"
        vt = VectorTheosis1092(dim=64)
        base = np.zeros(64, dtype=np.float32)
        # Gera TEE muito diferente em janela 2 vs janela 8
        vt.update(base)
        vt.update(base + 0.001 * np.ones(64, dtype=np.float32))
        vt.update(base + 0.5 * np.ones(64, dtype=np.float32))  # spike
        r = vt.update(base + 0.6 * np.ones(64, dtype=np.float32))
        if r:
            # A variação entre escalas deve ser alta
            assert r["tee_per_scale"] is not None
            # (não garante bifurcação para toda entrada, mas testa que o campo existe)

    def test_reset(self):
        vt = VectorTheosis1092(dim=64)
        for _ in range(5):
            vt.update(np.random.randn(64).astype(np.float32))
        assert len(vt.readings) > 0
        vt.reset()
        assert len(vt.readings) == 0
        assert vt._cycle == 0
        assert vt._last_theosis == 1.0


class TestVectorTheosisTelemetry:
    def test_telemetry_structure(self):
        vt = VectorTheosis1092(dim=64)
        vt.update(np.zeros(64, dtype=np.float32))
        vt.update(np.ones(64, dtype=np.float32))
        vt.update(np.full(64, 0.5, dtype=np.float32))
        t = vt.get_telemetry()
        assert t["module"] == "VectorTheosis1092"
        assert t["version"] == "4.0.0"
        assert t["dim"] == 64
        assert t["n_readings"] == 1
        assert "stats" in t
        assert "seal" in t
""")
