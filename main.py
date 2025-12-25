OFFSET = 0x80200000
class RV64:
    def __init__(self):
        self.regs = [0] * 32
        self.pc = OFFSET
        self.mem = bytearray(1024 * 1024)
    
    def fetch(self):
        addr = self.pc - OFFSET
        instr = struct.unpack('<I', self.mem[addr:addr+4])[0]
        return instr
    
    def step(self):
        self.pc += 4

if __name__ == '__main__':
    cpu = RV64()

    # Load kernel elf
    path_to_kernel = '/Users/Bartek/gitreps/os/kernel.elf'
    kf = open(path_to_kernel, 'rb')
    kernel_data = kf.read() # Byte array of the entire elf
    kf.close()
    import struct

    # Where does the program header table start, even though
    # it seems its always directly after the header, i.e. 64
    e_phoff = struct.unpack('<Q', kernel_data[32:40])[0]

    # How many program headers are there
    e_phnum = struct.unpack('<H', kernel_data[56:58])[0]

    # Iterate over the table entries
    for i in range(e_phnum):
        # Calculate file offset of this ph entry
        # Each ph entry is 56 bytes
        e_offset = e_phoff + i*56 # the file offset of this ph entry
        # each 
        p_type = struct.unpack('<I', kernel_data[e_offset:e_offset+4])[0]

        if p_type == 1:
            # Load
            p_offset = struct.unpack('<Q', kernel_data[e_offset+8:e_offset+16])[0]
            p_vaddr = struct.unpack('<Q', kernel_data[e_offset+16:e_offset+24])[0]
            p_filesz = struct.unpack('<Q', kernel_data[e_offset+32:e_offset+40])[0]
            p_memsz = struct.unpack('<Q', kernel_data[e_offset+40:e_offset+48])[0]

            # Copy segment to memory
            mem_offset = p_vaddr - OFFSET
            cpu.mem[mem_offset:mem_offset+p_filesz] = kernel_data[p_offset:p_offset+p_filesz]
            # Zero out bss
            cpu.mem[mem_offset+p_filesz:mem_offset+p_memsz] = b'\x00' * (p_memsz - p_filesz)
