class FPGAFilterOffload:
    def __init__(self, fpga_device: str = "/dev/fpga0"):
        self.device = fpga_device
        self.loaded = False

    def compile_rules(self, rules: list) -> bytes:
        return b"FPGA_BITSTREAM_PLACEHOLDER"

    def load_bitstream(self, bitstream: bytes):
        self.loaded = True

    def filter_batch(self, packets: list) -> list:
        if not self.loaded:
            raise RuntimeError("FPGA not loaded")
        return []
