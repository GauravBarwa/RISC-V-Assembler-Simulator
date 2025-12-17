# RISC-V Assembler & Simulator

A Python-based implementation of an Assembler and Simulator for the RISC-V Instruction Set Architecture (RV32I subset). This project allows users to convert RISC-V assembly code into machine code and simulate its execution, providing a detailed trace of the processor's state.

##  Features

### 1. Assembler
* **Converts Assembly to Binary:** Translates RISC-V assembly instructions into 32-bit binary machine code.
* **Label Support:** Handles symbolic labels for branching and jumps (e.g., `loop:`, `bne t0, t1, loop`).
* **Error Handling:** Detects syntax errors, undefined labels, and invalid registers.
* **Output:** Generates a `binary.txt` file containing the machine code.

### 2. Simulator
* **Execution Trace:** Simulates the generated binary code line-by-line.
* **Register Dump:** Tracks and outputs the state of all 32 registers (`x0`–`x31`) and the Program Counter (PC) in binary format after every instruction.
* **Memory Simulation:** Simulates Data Memory and Stack Memory, providing a memory dump upon termination.
* **Virtual Hardware:**
    * **Registers:** 32 general-purpose registers (x0 is hardwired to 0).
    * **Data Memory Base:** `0x00010000`
    * **Stack Memory Base:** `0x00000100`

## ⚙️ Supported Instructions (RV32I)

The toolchain supports the following instructions:

| Type | Operations |
| :--- | :--- |
| **R-Type** | `add`, `sub`, `slt`, `srl`, `or`, `and` |
| **I-Type** | `lw`, `addi`, `jalr` |
| **S-Type** | `sw` |
| **B-Type** | `beq`, `bne`, `blt` |
| **J-Type** | `jal` |

##  Getting Started

### Prerequisites
* Python 3.6 or higher.

### Installation
Clone the repository:
```bash
git clone [https://github.com/yourusername/riscv-assembler-simulator.git](https://github.com/yourusername/riscv-assembler-simulator.git)
cd riscv-assembler-simulator
