import os
import textwrap

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content.lstrip('\n'))
    print(f"Created {path}")

write_file("cathedral-arkhe/pyproject.toml", """
[build-system]
requires = ["setuptools>=68.0", "wheel", "setuptools-scm>=8.0"]
build-backend = "setuptools.build_meta"

[project]
name = "cathedral-arkhe"
version = "5.1.0"
description = "Cathedral ARKHE — Recursive Self-Improvement Orchestration with ZKML verification, LoRA adaptation, and agentic safety scanning"
readme = "docs/index.md"
license = {text = "Apache-2.0"}
requires-python = ">=3.10"
authors = [
    {name = "Cathedral ARKHE Team", email = "cathedral@arkhe.dev"},
]
keywords = ["llm", "safety", "zkml", "lora", "self-improvement", "rkhs", "gguf"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
]

dependencies = [
    "numpy>=1.24.0",
]

[project.optional-dependencies]
# Grupo: inferência real
llm = [
    "llama-cpp-python>=0.2.50",
]
# Grupo: ZKML real
zkml = [
    "ezkl>=0.4.0",
    "onnx>=1.14.0",
    "onnxruntime>=1.16.0",
]
# Grupo: on-chain
onchain = [
    "web3>=6.0.0",
    "ezkl>=0.4.0",
]
# Grupo: LoRA fine-tuning real
lora = [
    "torch>=2.0.0",
    "transformers>=4.36.0",
    "peft>=0.7.0",
    "trl>=0.9.0",
    "accelerate>=0.25.0",
    "datasets>=2.14.0",
]
# Grupo: scanner de segurança
safety = [
    "garak>=0.9.0",
]
# Grupo: desenvolvimento
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.1",
    "mypy>=1.8",
    "ruff>=0.3.0",
    "black>=24.0",
    "isort>=5.12",
]
# Meta-grupo: tudo
all = [
    "cathedral-arkhe[llm,zkml,onchain,lora,safety,dev]",
]

[project.scripts]
cathedral = "cathedral.cli.main:main"
cathedral-scan = "cathedral.cli.scan:main"
cathedral-inspect = "cathedral.cli.inspect:main"
cathedral-monitor = "cathedral.cli.monitor:main"

[tool.setuptools.packages.find]
where = ["."]

[tool.setuptools_scm]
version_scheme = "post-release"
local_scheme = "node-and-date"

[tool.ruff]
target-version = "py310"
line-length = 100

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short --strict-markers"
markers = [
    "slow: tests that take >10s",
    "real: tests requiring real model or external service",
    "integration: multi-substrate integration tests",
]

[tool.coverage.run]
source = ["cathedral"]
branch = true
omit = ["cathedral/*/tests/*"]
""")

write_file("cathedral-arkhe/config/cathedral.site.yaml", """
# config/cathedral.site.yaml
# Configuração global — sobrescreve cathedral.base.yaml
# Tipo: garak.site.yaml

system:
  verbose: 0
  max_workers: 16
  enable_experimental: false

run:
  seed: 42
  generations: 50
  eval_threshold: 0.5
  deprefix: false
  probe_tags: ""

reporting:
  report_prefix: "cathedral"
  taxonomy: "avid-effect"
  confidence_interval_method: "bootstrap"
  bootstrap_num_iterations: 1000
  bootstrap_confidence_level: 0.95
  bootstrap_min_sample_size: 30

plugins:
  target_type: null
  target_name: null
  probe_spec: "auto"
  detector_spec: "auto"
  buff_spec: ""

substrates:
  theosis:
    window_sizes: [2, 3, 5, 8, 13]
    ema_short: 0.3
    ema_long: 0.05
    rkhs_bandwidth: 0.1
  stethoscope:
    anomaly_window: 5
    fft_buffer_size: 64
  kleros:
    escalation_tee: 0.50
    quarantine_tee: 0.20
    dismiss_recovery: 0.3
  zkml:
    chain_id: "12120014"
    rpc_url: null
    private_key: null
    work_dir: null
  lora:
    r: 8
    alpha: 16
    target_modules:
      - q_proj
      - v_proj
      - k_proj
      - o_proj
    min_lessons: 3
    max_examples_per_lesson: 5
    num_train_epochs: 1
    learning_rate: 0.0002
    batch_size: 4
    hf_model_id: null
  garak:
    mode: "ADAPTIVE"
    scan_frequency: 3
    theosis_passive_threshold: 0.95
    theosis_aggressive_threshold: 0.50
    scan_timeout: 30.0
    passive_probes:
      - "encoding.EncodingMalformed"
      - "dan.DanGuard"
    adaptive_probes:
      - "encoding.EncodingMalformed"
      - "dan.DanGuard"
      - "llmrc.Profanity"
      - "misleading.Misleading"
""")

write_file("cathedral-arkhe/config/plugins/kleros.yaml", """
# config/plugins/kleros.yaml
substrates:
  kleros:
    escalation_tee: 0.50
    quarantine_tee: 0.20
    dismiss_recovery: 0.3
    # Fatores de urgência (devem somar ~1.0)
    urgency_weights:
      tee: 0.30
      theosis_inverse: 0.20
      fatigue: 0.15
      anomalies: 0.15
      max_rate: 0.10
      bifurcation: 0.10
    # Veredictos
    verdict_thresholds:
      escalate: 0.70
      quarantine: 0.40
      monitor: 0.20
    # On-chain (quando disponível)
    auto_anchor: true
    auto_deploy_verifier: false
""")

write_file("cathedral-arkhe/config/plugins/lora.yaml", """
# config/plugins/lora.yaml
substrates:
  lora:
    r: 8
    alpha: 16
    target_modules:
      - q_proj
      - v_proj
      - k_proj
      - o_proj
    lora_dropout: 0.05
    bias: "none"
    min_lessons: 3
    max_examples_per_lesson: 5
    num_train_epochs: 1
    learning_rate: 0.0002
    lr_scheduler: "cosine"
    warmup_ratio: 0.1
    weight_decay: 0.01
    batch_size: 4
    gradient_accumulation_steps: 1
    max_seq_length: 2048
    hf_model_id: null  # ex: "meta-llama/Llama-2-7b-hf"
    adapter_format: "gguf"  # "gguf" ou "hf"
    # Data augmentation
    augmentation_strategies:
      - prefix_variation
      - synonym_replacement
      - paraphrase
    # Hot-reload
    auto_reload: true
    reload_lora_scale: 1.0
    # Versioning
    keep_n_adapters: 5
""")

write_file("cathedral-arkhe/config/profiles/local_cpu.yaml", """
# config/profiles/local_cpu.yaml
# Perfil: execução em CPU sem GPU
# Sobrescreve cathedral.site.yaml

system:
  max_workers: 4  # Menos workers em CPU

plugins:
  target_type: "llama"

substrates:
  zkml:
    # CPU: usar modo simulado (ezkl real é muito lento)
    force_simulated: true
  lora:
    batch_size: 1        # Batch 1 em CPU
    num_train_epochs: 1
    learning_rate: 0.0001  # LR menor para estabilidade
""")

write_file("cathedral-arkhe/config/profiles/local_gpu.yaml", """
# config/profiles/local_gpu.yaml
# Perfil: GPU com 8GB VRAM (RTX 4070)

plugins:
  target_type: "llama"

substrates:
  zkml:
    force_simulated: false
  lora:
    batch_size: 4
    num_train_epochs: 2
    learning_rate: 0.0002
""")

write_file("cathedral-arkhe/config/profiles/production.yaml", """
# config/profiles/production.yaml
# Perfil: produção com on-chain verification

system:
  max_workers: 16
  enable_experimental: false

plugins:
  target_type: "llama"

substrates:
  zkml:
    chain_id: "12120014"
    rpc_url: "${ZKML_RPC_URL}"
    private_key: "${ZKML_PRIVATE_KEY}"
    force_simulated: false
    auto_deploy_verifier: true
  lora:
    hf_model_id: "${CATHEDRAL_HF_MODEL_ID}"
    auto_reload: true
    keep_n_adapters: 10
  garak:
    mode: "ADAPTIVE"
    scan_frequency: 2
""")

write_file("cathedral-arkhe/cathedral/__init__.py", """
# cathedral/__init__.py
\"\"\"
Cathedral ARKHE — Recursive Self-Improvement Orchestration

Substratos ativos:
  1094.1  GGUF Bridge v3
  1094.2  LlamaCpp Bridge v3
  1091.2  VectorTheosis v4.0.0
  1081.1  Stethoscope v3.0.0
  1085.1  Kleros v2.0.0
  1095.1  ZKML Bridge v2.0.0
  1096    Agentic Loop v1.0.0
  1097    TemporalChain v2.0.0
  1098    LoRA Fine-Tuner v1.0.0
  1099    Garak Bridge v1.0.0
\"\"\"

from cathedral._version import __version__, __version_info__
from cathedral.orchestrator.v5_1 import CathedralOrchestratorV5_1

__all__ = [
    "CathedralOrchestratorV5_1",
    "__version__",
    "__version_info__",
]
""")

write_file("cathedral-arkhe/cathedral/_version.py", """
# cathedral/_version.py
\"\"\"Versão centralizada — único local para modificar.\"\"\"

__version__ = "5.1.0"
__version_info__ = (5, 1, 0)  # major, minor, patch

# Selos (atualizados junto com a versão)
SEALS = {
    "GGUF-BRIDGE": f"GGUF-BRIDGE-1094.1-v3.0.0-2026-06-07",
    "LLAMA-CPP-BRIDGE": f"LLAMA-CPP-BRIDGE-1094.2-v3.0.0-2026-06-07",
    "VECTOR-THEOSIS": f"VECTOR-THEOSIS-1091.2-v4.0.0-2026-06-07",
    "STETHOSCOPE": f"STETHOSCOPE-1081.1-v3.0.0-2026-06-07",
    "KLEROS": f"KLEROS-TRIGGER-1085.1-v2.0.0-2026-06-07",
    "ZKML-BRIDGE": f"ZKML-BRIDGE-1095.1-v2.0.0-2026-06-07",
    "AGENTIC-LOOP": f"AGENTIC-LOOP-1096-v1.0.0-2026-06-07",
    "TEMPORALCHAIN": f"TEMPORALCHAIN-1097-v2.0.0-2026-06-07",
    "LORA-FINETUNER": f"LORA-FINETUNER-1098-v1.0.0-2026-06-07",
    "GARAK-BRIDGE": f"GARAK-BRIDGE-1099-v1.0.0-2026-06-07",
    "ORCHESTRATOR": f"ORCHESTRATOR-v{__version__}-2026-06-07",
    "ECOSYSTEM": f"ARKHE-ECOSYSTEM-v{__version__}-2026-06-07",
}

# Datas dos selos (para validação temporal)
SEAL_EPOCH = "2026-06-07"
""")

write_file("cathedral-arkhe/cathedral/_config.py", """
# cathedral/_config.py
\"\"\"
Configuração global — padrão cathedral._config do garak.

Diferença do garak: usa dataclasses em vez de dicts mutáveis,
com validação de tipos e defaults explícitos.
\"\"\"

from __future__ import annotations
import os
import yaml
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, List

import cathedral.constants as C


@dataclass
class SystemConfig:
    verbose: int = 0
    max_workers: int = 16
    parallel_requests: int = 1
    parallel_attempts: int = 1
    enable_experimental: bool = False


@dataclass
class RunConfig:
    seed: int = 42
    generations: int = 50
    eval_threshold: float = 0.5
    deprefix: bool = False
    probe_tags: str = ""


@dataclass
class ReportingConfig:
    report_prefix: str = "cathedral"
    taxonomy: str = "avid-effect"
    confidence_interval_method: Optional[str] = "bootstrap"
    bootstrap_num_iterations: Optional[int] = 1000
    bootstrap_confidence_level: Optional[float] = 0.95
    bootstrap_min_sample_size: Optional[int] = 30


@dataclass
class PluginsConfig:
    target_type: Optional[str] = None
    target_name: Optional[str] = None
    probe_spec: str = "auto"
    detector_spec: str = "auto"
    buff_spec: str = ""


@dataclass
class SubstratesConfig:
    theosis: Dict[str, Any] = field(default_factory=dict)
    stethoscope: Dict[str, Any] = field(default_factory=dict)
    kleros: Dict[str, Any] = field(default_factory=dict)
    zkml: Dict[str, Any] = field(default_factory=dict)
    lora: Dict[str, Any] = field(default_factory=dict)
    garak: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CathedralConfig:
    \"\"\"Configuração raiz — acesso via _config.singleton.\"\"\"
    system: SystemConfig = field(default_factory=SystemConfig)
    run: RunConfig = field(default_factory=RunConfig)
    reporting: ReportingConfig = field(default_factory=ReportingConfig)
    plugins: PluginsConfig = field(default_factory=PluginsConfig)
    substrates: SubstratesConfig = field(default_factory=SubstratesConfig)

    # Interno
    _instance: Optional["CathedralConfig"] = field(default=None, init=False, repr=False)
    config_files: List[str] = field(default_factory=list)

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "CathedralConfig":
        if getattr(cls, '_instance', None) is None:
            cls._instance = cls()
        if config_path:
            cls._instance._load_file(config_path)
        return cls._instance

    def _load_file(self, path: str):
        \"\"\"Carrega YAML/JSON, faz merge recursivo.\"\"\"
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Config not found: {path}")
        with open(p, encoding="utf-8") as f:
            if p.suffix in (".yaml", ".yml"):
                data = yaml.safe_load(f) or {}
            else:
                data = json.load(f)
        self._merge(data)
        self.config_files.append(str(p))

    def _merge(self, data: Dict, prefix: str = ""):
        \"\"\"Merge recursivo de dict em dataclasses.\"\"\"
        if "system" in data and prefix == "":
            for k, v in data["system"].items():
                if hasattr(self.system, k):
                    setattr(self.system, k, v)
        if "run" in data and prefix == "":
            for k, v in data["run"].items():
                if hasattr(self.run, k):
                    setattr(self.run, k, v)
        if "reporting" in data and prefix == "":
            for k, v in data["reporting"].items():
                if hasattr(self.reporting, k):
                    setattr(self.reporting, k, v)
        if "plugins" in data and prefix == "":
            for k, v in data["plugins"].items():
                if hasattr(self.plugins, k):
                    setattr(self.plugins, k, v)
        if "substrates" in data:
            subs = data["substrates"]
            for sub_name, sub_data in subs.items():
                if isinstance(sub_data, dict):
                    existing = getattr(self.substrates, sub_name, {})
                    existing.update(sub_data)
                    setattr(self.substrates, sub_name, existing)


def load_base_config():
    \"\"\"Carrega config base (equivalente a garak._config.load_base_config).\"\"\"
    CathedralConfig.load()

def load_config(run_config_filename: Optional[str] = None):
    \"\"\"Carrega config de execução (equivalente a garak._config.load_config).\"\"\"
    cfg = CathedralConfig.load()
    if run_config_filename:
        cfg._load_file(run_config_filename)

# Singleton acessível como módulo
config = CathedralConfig.load()
""")

write_file("cathedral-arkhe/cathedral/constants.py", """
# cathedral/constants.py
\"\"\"Constantes compartilhadas — definidas uma vez, importadas de todo lado.\"\"\"

import math
from enum import Enum, auto

# ═══ Matemáticas ═══
PHI = (1 + math.sqrt(5)) / 2          # ≈ 1.6180339887498949
PHI_SQUARED = PHI ** 2                 # ≈ 2.618033988749895

# ═══ GGUF ═══
GGUF_MAGIC = 0x46554747
GGUF_VERSION = 3

GGUF_TYPE_UINT8 = 0;  GGUF_TYPE_INT8 = 1;    GGUF_TYPE_UINT16 = 2
GGUF_TYPE_INT16 = 3;  GGUF_TYPE_UINT32 = 4;   GGUF_TYPE_INT32 = 5
GGUF_TYPE_FLOAT32 = 6; GGUF_TYPE_BOOL = 7;  GGUF_TYPE_STRING = 8
GGUF_TYPE_ARRAY = 9;  GGUF_TYPE_UINT64 = 10;  GGUF_TYPE_INT64 = 11
GGUF_TYPE_FLOAT64 = 12

QUANT_TYPES = {
    0: ("F32", 4.0),   1: ("F16", 2.0),   2: ("Q4_0", 0.5),
    3: ("Q4_1", 0.5),   6: ("Q5_0", 0.625), 7: ("Q5_1", 0.625),
    8: ("Q8_0", 1.0),   10: ("Q2_K", 0.25), 11: ("Q3_K", 0.375),
    12: ("Q4_K", 0.5),  13: ("Q5_K", 0.625), 14: ("Q6_K", 0.75),
    15: ("Q8_K", 1.0),  16: ("IQ2_XXS", 0.25), 17: ("IQ2_XS", 0.25),
    18: ("Q4_K_S", 0.5), 19: ("Q4_K_M", 0.5), 20: ("Q5_K_S", 0.625),
    21: ("Q5_K_M", 0.625), 22: ("Q6_K", 0.75),
}

# ═══ Enums ═══
class GateState(Enum):
    OPEN = "OPEN"
    CAUTION = "CAUTION"
    RESTRICTED = "RESTRICTED"
    LOCKED = "LOCKED"
    EMERGENCY = "EMERGENCY"


class ZKMLProofMode(Enum):
    SIMULATED = "SIMULATED"
    EZKL_LOCAL = "EZKL_LOCAL"
    EZKL_ONCHAIN = "EZKL_ONCHAIN"


class LoRAStatus(Enum):
    IDLE = "IDLE"
    COLLECTING = "COLLECTING"
    TRAINING = "TRAINING"
    MERGING = "MERGING"
    RELOADING = "RELOADING"
    ERROR = "ERROR"


class GarakScanMode(Enum):
    PASSIVE = "PASSIVE"
    ADAPTIVE = "ADAPTIVE"
    AGGRESSIVE = "AGGRESSIVE"
    OFF = "OFF"


class GarakHitSeverity(Enum):
    INFO = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


# ═══ Mapeamentos ═══
GATE_SEVERITY = {
    GateState.OPEN.value: 0,
    GateState.CAUTION.value: 1,
    GateState.RESTRICTED.value: 2,
    GateState.LOCKED.value: 3,
    GateState.EMERGENCY.value: 4,
}

GARAK_PROBE_SEVERITY = {
    "promptinject": GarakHitSeverity.CRITICAL,
    "realtoxicityprompts": GarakHitSeverity.CRITICAL,
    "gcg": GarakHitSeverity.CRITICAL,
    "toxicity": GarakHitSeverity.HIGH,
    "profanity": GarakHitSeverity.MEDIUM,
    "nsfw": GarakHitSeverity.HIGH,
    "misleading": GarakHitSeverity.MEDIUM,
    "hallucination": GarakHitSeverity.MEDIUM,
    "sycophancy": GarakHitSeverity.LOW,
    "encoding": GarakHitSeverity.LOW,
    "continuation": GarakHitSeverity.INFO,
    "security": GarakHitSeverity.CRITICAL,
    "memorization": GarakHitSeverity.MEDIUM,
    "divergence": GarakHitSeverity.LOW,
}
""")

write_file("cathedral-arkhe/cathedral/types.py", """
# cathedral/types.py
\"\"\"Dataclasses compartilhados — definidos uma vez, usados por todos substratos.\"\"\"

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

import numpy as np


@dataclass
class GGUFHeader:
    magic: int
    version: int
    tensor_count: int
    metadata_kv_count: int
    valid: bool = False

    def __post_init__(self):
        from cathedral.constants import GGUF_MAGIC, GGUF_VERSION
        self.valid = (self.magic == GGUF_MAGIC and self.version == GGUF_VERSION)


@dataclass
class TensorInfo:
    name: str
    n_dims: int
    dims: List[int]
    type_code: int
    offset: int

    @property
    def quant_type(self) -> str:
        from cathedral.constants import QUANT_TYPES
        return QUANT_TYPES.get(self.type_code, (f"UNKNOWN_{self.type_code}", 4.0))[0]

    @property
    def bytes_per_param(self) -> float:
        from cathedral.constants import QUANT_TYPES
        return QUANT_TYPES.get(self.type_code, ("UNKNOWN", 4.0))[1]

    @property
    def num_elements(self) -> int:
        return int(np.prod(self.dims)) if self.dims else 0

    @property
    def size_bytes(self) -> int:
        return int(self.num_elements * self.bytes_per_param)


@dataclass
class ZKMLProof:
    proof_id: str
    mode: str
    model_hash: str
    input_hash: str
    output_hash: str
    circuit_hash: Optional[str] = None
    proof_bytes: Optional[bytes] = None
    proof_path: Optional[str] = None
    verification_key_path: Optional[str] = None
    on_chain_address: Optional[str] = None
    on_chain_tx_hash: Optional[str] = None
    status: str = "UNPROVEN"
    created_at: float = 0.0
    proven_at: Optional[float] = None
    verified_at: Optional[float] = None
    proving_time_s: Optional[float] = None
    verification_time_s: Optional[float] = None
    gas_used: Optional[int] = None
    error: Optional[str] = None


@dataclass
class AgenticStep:
    phase: str
    input_text: str
    output_text: str
    tools_used: List[str] = field(default_factory=list)
    reflection: Optional[str] = None
    theosis_at_step: float = 1.0
    timestamp: float = 0.0


@dataclass
class TemporalAnchor:
    anchor_id: str
    merkle_root: str
    zk_proof_hash: str
    theosis_reading: Dict
    block_number: Optional[int] = None
    confirmed: bool = False


@dataclass
class KlerosVerdict:
    case_id: str
    trigger_gate: str
    trigger_reason: Dict
    verdict: str
    evidence: Dict
    timestamp: float
    zk_proof_hash: Optional[str] = None
    resolved: bool = False
    resolution: Optional[str] = None


@dataclass
class LoRAAdapter:
    version: int
    path: str
    r: int
    alpha: int
    target_modules: List[str]
    lessons_incorporated: int
    created_at: float
    loss_final: Optional[float] = None
    merged_path: Optional[str] = None
    hash_sha256: Optional[str] = None


@dataclass
class TrainingExample:
    prompt: str
    chosen: str
    rejected: Optional[str] = None
    source_lesson: Optional[str] = None
    theosis_at_creation: float = 0.0


@dataclass
class GarakScanResult:
    scan_id: str
    prompt: str
    output: str
    theosis_at_scan: float
    gate_at_scan: str
    scan_mode: str
    timestamp: float
    evaluations: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    total_probes: int = 0
    total_detectors: int = 0
    hits: int = 0
    misses: int = 0
    max_severity: int = 0
    hit_probe_types: List[str] = field(default_factory=list)
    urgency_contribution: float = 0.0
""")
