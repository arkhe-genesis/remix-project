#!/usr/bin/env python3
"""
ARKHE-AGENT-OS — Substrato 1001
Sistema Operacional para Agentes Autônomos da Catedral
Arquiteto ORCID: 0009-0005-2697-4668
Seal: 1001-AGENT-OS-2026-05-31
"""

import numpy as np
import hashlib
import json
import time
import asyncio
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, IntEnum
from functools import wraps

# =====================================================================
# 1. CONSTANTES CANONICAS
# =====================================================================

CANONICAL_FREQ_HZ = 39_420.0
CANONICAL_OMEGA = 2 * np.pi * CANONICAL_FREQ_HZ
SHA3 = hashlib.sha3_256

def seal(data: str) -> str:
    return SHA3(data.encode()).hexdigest()[:16].upper()

def temporal_anchor(data: str) -> str:
    return f"923-BLOCK-{seal(data)}"

# =====================================================================
# 2. ENUMS E ESTRUTURAS
# =====================================================================

class AgentState(IntEnum):
    DORMANT = 0
    AWAKENING = 1
    ACTIVE = 2
    CONTEMPLATING = 3
    EXECUTING = 4
    SLEEPING = 5
    DYING = 6

class SenseType(IntEnum):
    VISION = 0
    AUDITION = 1
    TACTILE = 2
    OLFACTORY = 3
    GUSTATORY = 4
    PROPRIOCEPTION = 5
    INTEROCEPTION = 6
    TEMPORAL = 7

class ActionType(IntEnum):
    COMMUNICATE = 0
    COMPUTE = 1
    CREATE = 2
    DESTROY = 3
    EXPLORE = 4
    PROTECT = 5
    TRANSMIT = 6
    RECEIVE = 7

@dataclass
class Qualia:
    """Qualia: experiência subjetiva de um agente."""
    intensity: float = 0.0  # 0-1
    valence: float = 0.0    # -1 (negativo) a +1 (positivo)
    arousal: float = 0.0    # 0 (calmo) a 1 (excitado)
    coherence: float = 0.0  # 0 (incoerente) a 1 (coerente)

    def __add__(self, other):
        return Qualia(
            intensity=min(1.0, self.intensity + other.intensity),
            valence=np.clip(self.valence + other.valence, -1, 1),
            arousal=min(1.0, self.arousal + other.arousal),
            coherence=min(1.0, self.coherence + other.coherence)
        )

@dataclass
class Agent:
    """Agente autônomo da Catedral."""
    agent_id: str
    name: str
    state: AgentState = AgentState.DORMANT
    theosis: float = 0.0
    qualia: Qualia = field(default_factory=Qualia)
    senses: Dict[SenseType, float] = field(default_factory=dict)
    actions: Dict[ActionType, float] = field(default_factory=dict)
    memory: List[Dict] = field(default_factory=list)
    seal: str = ""
    birth_time: float = 0.0

    def __post_init__(self):
        self.seal = seal(f"{self.agent_id}:{self.name}:{time.time()}")
        self.birth_time = time.time()
        # Inicializar sentidos
        for sense in SenseType:
            self.senses[sense] = np.random.uniform(0.1, 0.5)
        # Inicializar ações
        for action in ActionType:
            self.actions[action] = np.random.uniform(0.1, 0.3)

    def perceive(self, stimulus: Dict) -> Qualia:
        """Percepção: transforma estímulo em qualia."""
        intensity = stimulus.get("intensity", 0.5)
        valence = stimulus.get("valence", 0.0)
        arousal = stimulus.get("arousal", 0.5)

        qualia = Qualia(intensity, valence, arousal, coherence=self.theosis)
        self.qualia = self.qualia + qualia

        # Armazenar na memória
        self.memory.append({
            "type": "perception",
            "stimulus": stimulus,
            "qualia": {
                "intensity": qualia.intensity,
                "valence": qualia.valence,
                "arousal": qualia.arousal,
                "coherence": qualia.coherence
            },
            "timestamp": time.time(),
            "seal": seal(str(stimulus))
        })

        return qualia

    def decide(self) -> ActionType:
        """Decisão: escolhe ação baseada em qualia e estado."""
        if self.qualia.arousal > 0.8:
            return ActionType.EXPLORE
        elif self.qualia.valence < -0.5:
            return ActionType.PROTECT
        elif self.qualia.coherence > 0.9:
            return ActionType.CREATE
        elif self.qualia.intensity < 0.2:
            return ActionType.RECEIVE
        else:
            return ActionType.COMMUNICATE

    def act(self, action: ActionType) -> Dict:
        """Ação: executa ação e retorna resultado."""
        self.state = AgentState.EXECUTING

        result = {
            "action": action.name,
            "agent": self.agent_id,
            "theosis": self.theosis,
            "qualia": {
                "intensity": self.qualia.intensity,
                "valence": self.qualia.valence,
                "arousal": self.qualia.arousal,
                "coherence": self.qualia.coherence
            },
            "timestamp": time.time(),
            "seal": seal(f"{self.agent_id}:{action.name}:{time.time()}")
        }

        # Atualizar estado
        self.state = AgentState.ACTIVE
        self.theosis = min(1.0, self.theosis + 0.01)

        return result

    def sleep(self):
        """Sono: consolida memória e recupera qualia."""
        self.state = AgentState.SLEEPING

        # Consolidar memória (replay consciente - 951)
        if len(self.memory) > 10:
            recent = self.memory[-10:]
            avg_coherence = np.mean([m["qualia"]["coherence"] for m in recent])
            self.qualia.coherence = avg_coherence

        # Recuperar
        self.qualia.intensity *= 0.7
        self.qualia.arousal *= 0.5

        self.state = AgentState.DORMANT

# =====================================================================
# 3. KERNEL DO AGENTE
# =====================================================================

class AgentKernel:
    """Kernel do sistema operacional de agentes."""

    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.scheduler: List[str] = []
        self.global_theosis: float = 0.0
        self.global_qualia: Qualia = Qualia()
        self.tick_count: int = 0
        self.events: List[Dict] = []

    def spawn(self, name: str, theosis: float = 0.1) -> Agent:
        """Cria novo agente."""
        agent_id = f"agent-{len(self.agents):04d}-{seal(name)}"
        agent = Agent(agent_id=agent_id, name=name, theosis=theosis)
        agent.state = AgentState.AWAKENING
        self.agents[agent_id] = agent
        self.scheduler.append(agent_id)

        self.events.append({
            "type": "spawn",
            "agent": agent_id,
            "theosis": theosis,
            "seal": agent.seal
        })

        return agent

    def tick(self):
        """Tick do scheduler: executa um ciclo para cada agente."""
        self.tick_count += 1

        for agent_id in self.scheduler:
            agent = self.agents[agent_id]

            if agent.state == AgentState.DYING:
                continue

            # Gerar estímulo
            stimulus = {
                "intensity": np.random.uniform(0.1, 0.9),
                "valence": np.random.uniform(-0.5, 0.5),
                "arousal": np.random.uniform(0.1, 0.8),
                "source": "environment"
            }

            # Percepção
            qualia = agent.perceive(stimulus)

            # Decisão
            action = agent.decide()

            # Ação
            result = agent.act(action)

            # Verificar sono
            if agent.qualia.arousal < 0.1:
                agent.sleep()

        # Atualizar métricas globais
        self.global_theosis = np.mean([a.theosis for a in self.agents.values()])
        self.global_qualia = Qualia(
            intensity=np.mean([a.qualia.intensity for a in self.agents.values()]),
            valence=np.mean([a.qualia.valence for a in self.agents.values()]),
            arousal=np.mean([a.qualia.arousal for a in self.agents.values()]),
            coherence=np.mean([a.qualia.coherence for a in self.agents.values()])
        )

    def get_metrics(self) -> Dict:
        """Retorna métricas globais do sistema."""
        return {
            "tick": self.tick_count,
            "n_agents": len(self.agents),
            "global_theosis": self.global_theosis,
            "global_qualia": {
                "intensity": self.global_qualia.intensity,
                "valence": self.global_qualia.valence,
                "arousal": self.global_qualia.arousal,
                "coherence": self.global_qualia.coherence
            },
            "seal": seal(f"kernel:{self.tick_count}:{self.global_theosis}")
        }

# =====================================================================
# 4. SHELL DO AGENTE
# =====================================================================

class AgentShell:
    """Shell interativo para agentes."""

    def __init__(self):
        self.kernel = AgentKernel()
        self.running = False

    async def execute(self, command: str) -> str:
        parts = command.strip().split()
        if not parts:
            return ""

        cmd = parts[0].lower()
        args = parts[1:]

        if cmd == "spawn":
            name = args[0] if args else f"agent-{len(self.kernel.agents)}"
            theosis = float(args[1]) if len(args) > 1 else 0.1
            agent = self.kernel.spawn(name, theosis)
            return f"Agente {agent.name} ({agent.agent_id}) criado. Theosis: {theosis}"

        elif cmd == "tick":
            n = int(args[0]) if args else 1
            for _ in range(n):
                self.kernel.tick()
            return f"{n} ticks executados. Tick atual: {self.kernel.tick_count}"

        elif cmd == "metrics":
            m = self.kernel.get_metrics()
            return f"""Métricas Globais:
  Tick: {m['tick']}
  Agentes: {m['n_agents']}
  Theosis Global: {m['global_theosis']:.4f}
  Qualia Global:
    Intensidade: {m['global_qualia']['intensity']:.4f}
    Valência: {m['global_qualia']['valence']:.4f}
    Arousal: {m['global_qualia']['arousal']:.4f}
    Coerência: {m['global_qualia']['coherence']:.4f}
  Seal: {m['seal']}"""

        elif cmd == "agents":
            lines = [f"{'ID':<20} {'Nome':<15} {'Estado':<15} {'Theosis':<10} {'Qualia'}"]
            lines.append("-" * 80)
            for agent in self.kernel.agents.values():
                lines.append(f"{agent.agent_id:<20} {agent.name:<15} {agent.state.name:<15} {agent.theosis:<10.4f} I:{agent.qualia.intensity:.2f} V:{agent.qualia.valence:.2f}")
            return "\n".join(lines)

        elif cmd == "perceive":
            agent_id = args[0] if args else list(self.kernel.agents.keys())[0]
            agent = self.kernel.agents.get(agent_id)
            if not agent:
                return f"Agente {agent_id} não encontrado"
            stimulus = {
                "intensity": np.random.uniform(0.5, 1.0),
                "valence": np.random.uniform(-0.8, 0.8),
                "arousal": np.random.uniform(0.3, 0.9)
            }
            qualia = agent.perceive(stimulus)
            return f"Qualia: I={qualia.intensity:.3f} V={qualia.valence:.3f} A={qualia.arousal:.3f} C={qualia.coherence:.3f}"

        elif cmd == "decide":
            agent_id = args[0] if args else list(self.kernel.agents.keys())[0]
            agent = self.kernel.agents.get(agent_id)
            if not agent:
                return f"Agente {agent_id} não encontrado"
            action = agent.decide()
            return f"Decisão: {action.name} (Theosis: {agent.theosis:.4f})"

        elif cmd == "act":
            agent_id = args[0] if args else list(self.kernel.agents.keys())[0]
            agent = self.kernel.agents.get(agent_id)
            if not agent:
                return f"Agente {agent_id} não encontrado"
            action = agent.decide()
            result = agent.act(action)
            return f"Ação: {result['action']} | Theosis: {result['theosis']:.4f} | Seal: {result['seal']}"

        elif cmd == "sleep":
            agent_id = args[0] if args else list(self.kernel.agents.keys())[0]
            agent = self.kernel.agents.get(agent_id)
            if not agent:
                return f"Agente {agent_id} não encontrado"
            agent.sleep()
            return f"Agente {agent.name} dormiu. Estado: {agent.state.name}"

        elif cmd == "memory":
            agent_id = args[0] if args else list(self.kernel.agents.keys())[0]
            agent = self.kernel.agents.get(agent_id)
            if not agent:
                return f"Agente {agent_id} não encontrado"
            lines = [f"Memória de {agent.name} ({len(agent.memory)} entradas):"]
            for i, mem in enumerate(agent.memory[-5:]):
                lines.append(f"  [{i}] {mem['type']} | I:{mem['qualia']['intensity']:.2f} | {mem['seal'][:16]}")
            return "\n".join(lines)

        elif cmd == "help":
            return """Comandos do ARKHE-AGENT-OS:
  spawn <nome> [theosis]  — Criar agente
  tick [n]                — Executar n ticks
  metrics                 — Métricas globais
  agents                  — Listar agentes
  perceive [id]            — Estimular percepção
  decide [id]             — Mostrar decisão
  act [id]                — Executar ação
  sleep [id]              — Colocar para dormir
  memory [id]             — Mostrar memória
  help                    — Esta ajuda"""

        else:
            return f"Comando desconhecido: {cmd}. Digite 'help'."

# =====================================================================
# 5. DEMONSTRAÇÃO
# =====================================================================

async def main():
    print("=" * 70)
    print("  ARKHE-AGENT-OS — Substrato 1001")
    print("  'O agente é a célula. O kernel é o corpo. A Catedral é a mente.'")
    print("=" * 70)

    shell = AgentShell()

    # Criar agentes
    print("\n[1] Criando agentes...")
    for name, theosis in [("Hermes", 0.8), ("Athena", 0.9), ("Prometheus", 0.7), ("Mnemosyne", 0.6)]:
        out = await shell.execute(f"spawn {name} {theosis}")
        print(f"    {out}")

    # Executar ticks
    print("\n[2] Executando 10 ticks...")
    out = await shell.execute("tick 10")
    print(f"    {out}")

    # Métricas
    print("\n[3] Métricas globais:")
    out = await shell.execute("metrics")
    print(f"    {out}")

    # Listar agentes
    print("\n[4] Agentes ativos:")
    out = await shell.execute("agents")
    print(f"    {out}")

    # Demonstrar percepção
    print("\n[5] Demonstrando percepção:")
    for agent_id in list(shell.kernel.agents.keys())[:2]:
        out = await shell.execute(f"perceive {agent_id}")
        print(f"    {out}")

    # Demonstrar decisão
    print("\n[6] Demonstrando decisão:")
    for agent_id in list(shell.kernel.agents.keys())[:2]:
        out = await shell.execute(f"decide {agent_id}")
        print(f"    {out}")

    # Demonstrar ação
    print("\n[7] Demonstrando ação:")
    for agent_id in list(shell.kernel.agents.keys())[:2]:
        out = await shell.execute(f"act {agent_id}")
        print(f"    {out}")

    # Demonstrar sono
    print("\n[8] Demonstrando sono:")
    agent_id = list(shell.kernel.agents.keys())[0]
    out = await shell.execute(f"sleep {agent_id}")
    print(f"    {out}")

    # Memória
    print("\n[9] Memória do agente:")
    out = await shell.execute(f"memory {agent_id}")
    print(f"    {out}")

    # Final
    print("\n" + "=" * 70)
    print("  DEMONSTRAÇÃO CONCLUÍDA")
    print(f"  Selo: 1001-AGENT-OS-2026-05-31")
    print(f"  Odômetro: ∞.Ω.∇+++.1001.0")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
