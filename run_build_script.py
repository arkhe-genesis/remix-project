import os
import sys

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)

with open('user_prompt.txt', 'w') as f:
    f.write(sys.stdin.read())
