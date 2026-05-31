import re

with open('arkhe_sdk/__init__.py', 'r') as f:
    content = f.read()

# Update import
content = re.sub(
    r'from \.agentfield_bridge import AgentFieldApp\n',
    r'from .agentfield_bridge import AgentFieldBridge\n',
    content
)

content = re.sub(
    r'"AgentFieldApp",\n',
    r'"AgentFieldBridge",\n',
    content
)

with open('arkhe_sdk/__init__.py', 'w') as f:
    f.write(content)
