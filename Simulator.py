import sys

registers = {f"x{i}": "0" * 32 for i in range(32)}
registers['x2'] = "00000000000000000000000101111100"
base_address_memory = 0x00010000
base_address_stack = 0x00000100
mem_locations = 32

word_size = 4
data_memory = {base_address_memory + (i * word_size): "0" * 32 for i in range(mem_locations)}
stack_memory = {base_address_stack + (i * word_size) : "0" * 32 for i in range (mem_locations)}

global pc
pc = 0  # Initialize program counter

r_operations = {
    ('0000000', '000'): 'add',
    ('0100000', '000'): 'sub',
    ('0000000', '010'): 'slt',
    ('0000000', '101'): 'srl',
    ('0000000', '110'): 'or',
    ('0000000', '111'): 'and'
}

i_operations = {
    '0000011': 'lw',
    '0010011': 'addi',
    '1100111': 'jalr'
}

s_operations = {
    '0100011': 'sw'
}

b_operations = {
    ('000'): 'beq',
    ('001'): 'bne',
    ('100'): 'blt',
}

def int_to_binary(num, bits=32):
    return format(num if num >= 0 else (1 << bits) + num, f'0{bits}b')

def binary_to_int(binary_str):
    return int(binary_str, 2) if binary_str[0] == '0' else -((1 << len(binary_str)) - int(binary_str, 2))

def int_to_hex(value: int, num_bits: int) -> str:
    # if value < 0:
    #     value = (1 << num_bits) + value
    # hex_digits = num_bits // 4
    # return f"0x{value:0{hex_digits}X}"
    hex_str = hex(value)[2:].upper()  # Convert to hex, remove "0x", uppercase
    return f"0x{hex_str.zfill(num_bits)}"  # Pad with leading zeros
def execute_r_type(rs1, rs2, rd, f3, f7):
    global pc
    try:
        op = r_operations[(f7, f3)]
    except KeyError:
        print(f"Error: Unknown R-type operation at PC {pc}")
        sys.exit(1)
    
    match op:
        case "add":
            registers[rd] = int_to_binary(binary_to_int(registers[rs1]) + binary_to_int(registers[rs2]))
        case "sub":
            registers[rd] = int_to_binary(binary_to_int(registers[rs1]) - binary_to_int(registers[rs2]))
        case "slt":
            registers[rd] = int_to_binary(1 if binary_to_int(registers[rs1]) < binary_to_int(registers[rs2]) else 0)
        case "srl":
            registers[rd] = int_to_binary(binary_to_int(registers[rs1]) >> (binary_to_int(registers[rs2]) & 0x1F))
        case "or":
            registers[rd] = int_to_binary(binary_to_int(registers[rs1]) | binary_to_int(registers[rs2]))
        case "and":
            registers[rd] = int_to_binary(binary_to_int(registers[rs1]) & binary_to_int(registers[rs2]))
    
    pc += 4  # Move to next instruction


def execute_j_type(rd, imm):
    global pc
    registers[rd] = int_to_binary(pc + 4)
    pc += binary_to_int(imm.zfill(32))


def execute_i_type(rs1, rd, imm, f3, opcode):
    global pc
    try:
        op = i_operations[opcode]
    except KeyError:
        print(f"Error: Unknown I-type operation at PC {pc}")
        sys.exit(1)
    
    imm_val = binary_to_int(imm)  # Ensure proper sign extension
    
    match op:
        case "addi":
            # print(f"{pc} {rs1} {rd} {imm}")
            registers[rd] = int_to_binary(binary_to_int(registers[rs1]) + imm_val)
        case "lw":
            address = binary_to_int(registers[rs1]) + imm_val

            # print(address)
            # print(address)
            if address in data_memory:
                registers[rd] = data_memory[address]
            elif address in stack_memory:
                registers[rd] = stack_memory[address]
            else:
                print(f"Error: Memory access out of bounds at PC {pc}")
                sys.exit(1)
        case "jalr":
            if rd=='x0':
                pass
            else:
                registers[rd] = int_to_binary(pc + 4)
            target = binary_to_int(registers[rs1]) + imm_val
            pc = target
            return  # Ensure PC update takes effect immediately
    
    pc += 4  # Move to next instruction

def execute_s_type(rs1, rs2, imm, opcode):
    # print(imm)
    global pc
    imm_val = binary_to_int(imm)  # Ensure proper sign extension
    address = binary_to_int(registers[rs1]) + imm_val

    # print(address)
    if address in data_memory:
        data_memory[address] = registers[rs2]
    elif address in stack_memory:
        stack_memory[address] = registers[rs2]
    else:
        print(f"Error: Memory access out of bounds at PC {pc} sw")
        sys.exit(1)

    
    pc += 4  # Move to next instruction

def execute_b_type(rs1, rs2, imm, f3):
    global pc
    try:
        op = b_operations[(f3)]
    except KeyError:
        print(f"Error: Unknown B-type operation at PC {pc}")
        sys.exit(1)
    
    rs1_val = binary_to_int(registers[rs1])
    rs2_val = binary_to_int(registers[rs2])
    imm_val = 2*binary_to_int(imm)  # Ensure proper sign extension
    
    match op:
        case "beq":
            if rs1_val == rs2_val:
                pc += imm_val
            else:
                pc += 4
        case "bne":
            if rs1_val != rs2_val:
                pc += imm_val
            else:
                pc += 4
        case "blt":
            if rs1_val < rs2_val:
                pc += imm_val
            else:
                pc += 4
    # print(pc)

def decode_and_execute(inst, line_no):
    global pc
    opcode = inst[-7:]
    # print(inst)
    if opcode == '0110011':  # R-type
        rd = f"x{int(inst[-12:-7], 2)}"
        rs1 = f"x{int(inst[-20:-15], 2)}"
        rs2 = f"x{int(inst[-25:-20], 2)}"
        f3 = inst[-15:-12]
        f7 = inst[:7]
        execute_r_type(rs1, rs2, rd, f3, f7)
    elif opcode in i_operations:  # I-type
        rd = f"x{int(inst[-12:-7], 2)}"
        rs1 = f"x{int(inst[-20:-15], 2)}"
        imm = inst[:12]  # Immediate is first 12 bits
        f3 = inst[-15:-12]
        execute_i_type(rs1, rd, imm, f3, opcode)
    elif opcode == '0100011':  # S-type
        rs1 = f"x{int(inst[-20:-15], 2)}"
        rs2 = f"x{int(inst[-25:-20], 2)}"
        imm = inst[:7] + inst[-12:-7]  # Immediate from different parts
        execute_s_type(rs1, rs2, imm, opcode)
    elif opcode == '1100011':  # B-type
        # print(inst)
        rs1 = f"x{int(inst[-20:-15], 2)}"
        rs2 = f"x{int(inst[-25:-20], 2)}"
        # imm = inst[:12]  # Immediate
        imm = f"{inst[0]}{inst[-8]}{inst[-31:-25]}{inst[-12:-8]}"
        f3 = inst[-15:-12]
        # print(f"{rs1}   {rs2}   {binary_to_int(imm)}   {f3}")
        if(int(imm, 2) == 0 and rs1==rs2):
            return 1
        execute_b_type(rs1, rs2, imm, f3)
    elif opcode == '1101111':
        rd = f"x{int(inst[-12:-7], 2)}"
        imm = f"{inst[-32]}{inst[-20:-12]}{inst[-21]}{inst[-31:-21]}0"
        execute_j_type(rd, imm)
    else:
        # print(inst)
        # print(opcode)
        print(f"Error at line {line_no}: Unknown opcode {opcode}")
        sys.exit(1)
    
    # print(opcode)
    return 0

def write_trace(output_file):
    with open(output_file, 'a') as f:
        f.write(f"0b{int_to_binary(pc, 32)} ")
        for i in range(32):
            f.write(f"0b{registers[f"x{i}"]} ")
        f.write("\n")

def run_simulator(input_file, output_file):
    # print(input_file, output_file)
    f = open(output_file, 'w')
    f.close()
    with open(input_file, 'r') as f:
        instructions = f.read().splitlines()
    # print(instructions)
    while(pc <= 4*(len(instructions)-1)):
        inst_to_execute = int(pc/4)
        if decode_and_execute(instructions[inst_to_execute], inst_to_execute+1):
            write_trace(output_file)
            break
        write_trace(output_file)

    # for line_no, inst in enumerate(instructions, 1):
    #     decode_and_execute(inst, line_no)
    #     write_trace(output_file)

    with open(output_file, 'a') as f:
        output = ""
        for i in range(mem_locations):
            address = base_address_memory + (i * word_size)
            output += f"{int_to_hex(address, 8)}:0b{data_memory[address]}\n"
        f.write(output.strip())

# input_file = sys.argv[0]
# output_file = sys.argv[1]
# run_simulator(input_file, output_file)
# run_simulator("text.txt", "trace.txt")
# Add this at the end of the simulator code (replace the last two lines)
# if __name__ == "__main__":
    # if len(sys.argv) >= 3:
input_file = sys.argv[1]
output_file = sys.argv[2]
run_simulator(input_file, output_file)
    # else:
        # print("Usage: python Simulator.py <input_file> <output_file>")
