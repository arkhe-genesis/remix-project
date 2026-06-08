import re

with open('cathedral-arkhe/cathedral/orchestrator/v5_1.py', 'r') as f:
    content = f.read()

new_compute_tee = """
    def _compute_tee(self, buffer, use_rkhs=True):
        predicted = self._rkhs_predict(buffer) if use_rkhs else self._linear_predict(buffer)
        if predicted is None: return None
        h_t = np.array(buffer[-1], dtype=np.float64)
        error = np.linalg.norm(h_t - predicted)
        scale = max(np.linalg.norm(h_t), 0.1) * 20.0
        return float(error / scale)
"""
content = re.sub(r'    def _compute_tee.*?return float\(error / \(scale \+ 1e-12\)\)', new_compute_tee.strip('\n'), content, flags=re.DOTALL)

new_compute_gate = """
    def _compute_gate(self, tee, theosis):
        if self._cycle < 10: return GateState.OPEN
        th = self._gate_thresholds
        if tee > th["emergency_tee"] or theosis < th["emergency_theta"]: return GateState.EMERGENCY
        if tee > th["locked_tee"] and theosis < th["locked_theta"]: return GateState.LOCKED
        if tee > th["restricted_tee"] or theosis < th["restricted_theta"]: return GateState.RESTRICTED
        if tee > th["caution_tee"] or theosis < th["caution_theta"]: return GateState.CAUTION
        return GateState.OPEN
"""

content = re.sub(r'    def _compute_gate.*?return GateState\.OPEN\n', new_compute_gate.strip('\n') + '\n', content, flags=re.DOTALL)

with open('cathedral-arkhe/cathedral/orchestrator/v5_1.py', 'w') as f:
    f.write(content)
