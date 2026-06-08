import os
import sys
content = sys.stdin.read()

lines = content.split('\n')
current_file = None
current_content = []

for line in lines:
    if line.startswith('#!/usr/bin/env python3') and 'CATHEDRAL ARKHE' in content:
        # We can just write the whole thing as one file
        pass
