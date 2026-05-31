import re

with open('arkhe_sdk/arkhe_os.py', 'r') as f:
    content = f.read()

# Update import
content = re.sub(
    r'from \.agentfield_bridge import AgentFieldApp\n',
    r'from .agentfield_bridge import AgentFieldBridge\n',
    content
)

with open('arkhe_sdk/arkhe_os.py', 'w') as f:
    f.write(content)
