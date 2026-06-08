import re

with open('cathedral-arkhe/cathedral/orchestrator/v5_1.py', 'r') as f:
    content = f.read()

# Fix duplicated _compute_gate
content = re.sub(
    r"""    def _compute_gate\(self, tee, theosis\):\s+if self\._cycle < 10: return GateState\.OPEN\s+th = self\._gate_thresholds\s+if tee > th\["emergency_tee"\] or theosis < th\["emergency_theta"\]: return GateState\.EMERGENCY\s+if tee > th\["locked_tee"\] and theosis < th\["locked_theta"\]: return GateState\.LOCKED\s+if tee > th\["restricted_tee"\] or theosis < th\["restricted_theta"\]: return GateState\.RESTRICTED\s+if tee > th\["caution_tee"\] or theosis < th\["caution_theta"\]: return GateState\.CAUTION\s+return GateState\.OPEN\s+if tee > th\["emergency_tee"\] or theosis < th\["emergency_theta"\]: return GateState\.EMERGENCY\s+if tee > th\["locked_tee"\] and theosis < th\["locked_theta"\]: return GateState\.LOCKED\s+if tee > th\["restricted_tee"\] or theosis < th\["restricted_theta"\]: return GateState\.RESTRICTED\s+if tee > th\["caution_tee"\] or theosis < th\["caution_theta"\]: return GateState\.CAUTION\s+return GateState\.OPEN""",
    """    def _compute_gate(self, tee, theosis):
        if self._cycle < 10: return GateState.OPEN
        th = self._gate_thresholds
        if tee > th["emergency_tee"] or theosis < th["emergency_theta"]: return GateState.EMERGENCY
        if tee > th["locked_tee"] and theosis < th["locked_theta"]: return GateState.LOCKED
        if tee > th["restricted_tee"] or theosis < th["restricted_theta"]: return GateState.RESTRICTED
        if tee > th["caution_tee"] or theosis < th["caution_theta"]: return GateState.CAUTION
        return GateState.OPEN""",
    content
)

with open('cathedral-arkhe/cathedral/orchestrator/v5_1.py', 'w') as f:
    f.write(content)

# Add CLI files
import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content.strip() + "\n")

write_file("cathedral-arkhe/cathedral/cli/__init__.py", "")

write_file("cathedral-arkhe/cathedral/cli/scan.py", """
def run_scan(args):
    print("Scan feature pending implementation.")
""")

write_file("cathedral-arkhe/cathedral/cli/inspect.py", """
def run_inspect(args):
    print("Inspect feature pending implementation.")
""")

write_file("cathedral-arkhe/cathedral/cli/monitor.py", """
def run_monitor(args):
    print("Monitor feature pending implementation.")
""")
