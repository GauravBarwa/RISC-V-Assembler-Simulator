import re

opcodes={
    'add':'0110011',#R
    'sub':'0110011',#R
    'slt':'0110011',#R
    'srl':'0110011',#R
    'or':'0110011', #R
    'and':'0110011',#R
    'lw':'0000011',#I
    'addi':'0010011',#I
    'jalr':'1100111',#I
    'sw':'0100011',#S
    'beq':'1100011',#B
    'bne':'1100011',#B
    'blt':'1100011',#B
    'jal':'1101111' #J
}

funct3= {
    'add':'000',#R
    'sub':'000',#R
    'slt':'010',#R
    'srl':'101',#R
    'or':'110', #R
    'and':'111',#R
    'lw':'010',#I
    'addi':'000',#I
    'jalr':'000',#I
    'sw':'010',#S
    'beq':'000',#B
    'bne':'001',#B
    'blt':'100'#B
}

funct7 = {
    'add':'0000000',#R
    'sub':'0100000',#R
    'slt':'0000000',#R
    'srl':'0000000',#R
    'or':'0000000', #R
    'and':'0000000' #R
}
registers={
'zero':'00000',
'ra':'00001',
'sp':'00010',
'gp':'00011',
'tp':'00100',
't0':'00101',
't1':'00110',
't2':'00111',
's0':'01000',
's1':'01001',
'a0':'01010',
'a1':'01011',
'a2':'01100',
'a3':'01101',
'a4':'01110',
'a5':'01111',
'a6':'10000',
'a7':'10001',
's2':'10010',
's3':'10011',
's4':'10100',
's5':'10101',
's6':'10110',
's7':'10111',
's8':'11000',
's9':'11001',
's10':'11010',
's11':'11011',
't3':'11100',
't4':'11101',
't5':'11110',
't6':'11111'
}

def int_to_binary(num, bits):
    if num >= 0:
        return format(num, f'0{bits}b')
    else:
        return format((1 << bits) + num, f'0{bits}b')

def r_type(op,rd,rs1,rs2):
    funct7_bin=funct7[op]
    rs2_bin, rs1_bin, rd_bin=registers[rs2],registers[rs1], registers[rd]
    funct3_bin=funct3[op]
    opcode=opcodes[op]
    return funct7_bin+rs2_bin+rs1_bin+funct3_bin+rd_bin+opcode

def i_type(op,rd,rs1,imm):
    rs1_bin, rd_bin = registers[rs1], registers[rd]
    opcode = opcodes[op]
    imm = int_to_binary(imm, 12)
    funct3_bin = funct3[op]
    return imm+rs1_bin+funct3_bin+rd_bin+opcode

def s_type(op,rs2,imm,rs1):
    rs1_bin, rs2_bin = registers[rs1], registers[rs2]
    funct3_bin = funct3[op]
    opcode = opcodes[op]
    imm = int_to_binary(imm, 12)
    return imm[0:7]+rs2_bin+rs1_bin+funct3_bin+imm[7:12]+opcode

def b_type(op,rs1,rs2,imm):
    rs1_bin , rs2_bin = registers[rs1], registers[rs2]
    funct3_bin = funct3[op]
    opcode = opcodes[op]
    imm = int_to_binary(imm , 13)[:-1]
    # print(imm)
    return imm[-12] + imm[-10:-4] + rs2_bin + rs1_bin + funct3_bin + imm[-4:] + imm[-11] + opcode

def checkValidity(register_lst):
    for register in register_lst:
        if register not in registers.keys():
            raise Exception(f"Syntax Error: Register {register} is not specified by the ISA")


def j_type(op,rd,imm):
    rd_bin = registers[rd]
    imm = int_to_binary(imm, 21)[:-1]
    opcode = opcodes[op]
    return imm[-20] + imm[-10:20] + imm[-11] + imm[-19:-11] + rd_bin + opcode

def assem(assembly_code):
    pc = 0
    labels_dict = {}
    binary_code = []
    for i in range(len(assembly_code)):
        instruction = assembly_code[i]
        if ':' in instruction:
            label = instruction.split(':')[0].strip()
            labels_dict[label] = pc
            assembly_code[i] = instruction.split(':')[1].strip()
        pc+=4

    pc=0
    for i in range(len(assembly_code)):
        instruction = assembly_code[i].strip().split()
        op = instruction[0]
        parameters = instruction[1].split(',')
        if op in ['add', 'sub', 'slt', 'srl', 'or', 'and']:
            checkValidity(parameters)
            binary_code.append(r_type(op, parameters[0], parameters[1], parameters[2]))
        elif op in ['addi','lw', 'jalr']:
            if op=='lw':
                imm = int(re.split(r'\(|\)', parameters[1])[0])
                rs1 = re.split(r'\(|\)', parameters[1])[1]
                checkValidity([parameters[0], rs1])
                binary_code.append(i_type(op, parameters[0], rs1, imm))
            else:
                checkValidity([parameters[0], parameters[1]])
                imm = int(parameters[2])
                binary_code.append(i_type(op, parameters[0], parameters[1], imm))
        elif op in ['jal']:
            if parameters[1] in labels_dict.keys():
                binary_code.append(j_type(op, parameters[0], labels_dict[parameters[1]]-pc))
            else:
                try:
                    binary_code.append(j_type(op, parameters[0], int(parameters[1])))
                except:
                    raise Exception(f"Syntax Error: undefined reference to label \"{parameters[1]}\"")

        elif op in ['sw']:
            imm = int(re.split(r'\(|\)', parameters[1])[0])
            rs1 = re.split(r'\(|\)', parameters[1])[1]
            checkValidity([parameters[0], rs1])
            binary_code.append(s_type(op, parameters[0], imm, rs1))
        elif op in ['beq', 'bne', 'blt']:
            if parameters[2] in labels_dict.keys():
                binary_code.append(b_type(op, parameters[0], parameters[1], labels_dict[parameters[2]]-pc))
            else:
                try:
                    binary_code.append(b_type(op, parameters[0], parameters[1], int(parameters[2])))
                except:
                    raise Exception(f"Syntax Error: undefined reference to label \"{parameters[2]}\"")

        else:
            raise Exception(f"Syntax Error: Operation \"{op}\" is not specified by the ISA")

        pc+=4
    return binary_code



filename = input("Enter name of assembly file: ")

assembly_code = []
with open(filename, 'r') as f:
    label_temp = None 

    for line in f:
        line = re.split(r';|#', line)[0].strip()
        if not line or line.startswith(";") or line.startswith("#"): 
            continue
        if line.endswith(":"):  
            label_temp = line
            continue
        if label_temp: 
            line = f"{label_temp} {line}"
            label_temp = None  
        assembly_code.append(line) 

     

binary_code = assem(assembly_code)
with open("binary.txt", 'w') as f:
    for line in binary_code:
        f.write(line)
        f.write("\n")

print("Output binary successfully generated in \"binary.txt\"")
