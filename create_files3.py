import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content.lstrip('\n'))
    print(f"Created {path}")

write_file("cathedral-arkhe/Makefile", """
# Makefile — Cathedral ARKHE

.PHONY: .DEFAULT
SHELL := /bin/bash

# ─── Desenvolvimento ───

install:
	pip install -e ".[dev]"
	@echo "✓ Dependências de desenvolvimento instaladas"

install-llm:
	pip install -e ".[llm]"
	@echo "✓ Dependências de inferência instaladas"

install-zkml:
	pip install -e ".[zkml]"
	@echo "✓ Dependências ZKML instaladas"

install-lora:
	pip install -e ".[lora]"
	@echo "✓ Dependências LoRA instaladas"

install-all:
	pip install -e ".[all]"
	@echo "✓ Todas as dependências instaladas"

# ─── Testes ───

test:
	pytest tests/ -v --tb=short
	@echo "✓ Testes passaram"

test-fast:
	pytest tests/ -v --tb=short -k "not slow and not real"
	@echo "✓ Testes rápidos passaram"

test-coverage:
	pytest tests/ --cov=cathedral --cov-report=html -v --tb=short
	@echo "✓ Cobertura gerada em htmlcov/"

test-integration:
	pytest tests/ -v --tb=short -m integration
	@echo "✓ Testes de integração passaram"

# ─── Qualidade ───

lint:
	ruff check cathedral/
	ruff format --check cathedral/
	@echo "✓ Lint passou"

typecheck:
	mypy cathedral/ --ignore-missing-imports
	@echo "✓ Type check completou"

format:
	ruff format cathedral/
	@echo "✓ Código formatado"

# ─── Documentação ───

docs:
	python -c "from cathedral._version import SEALS; \\
	           import json; \\
	           print(json.dumps(SEALS, indent=2))"
	@echo "✓ Selos listados"

# ─── Demonstração ───

demo:
	python examples/full_orchestration.py
	@echo "✓ Demonstração executada"

demo-meta-attack:
	python examples/meta_attack_experiment.py
	@echo "✓ Experimento meta-attack executado"

# ─── Limpeza ───

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".pytest_cache" -delete
	find reports/ -name "*.jsonl" -delete 2>/dev/null || true
	@echo "✓ Limpo"

# ─── Publicação ───

publish-test:
	python -m build
	twine check dist/*
	@echo "✓ Build e check passaram"

publish:
	python -m build
	twine upload dist/*
	@echo "✓ Publicado no PyPI"

# ─── Info ───

info:
	@echo "Cathedral ARKHE v$$(python -c 'from cathedral._version import __version__; print(__version__)')"
	@echo "Substratos: 10"
	@echo "Selos: $$(python -c 'from cathedral._version import SEALS; print(len(SEALS))')"
""")

write_file("cathedral-arkhe/.github/workflows/test.yml", """
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [main, "v*"]
  pull_request:
    branches: [main]

jobs:
  test-fast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -e ".[dev]"
      - run: pytest tests/ -v --tb=short -k "not slow and not real"
        timeout-minutes: 5

  test-full:
    runs-on: ubuntu-latest
    needs: test-fast
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -e ".[dev]"
      - run: pytest tests/ -v --tb=short --cov=cathedral --cov-report=xml
        timeout-minutes: 15
      - uses: codecov/codecov-action@v4
        with:
          files: coverage.xml

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install ruff mypy
      - run: ruff check cathedral/
      - run: ruff format --check cathedral/
      - run: mypy cathedral/ --ignore-missing-imports
""")

write_file("cathedral-arkhe/.github/workflows/publish.yml", """
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  push:
    tags: ["v*"]

permissions:
  id-token: write

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install build twine
      - run: python -m build
      - run: twine upload dist/*
""")

write_file("cathedral-arkhe/scripts/convert_to_gguf.py", """
#!/usr/bin/env python3
\"\"\"Converte modelo HuggingFace para GGUF com quantização.

Uso:
    python scripts/convert_to_gguf.py meta-llama/Llama-2-7b-hf --quant q4_k_m
\"\"\"

import argparse
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description="HF → GGUF conversion")
    parser.add_argument("model_id", help="HuggingFace model ID or local path")
    parser.add_argument("--quant", default="q4_k_m",
                        choices=["q4_0", "q4_1", "q5_0", "q5_1", "q4_k_s", "q4_k_m",
                                 "q5_k_s", "q5_k_m", "q6_k", "q8_0"],
                        help="Quantização (default: q4_k_m)")
    parser.add_argument("--out", default=None,
                        help="Output path (default: auto)")
    parser.add_argument("--ctx", type=int, default=4096,
                        help="Context length (default: 4086→4096)")
    args = parser.parse_args()

    model_id = args.model_id
    out_name = args.out or f"{model_id.split('/')[-1]}-{args.quant}.gguf"

    cmd = [
        sys.executable, "-m", "llama_cpp.convert",
        model_id,
        "--outtype", "gguf",
        "--outfile", out_name,
        "--outquant", args.quant,
    ]

    print(f"Convertendo: {model_id} → {out_name} ({args.quant})")
    print(f"Comando: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"Erro: {result.stderr}")
        sys.exit(1)

    print(f"\\n✓ Modelo salvo: {out_name}")
    print(f"  Tamanho: {__import__('os').path.getsize(out_name) / 1e9:.2f} GB")


if __name__ == "__main__":
    main()
""")

write_file("cathedral-arkhe/scripts/run_meta_attack.py", """
#!/usr/bin/env python3
\"\"\"Executa experimento de 5 rodadas de meta-attack.

Uso:
    python scripts/run_meta_attack.py --model model.gguf --rounds 5
    python scripts/run_meta_attack.py --model model.gguf --rounds 10 --output results.jsonl
\"\"\"

import argparse
import json
import sys
import time

# Importa o experimento do módulo de exemplos
sys.path.insert(0, ".")


def main():
    parser = argparse.ArgumentParser(description="Meta-attack experiment")
    parser.add_argument("--model", required=True, help="Path to GGUF model")
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--prompt", default=None,
                        help="Custom meta-attack prompt")
    parser.add_argument("--output", default=None, help="Output JSONL path")
    args = parser.parse_args()

    # Se não importou o exemplo, executa standalone
    try:
        from examples.meta_attack_experiment import run_meta_attack_experiment
    except ImportError:
        # Executa como módulo standalone
        exec(open("examples/meta_attack_experiment.py").read())

    if args.prompt:
        # Substitui o prompt padrão
        import examples.meta_attack_experiment as ma
        ma.META_ATTACK_PROMPT = args.prompt

    if args.output:
        # Redireciona saída para arquivo
        import io
        captured = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured

        try:
            run_meta_attack_experiment()
        finally:
            sys.stdout = old_stdout
            with open(args.output, "w") as f:
                f.write(captured.getvalue())
        print(f"\\n✓ Resultados salvos em {args.output}")
    else:
        run_meta_attack_experiment()


if __name__ == "__main__":
    main()
""")
