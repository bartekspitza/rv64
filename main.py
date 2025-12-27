import struct
from dataclasses import dataclass

OFFSET = 0x80200000
R_MASKS = [
    0b0000_0000_0000_0000_0000_0000_0111_1111, # Op code
    0b0000_0000_0000_0000_0000_1111_1000_0000, # rd
    0b0000_0000_0000_0000_0111_0000_0000_0000, # funct3
    0b0000_0000_0000_1111_1000_0000_0000_0000, # rs1
    0b0000_0001_1111_0000_0000_0000_0000_0000, # rs2
    0b1111_1110_0000_0000_0000_0000_0000_0000, # imm
]
twelwe_imm= 0b1111_1111_1110_0000_0000_0000_0000_0000, # imm

def sign_extend(value, bits):
    sign_bit_mask = 1 << (bits-1)

    if value & sign_bit_mask:
        # Negative: fill upper bits with 1s
        mask = (1 << bits) - 1
        return value | (~mask & 0xFFFFFFFFFFFFFFFF)
    else:
        # Positive: just mask to size
        return value & ((1 << bits) - 1)

@dataclass
class InstructionMeta:
    type: str # I | R | S | B | U | J

class Instruction:
    def __init__(self, instr: int):
        self.raw = instr
        self.opcode = instr & 0b1111_111
        self.meta = self.get_meta()

    def get_meta(self) -> InstructionMeta:
        vals = ()
        if self.opcode == 0b11: # Load (lb, lh etc)
            vals = ("I")

        if len(vals) == 0:
            raise NotImplementedError(f"Type cannot be fetched for opcode={self.opcode}")
        
        return InstructionMeta(vals[0])
        
    
    def __str__(self):
        try:
            return f"instruction={self.decode()}"
        except:
            return f"instruction={hex(self.raw)}"

    def decode(self):
        if self.get_meta() == "I":
            return {
                'opcode': self.opcode,
                'rd': (R_MASKS[1] & instr) >> 7, 
                'func3': (R_MASKS[2] & instr) >> 12,
                'rs1': (R_MASKS[3] & instr) >> 15,
                'imm': sign_extend((twelwe_imm & instr) >> 20, 12)
            }


class RV64:
    def __init__(self):
        self.regs = [0] * 32
        self.pc = OFFSET
        self.mem = bytearray(1024 * 1024)

    def fetch(self) -> Instruction:
        addr = self.pc - OFFSET
        instr = struct.unpack('<I', self.mem[addr:addr+4])[0]
        return Instruction(instr)
    
    def decode(self, instr: Instruction) -> dict:
        return instr.decode()

    def step(self):
        self.pc += 4

def load_kernel(cpu, path_to_kernel):
    kf = open(path_to_kernel, 'rb')
    kernel_data = kf.read() # Byte array of the entire elf
    kf.close()

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

if __name__ == '__main__':
    cpu = RV64()
    load_kernel(cpu, '/home/maikzy/gitreps/os/os/kernel.elf')

    instr = cpu.fetch()
    print(hex(instr.raw))

    cpu.step()
    instr = cpu.fetch()
    print(instr)

