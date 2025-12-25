
class RV64:
    def __init__(self):
        self.regs = [0] * 32
        self.pc = 0x80200000
        self.mem = bytearray(1024 * 1024)


if __file__ == '__main__':
    cpu = RV64()

    # Load kernel
    path_to_kernel = '/Users/Bartek/gitreps/os/kernel.elf'

    with open(path_to_kernel, 'rb') as kernel:
        kernel_data = kernel.read()
