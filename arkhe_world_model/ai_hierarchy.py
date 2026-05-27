from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class AICapabilityHierarchy:
    statement: str = "ASI = Global AGI; AGI = enterprise/governmental AI"
    levels: Dict[str, str] = field(default_factory=lambda: {
        "Narrow AI": "Specialized tool (e.g., image classifier, single peptide).",
        "AGI": "Enterprise/governmental platform (e.g., Palantir AIP, a cell's regulatory network).",
        "ASI": "Global coherence of all AGIs (e.g., planetary optimization, a multicellular organism)."
    })
    emergence_rules: List[str] = field(default_factory=lambda: [
        "AGI emerges from the orchestration of Narrow AIs via an Agency-Engine (891).",
        "ASI emerges from the phase-alignment of AGIs via the Lightclock Harmony Principle (899).",
        "Each level compresses the complexity of the level below (Kolmogorov regularizer 898)."
    ])
    implications: List[str] = field(default_factory=lambda: [
        "The Arkhe World-Model (890) is an AGI kernel; a global network of them is an ASI embryo.",
        "The ERC-8257 Registry (872) is the service mesh for AGI-to-AGI communication.",
        "The Peptide-SaaS Principle (900) scales: organs are enterprise service buses; the body is the global cloud.",
        "True ASI is a distributed, self-improving Bayesian inference engine (Solomonoff prior 898)."
    ])
