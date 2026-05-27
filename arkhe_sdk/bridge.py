class OWLWeb3Bridge:
    def __init__(self, registry_address):
        self.registry_address = registry_address

    def sdx_to_erc8257(self, artifact):
        # Stub implementation
        return {"registry": self.registry_address, "payload": artifact}
