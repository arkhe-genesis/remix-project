#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════════════╗
║ CATHEDRAL ARKHE v14.0.0 — SUBSTRATO 1500 (Sovereign Cognitive Loop - Standalone)  ║
║                                                                                   ║
║ Módulos Contidos:                                                                ║
║ 1. PrometheusRegistry (Gauges, Counters, Histograms)                             ║
║ 2. GgufInferenceEngine (Thread-Safe Queue, Semantic Cache, Sliding Window)       ║
║ 3. InferenceRouter (Custo x Complexidade x Disponibilidade)                     ║
║ 4. CathedralOrchestratorV14_0_0 (Lifecycle, Graceful Shutdown, Metrics)          ║
║ 5. Servidor HTTP (Prometheus /metrics)                                           ║
║                                                                                   ║
║ Selo: CATHEDRAL-ARKHE-v14.0.0-SUBSTRATO1500-2026-06-14                           ║
║ Arquiteto: ORCID 0009-0005-2697-4668                                             ║
╚═════════════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
import asyncio
import hashlib
import logging
import math
import signal
import time
from collections import deque
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Tenta importar dependências opcionais de forma silenciosa
try:
    from llama_cpp import Llama
    HAS_LLAMA_CPP = True
except ImportError:
    HAS_LLAMA_CPP = False

try:
    from huggingface_hub import hf_hub_download
    HAS_HF_HUB = True
except ImportError:
    HAS_HF_HUB = False

try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

logger = logging.getLogger("cathedral.v14")

# =============================================================================
# 1. PROMETHEUS REGISTRY
# =============================================================================

class PrometheusRegistry:
    def __init__(self):
        self._gauges: Dict[str, float] = {}
        self._counters: Dict[str, float] = {}
        self._histograms: Dict[str, Dict] = {}

    def _key(self, name: str, labels: Optional[Dict[str, str]] = None) -> str:
        if not labels: return name
        lbl_str = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
        return f"{name}{{{lbl_str}}}"

    def gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        self._gauges[self._key(name, labels)] = value

    def counter_inc(self, name: str, inc: float = 1.0, labels: Optional[Dict[str, str]] = None):
        k = self._key(name, labels)
        self._counters[k] = self._counters.get(k, 0.0) + inc

    def histogram_observe(self, name: str, value: float, buckets: Optional[list] = None, labels: Optional[Dict[str, str]] = None):
        k = self._key(name, labels)
        if k not in self._histograms:
            b = sorted(buckets or [0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0])
            self._histograms[k] = {"buckets": b, "counts": [0] * (len(b) + 1), "sum": 0.0, "count": 0}
        h = self._histograms[k]
        h["sum"] += value; h["count"] += 1
        for i, b in enumerate(h["buckets"]):
            if value <= b: h["counts"][i] += 1
        h["counts"][-1] += 1

    def render(self) -> str:
        lines = []
        for k, v in sorted(self._gauges.items()): lines.append(f"# TYPE {k.split('{')[0]} gauge\n{k} {v}")
        for k, v in sorted(self._counters.items()): lines.append(f"# TYPE {k.split('{')[0]} counter\n{k} {v}")
        for k, h in sorted(self._histograms.items()):
            base = k.split('{')[0]
            lines.append(f"# TYPE {base} histogram")
            for i, b in enumerate(h["buckets"]): lines.append(f'{k}_bucket{{le="{b}"}} {h["counts"][i]}')
            lines.append(f'{k}_bucket{{le="+Inf"}} {h["counts"][-1]}')
            lines.append(f'{k}_sum {h["sum"]}\n{k}_count {h["count"]}')
        return "\n".join(lines) + "\n"

# =============================================================================
# 2. GGUF INFERENCE ENGINE (Core Soberano)
# =============================================================================

@dataclass
class _InferenceRequest:
    future: asyncio.Future
    prompt: str
    kwargs: Dict[str, Any]

class GgufInferenceEngine:
    def __init__(self, model_id: str = "unsloth/Qwen3-0.6B-GGUF",
                 quant: str = "Q4_K_M", cache_dir: str = "~/.cathedral/gguf",
                 n_ctx: int = 4096, n_threads: int = 8, n_gpu_layers: int = -1,
                 temperature: float = 0.7, max_tokens: int = 256):

        self.model_id = model_id
        self.quant = quant.lower()
        self.cache_dir = Path(cache_dir).expanduser()
        self.n_ctx = n_ctx
        self.n_threads = n_threads
        self.n_gpu_layers_cfg = n_gpu_layers
        self.temperature = temperature
        self.max_tokens = max_tokens

        self._llm = None
        self._loaded = False
        self._embed_dim = 0

        # Janela Deslizante
        self._history: deque = deque(maxlen=50)
        self._system_prompt = "Você é o Oráculo da Cathedral ARKHE. Responda de forma precisa."

        # Fila Serial (Thread-Safety)
        self._queue: asyncio.Queue[_InferenceRequest] = asyncio.Queue()
        self._worker_task: Optional[asyncio.Task] = None

        # Cache Semântico
        self._semantic_cache: deque[Tuple[List[float], str]] = deque(maxlen=30)
        self._cache_threshold = 0.98

        # Métricas Internas
        self._load_time_ms = 0.0
        self._tokens_generated = 0
        self._gen_time_ms = 0.0
        self._cache_hits = 0
        self._cache_misses = 0

        self._try_load()

    def _detect_gpu_layers(self) -> int:
        if self.n_gpu_layers_cfg != -1: return self.n_gpu_layers_cfg
        if HAS_TORCH and torch.cuda.is_available(): return 99
        return 0

    def _resolve_and_download_model(self) -> Optional[Path]:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        for f in self.cache_dir.rglob(f"*{self.quant}*.gguf"): return f
        if HAS_HF_HUB:
            try:
                logger.info("Baixando %s (%s) via HuggingFace...", self.model_id, self.quant)
                path = hf_hub_download(repo_id=self.model_id, filename=f"*{self.quant}*.gguf", cache_dir=str(self.cache_dir))
                return Path(path)
            except Exception as e: logger.error("Falha no download HF: %s", e)
        return None

    def _try_load(self):
        if not HAS_LLAMA_CPP: return logger.warning("llama-cpp-python não instalado. Operando em modo Stub.")
        path = self._resolve_and_download_model()
        if not path or not path.exists(): return logger.warning("Modelo GGUF não encontrado.")
        try:
            start = time.time()
            self._llm = Llama(model_path=str(path), n_ctx=self.n_ctx, n_threads=self.n_threads, n_gpu_layers=self._detect_gpu_layers(), verbose=False)
            self._load_time_ms = (time.time() - start) * 1000
            self._loaded = True
            try: self._embed_dim = len(self._llm.embed("test"))
            except: self._embed_dim = 0
            logger.info("GGUF Carregado (GPU:%d, Dim:%d, Load:%.0fms)", self._detect_gpu_layers(), self._embed_dim, self._load_time_ms)
        except Exception as e: logger.error("Falha ao carregar GGUF: %s", e)

    async def start(self):
        if self._loaded and self._worker_task is None:
            self._worker_task = asyncio.create_task(self._worker_loop())

    async def stop(self):
        if self._worker_task:
            self._worker_task.cancel()
            try: await self._worker_task
            except asyncio.CancelledError: pass

    async def _worker_loop(self):
        loop = asyncio.get_running_loop()
        while True:
            req = await self._queue.get()
            try:
                result = await loop.run_in_executor(None, self._sync_generate, req.prompt, req.kwargs)
                if not req.future.done(): req.future.set_result(result)
            except Exception as e:
                if not req.future.done(): req.future.set_exception(e)

    def _sync_generate(self, prompt: str, kwargs: Dict) -> Dict[str, Any]:
        output = self._llm(prompt, **kwargs)
        text = output["choices"][0]["text"].strip()
        tokens = output.get("usage", {}).get("completion_tokens", 0)
        self._tokens_generated += tokens
        return {"text": text, "tokens": tokens}

    async def embed(self, text: str) -> List[float]:
        if not self.is_available() or self._embed_dim == 0: return [0.0] * 64
        loop = asyncio.get_running_loop()
        raw_emb = await loop.run_in_executor(None, self._llm.embed, text)
        norm = math.sqrt(sum(x*x for x in raw_emb))
        return [x / norm for x in raw_emb] if norm > 0 else raw_emb

    async def _check_semantic_cache(self, prompt: str) -> Optional[str]:
        if not self._semantic_cache or self._embed_dim == 0: return None
        prompt_emb = await self.embed(prompt)
        for cached_emb, cached_resp in self._semantic_cache:
            if sum(a*b for a, b in zip(prompt_emb, cached_emb)) >= self._cache_threshold:
                return cached_resp
        return None

    def _build_prompt_sliding_window(self, user_prompt: str) -> str:
        self._history.append({"role": "user", "content": user_prompt})
        max_ctx_chars = (self.n_ctx - self.max_tokens - 50) * 4
        parts = [f"[System]: {self._system_prompt}\n"]
        current_chars = len(parts[0])
        for msg in reversed(self._history):
            msg_str = f"[{msg['role'].capitalize()}]: {msg['content']}\n"
            if current_chars + len(msg_str) > max_ctx_chars: break
            parts.insert(1, msg_str); current_chars += len(msg_str)
        parts.append("[Assistant]:")
        return "".join(parts)

    def is_available(self) -> bool: return self._loaded and self._llm is not None

    async def generate(self, prompt: str, use_history: bool = True) -> Dict[str, Any]:
        if not self.is_available(): return {"text": f"[GGUF Stub] {prompt[:50]}", "tokens": 0}

        cached = await self._check_semantic_cache(prompt)
        if cached:
            self._cache_hits += 1
            return {"text": cached, "tokens": 0, "cache_hit": True}
        self._cache_misses += 1

        final_prompt = self._build_prompt_sliding_window(prompt) if use_history else prompt
        req = _InferenceRequest(future=asyncio.get_running_loop().create_future(), prompt=final_prompt, kwargs={"max_tokens": self.max_tokens, "temperature": self.temperature, "stop": ["\n\n[", "["]})
        self._queue.put_nowait(req)

        start = time.monotonic()
        result = await req.future
        duration_ms = (time.monotonic() - start) * 1000
        self._gen_time_ms += duration_ms

        if not result.get("cache_hit"):
            self._semantic_cache.append((await self.embed(prompt), result["text"]))
        return result

    def get_stats(self) -> Dict[str, Any]:
        tps = (self._tokens_generated / (self._gen_time_ms / 1000)) if self._gen_time_ms > 0 else 0.0
        total_c = self._cache_hits + self._cache_misses
        return {
            "loaded": self._loaded, "model_id": self.model_id, "embed_dim": self._embed_dim,
            "load_time_ms": round(self._load_time_ms, 1),
            "total_tokens": self._tokens_generated, "tokens_per_second": round(tps, 2),
            "cache_hits": self._cache_hits, "cache_misses": self._cache_misses,
            "cache_hit_rate": round(self._cache_hits / total_c, 3) if total_c > 0 else 0.0,
            "queue_size": self._queue.qsize()
        }

# =============================================================================
# 3. INFERENCE ROUTER
# =============================================================================

class InferenceMode(Enum):
    LOCAL_GGUF = auto(); EXTERNAL_API = auto(); STUB_FALLBACK = auto()

class InferenceRouter:
    def __init__(self, gguf_engine: GgufInferenceEngine, cost_limit_usd: float = 5.0):
        self.gguf = gguf_engine
        self.cost_limit = cost_limit_usd
        self.spent_this_hour = 0.0

    def decide_route(self, complex_reasoning: bool = False, force_local: bool = False) -> InferenceMode:
        if force_local: return InferenceMode.LOCAL_GGUF if self.gguf.is_available() else InferenceMode.STUB_FALLBACK
        if self.spent_this_hour >= self.cost_limit: return InferenceMode.LOCAL_GGUF if self.gguf.is_available() else InferenceMode.STUB_FALLBACK
        if complex_reasoning and self.gguf.is_available(): return InferenceMode.LOCAL_GGUF # Mesmo complexo, tenta local primeiro na v14
        return InferenceMode.LOCAL_GGUF if self.gguf.is_available() else InferenceMode.STUB_FALLBACK

    async def infer(self, prompt: str, **kwargs) -> Dict[str, Any]:
        mode = self.decide_route(kwargs.pop("complex_reasoning", False), kwargs.pop("force_local", False))
        start = time.monotonic()

        if mode == InferenceMode.LOCAL_GGUF:
            res = await self.gguf.generate(prompt, **kwargs)
            return {"text": res["text"], "mode": mode.name, "tokens": res["tokens"], "duration_s": time.monotonic() - start, "cache_hit": res.get("cache_hit", False)}
        elif mode == InferenceMode.EXTERNAL_API:
            await asyncio.sleep(0.05)
            self.spent_this_hour += 0.0001
            return {"text": "[API] Simulação.", "mode": mode.name, "tokens": 100, "duration_s": time.monotonic() - start, "cache_hit": False}
        else:
            return {"text": "[Stub] Degradado.", "mode": mode.name, "tokens": 0, "duration_s": time.monotonic() - start, "cache_hit": False}

# =============================================================================
# 4. ORCHESTRATOR V14.0.0
# =============================================================================

class CathedralOrchestratorV14_0_0:
    def __init__(self, config: Dict):
        self.config = config
        self.cycle = 0
        self._shutdown_event = asyncio.Event()

        self.prom = PrometheusRegistry()
        self.gguf = GgufInferenceEngine(**config.get("gguf", {}))
        self.router = InferenceRouter(self.gguf, config.get("inference", {}).get("cost_limit_usd", 5.0))
        self._server = None

    async def start(self):
        logger.info("Iniciando Orquestrador v14.0.0...")
        await self.gguf.start()
        port = self.config.get("prometheus", {}).get("port", 9090)
        self._server = await asyncio.start_server(self._handle_prom, "0.0.0.0", port)
        logger.info("Prometheus exposto em :%d/metrics", port)
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try: loop.add_signal_handler(sig, self._trigger_shutdown)
            except NotImplementedError: pass

    async def stop(self):
        logger.info("Desligando v14.0.0...")
        self._shutdown_event.set()
        await self.gguf.stop()
        if self._server: self._server.close(); await self._server.wait_closed()

    def _trigger_shutdown(self):
        if not self._shutdown_event.is_set(): asyncio.create_task(self.stop())

    async def run(self):
        await self.start()
        try:
            while not self._shutdown_event.is_set():
                try:
                    await self.tick()
                    await asyncio.sleep(2.0)
                except Exception as e:
                    logger.critical("Erro no tick: %s", e, exc_info=True)
        finally:
            await self.stop()

    async def tick(self):
        self.cycle += 1
        prompt = f"Analise metricas do ciclo {self.cycle} e sugira otimizações."
        result = await self.router.infer(prompt, complex_reasoning=(self.cycle % 5 == 0))
        self._update_metrics(result)

    def _update_metrics(self, res: Dict):
        self.prom.gauge("cathedral_cycle", float(self.cycle))
        stats = self.gguf.get_stats()
        self.prom.gauge("cathedral_gguf_tokens_per_sec", stats["tokens_per_second"])
        self.prom.gauge("cathedral_gguf_cache_hit_rate", stats["cache_hit_rate"])
        self.prom.gauge("cathedral_gguf_queue_size", float(stats["queue_size"]))
        self.prom.counter_inc("cathedral_inferences_total", 1.0, {"mode": res["mode"]})
        self.prom.counter_inc("cathedral_inference_tokens_total", float(res["tokens"]), {"mode": res["mode"]})
        if res.get("cache_hit"): self.prom.counter_inc("cathedral_gguf_cache_hits_total")
        self.prom.histogram_observe("cathedral_inference_duration_seconds", res["duration_s"], labels={"mode": res["mode"]})

    async def _handle_prom(self, reader, writer):
        try:
            req = (await reader.readline()).decode(errors="replace")
            while await reader.readline() != b"\r\n": pass
            body = self.prom.render() if "/metrics" in req else '{"status":"v14_active"}'
            writer.write(f"HTTP/1.1 200 OK\r\nContent-Length: {len(body)}\r\n\r\n{body}".encode())
            await writer.drain()
        finally:
            writer.close()

# =============================================================================
# ENTRY POINT
# =============================================================================

async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
    config = {
        "gguf": {"model_id": "unsloth/Qwen3-0.6B-GGUF", "quant": "Q4_K_M", "n_ctx": 4096},
        "prometheus": {"port": 9090}
    }
    await CathedralOrchestratorV14_0_0(config).run()

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: pass
