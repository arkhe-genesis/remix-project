import os
import sys
import re

content = sys.stdin.read()

# Match the big python file at the end
match = re.search(r'#!/usr/bin/env python3\n"""\n╔════.*?if __name__ == "__main__":\n    demo_orchestrator_v5_1\(\)', content, re.DOTALL)
if match:
    os.makedirs('cathedral-arkhe/cathedral/orchestrator', exist_ok=True)
    with open('cathedral-arkhe/cathedral/orchestrator/v5_1.py', 'w') as f:
        f.write(match.group(0))
        print("Wrote cathedral-arkhe/cathedral/orchestrator/v5_1.py")
else:
    print("Could not find the orchestrator file!")
