# Mips-diassembler-simulator
This is a MIPS architecture implementation without pipeline.
This simple MIPS simulator performs the following two tasks:
• Load a specified MIPS text file1
and generate the assembly code equivalent to the input file
(disassembler). 
• Generate the instruction-by-instruction simulation of the MIPS code (simulator). It should also
produce/print the contents of registers and data memories after execution of each instruction.
There is no exception/interrupt handling for this project.
Instructions
The instructions supported by this simulator is shown in the manual of MIPS, which has two categories.

Category-1
* J, JR, BEQ, BLTZ, BGTZ
* BREAK
* SW, LW
* SLL, SRL, SRA
* NOP
Category-2
* ADD, SUB, MUL, AND
* OR, XOR, NOR
* SLT
* ADDI
* ANDI, ORI, XORI

There are small changes to the opcode to fit the instructions to the simulator, which will be specified in the project requirement.
