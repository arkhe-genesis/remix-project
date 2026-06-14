import platform
import os
import subprocess
import sys

print("=== CHECKPOINT FASE 1 (Linux Adaptation) ===")
print("")
print("[1] OS:")
print(platform.system(), platform.release(), platform.version())
print("")
print("[2] NVIDIA Driver:")
try:
    subprocess.run(['nvidia-smi', '--query-gpu=driver_version,name', '--format=csv,noheader'], check=True)
except FileNotFoundError:
    print("  nvidia-smi NAO ENCONTRADO")
print("")
print("[3] CUDA:")
try:
    subprocess.run(['nvcc', '--version'], check=True)
except FileNotFoundError:
    print("  nvcc NAO ENCONTRADO")
print("")
print("[4] Python:")
print(sys.version)
print("")
print("[5] PyTorch + CUDA:")
try:
    import torch
    print(f'  CUDA: {torch.cuda.is_available()}, GPUs: {torch.cuda.device_count()}, Device 0: {torch.cuda.get_device_name(0) if torch.cuda.device_count() > 0 else "N/A"}')
except ImportError:
    print("  torch NAO ENCONTRADO")
print("")
print("[6] Rust:")
try:
    subprocess.run(['rustc', '--version'], check=True)
    subprocess.run(['cargo', '--version'], check=True)
except FileNotFoundError:
    print("  rustc/cargo NAO ENCONTRADO")
print("")
print("[7] C Compiler:")
try:
    subprocess.run(['gcc', '--version'], stdout=subprocess.PIPE, check=True)
    print("  gcc ENCONTRADO")
except FileNotFoundError:
    print("  gcc NAO ENCONTRADO")
print("")
print("[8] Dependências Python críticas:")
mods = ['torch','numpy','aiohttp','transformers','z3','cv2','ultralytics','timm','hnswlib','yaml','prometheus_client']
for m in mods:
    try:
        __import__(m)
        print(f'  ✅ {m}')
    except ImportError:
        print(f'  ❌ {m}')

print("")
print("=== FIM CHECKPOINT ===")
