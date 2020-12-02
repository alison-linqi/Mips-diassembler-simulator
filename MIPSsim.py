#  On my honor, I have neither given nor received unauthorized aid on this assignment
#  Author: Lin Qi

import linecache
import os
import numpy as np
import sys
import ctypes
import math
# global
PC = 252
# reg= dict()
# for i in range(32):
#     reg[i] = 0
Cycle = 0
memory = dict()


reg = np.zeros(32, dtype=int)

opdict= dict(
ADD = "110000",
SUB = "110001",
MUL = "110010",
AND = "110011",
OR = "110100",
XOR = "110101",
NOR = "110110",
SLT = "110111",
ADDI = "111000",
ANDI = "111001",
ORI = "111010",
XORI = "111011",
J = "010000",
JR = "010001",
BEQ = "010010",
BLTZ = "010011",
BGTZ = "010100",
BREAK = "010101",
SW = "010110",
LW = "010111",
SLL = "011000",
SRL = "011001",
SRA = "011010",
NOP = "011011")
# op_mask = 0b11111100000000000000000000000000
regset = {'ADD','SUB','MUL','AND', 'OR', 'XOR', 'SLT','NOR'}
immeset = {'ADDI', 'ANDI', 'ORI', 'XORI'}
slw_set = {'SW', 'LW'}

def searchkey(binary_code):
    for i in opdict.keys():
        if binary_code == opdict.get(i):
            return i
    return "data"

# def searchop(s):
#     for i in opdict.keys():
#         if s == opdict.get(i):
#             return i
#     return "data"


def swlw(s):
    base = int(s[6:11], 2)
    rt = int(s[11:16], 2)
    offset = str(s[16:32])
    offset = handledata(offset)
    return str(rt), str(offset), str(base)

def getreg(s):
    rs = int(s[6:11], 2)
    rt = int(s[11:16], 2)
    rd = int(s[16:21], 2)
    return str(rd), str(rs), str(rt)

def getimme(s):
    rs = int(s[6:11], 2)
    rt = int(s[11:16], 2)
    imme = str(s[16:32])
    # imme = imme[2: len(imme) - 1]
    imme = handledata(imme)
    # imme = int(s[16:32], 2)
    return str(rt), str(rs), str(imme)

# category 2
def add(s):
    global reg
    rd, rs, rt = getreg(s)
    reg[int(rd)] = reg[int(rt)] + reg[int(rs)]
    return


def sub(s):
    global reg
    rd, rs, rt = getreg(s)
    reg[int(rd)] = reg[int(rs)] - reg[int(rt)]
    return


def mul(s):
    global reg
    rd, rs, rt = getreg(s)
    reg[int(rd)] = reg[int(rs)] * reg[int(rt)]
    return


def func_and(s):
    global reg
    rd, rs, rt = getreg(s)
    reg[int(rd)] = reg[int(rs)] & reg[int(rt)]
    return



def func_or(s):
    global reg
    rd, rs, rt = getreg(s)
    reg[int(rd)] = reg[int(rs)] | reg[int(rt)]
    return



def xor(s):
    global reg
    rd, rs, rt = getreg(s)
    reg[int(rd)] = reg[int(rs)] ^ reg[int(rt)]
    return


def nor(s):
    global reg
    rd, rs, rt = getreg(s)
    reg[int(rd)] = -(reg[int(rs)] | reg[int(rt)])
    return


def slt(s):
    global reg
    rd, rs, rt = getreg(s)
    if(reg[int(rs)] < reg[int(rt)]):
        reg[int(rd)] = 1
    else:
        reg[int(rd)] = 0
    return



def addi(s):
    global reg
    rt, rs, imme = getimme(s)
    reg[int(rt)] = reg[int(rs)] + int(imme)
    return


# 16 bit immediate is zero-extended to the left
def andi(s):
    global reg
    rt, rs, imme = getimme(s)
    imme = int(s[16:32], 2)
    reg[int(rt)] = reg[int(rs)] & int(imme)
    return


def ori(s):
    global reg
    rt, rs, imme = getimme(s)
    imme = int(s[16:32], 2)
    reg[int(rt)] = reg[int(rs)] | int(imme)
    return


def xori(s):
    global reg
    rt, rs, imme = getimme(s)
    imme = int(s[16:32], 2)
    reg[int(rt)] = reg[int(rs)] ^ int(imme)
    return



def jump_code(s):
    target = int(s[6:32], 2)
    target = target << 2
    return str(target)

def jr_code(s):
    rs = int(s[6:11], 2)
    return str(rs)

# category 1
def jump(s):
    target = jump_code(s)
    target = int(target)
    global PC
    PC = target
    line = target/4 - 63
    return line

def jr(s):
    global reg
    rs = jr_code(s)
    target = reg[int(rs)]
    global PC
    PC = target
    line = target/4 - 63
    return line

def beq_code(s):
    rs = int(s[6:11], 2)
    rt = int(s[11:16], 2)
    # shift left and get 18 bit signed value
    a = convert_list_to_string(s[16: 32], '')

    # a = a[2: len(a) - 1]
    a = a + "00"
    # print(a)

    offset = handledata(a)
    # print(offset)
    return str(rs), str(rt), str(offset)

def beq(s):
    global reg
    rs, rt, offset = beq_code(s)
    global PC
    if(reg[int(rs)] == reg[int(rt)]):
        PC = PC + 4 + int(offset)
        line = PC/4 - 63
    else:
        PC = PC + 4
        line = PC/4 - 63
    # print("beq code beq code beq code")
    # print(PC)
    return line, PC



bgltzset = {'BLTZ', 'BGTZ'}

def bgltz(s):
    rs = int(s[6:11], 2)

    # shift left and get 18 bit signed value
    a = str(s[16: 32])
    # a = a[2: len(a) - 1]
    a = a + "00"
    offset = handledata(a)
    return str(rs), str(offset)


def bltz(s):
    global reg
    rs, offset = bgltz(s)
    global PC
    if(reg[int(rs)] < 0):
        PC = PC + 4 + int(offset)
        line = PC / 4 - 63
    else:
        PC = PC + 4
        line = PC / 4 - 63
    return line

def bgtz(s):
    global reg
    rs, offset = bgltz(s)
    global PC
    if (reg[int(rs)] > 0):
        PC = PC + 4 + int(offset)
        line = PC / 4 - 63
    else:
        PC = PC + 4
        line = PC / 4 - 63
    return line

# def func_break():
#
#     return


# store value
def sw(s):
    global reg
    global memory
    rt, offset, base = swlw(s)
    memory[reg[int(base)] + int(offset)] = reg[int(rt)]
    return

    # memfield = (ctypes.c_int).from_address(0x0A7F03E4)
# load value
def lw(s):
    global reg
    global memory
    rt, offset, base = swlw(s)
    reg[int(rt)] = memory[reg[int(base)] + int(offset)]
    return

trisset = {'SLL', 'SRL', 'SRA'}
def tris(s):
    rt = int(s[11:16], 2)
    rd = int(s[16:21], 2)
    sa = int(s[21:26], 2)
    return str(rd), str(rt), str(sa)

def sll(s):
    global reg
    rd, rt, sa = tris(s)
    # print("sll line of code ")
    # print(reg[int(rd)])
    reg[int(rd)] = reg[int(rt)] << int(sa)
    # print(reg[int(rd)])
    return

def get_bin(x, n=0):
    return format(x, 'b').zfill(n)

def srl(s):
    global reg
    rd, rt, sa = tris(s)
    rt_value = reg[int(rt)]
    if rt_value < 0:
        # digits = get_bin(-1 * rt_value, 0)
        bin = get_bin(-1 * rt_value, 31)
        # print(bin)

        arr_bin = np.array(list(bin))
        leng = len(arr_bin)
        for i in range(leng):
            if arr_bin[i] == '0':
                arr_bin[i] = '1'
            else:
                arr_bin[i] = '0'
        re = convert_list_to_string(arr_bin)
        # print(leng)
        # print(re)
        e = int(re, 2) + 1 + 2 ** leng
        reg[int(rd)] = e >> int(sa)
    else:
        reg[int(rd)] = reg[int(rt)] >> int(sa)
    return

def sra(s):
    global reg
    rd, rt, sa = tris(s)
    reg[int(rd)] = reg[int(rt)] >> int(sa)
    return

# def nop(s):
#     return "NOP"


def convert_list_to_string(org_list, seperator=''):
    return seperator.join(org_list)

# if flag == whole, process the whole ins, else just the s ins
def handledata(s):

    if s[0] == "0":
        return int(s,2)
    else:
        arr = np.array(list(s))
        for i in range(1, len(arr)):
            if arr[i] == '0':
                arr[i] = '1'
            else:
                arr[i] = '0'

        full_str = convert_list_to_string(arr[1:])
        # print(full_str)

        result = int(full_str, 2)
        # print(-1 * (result + 1))
        return -1 * (result + 1)
# needs to be refined********
def printmemory(f):
    f.write('\n')
    f.write("Data" + '\n')
    keyset = list(memory.keys())
    length = len(keyset)
    # key = keyset[0]
    times = math.floor(length/8)
    timesplus = math.ceil(length/8)
    for i in range(0, times):

        f.write(str(keyset[8 * i]) + ':' + '\t')
        for j in keyset[8 * i :8 * (i + 1)]:
            if j == keyset[8 * i + 7]:
                f.write(str(memory[j]))
                break
            f.write(str(memory[j]) + '\t')
        f.write('\n')

    if(times != timesplus):
        start = times * 8
        f.write(str(keyset[start]) + ':' + '\t')
        for k in keyset[start, length]:
            if k == length -1:
                f.write(str(memory[k]))
                break
            f.write(str(memory[k]) + '\t')
        f.write('\n')

    f.write('\n')
    return




def printRegister(f):
    global reg
    f.write('\n')
    f.write("Registers" + '\n')

    f.write("R00:" + '\t')
    for i in range(8):
        if i == 7:
            f.write(str(reg[i]))
            break
        f.write(str(reg[i]))
        f.write('\t')
    f.write('\n')
    f.write("R08:" + '\t')
    for i in range(8, 16):
        if i == 15:
            f.write(str(reg[i]))
            break
        f.write(str(reg[i]))
        f.write('\t')
    f.write('\n')
    f.write("R16:" + '\t')
    for i in range(16, 24):
        if i == 23:
            f.write(str(reg[i]))
            break
        f.write(str(reg[i]))
        f.write('\t')
    f.write('\n')
    f.write("R24:" + '\t')

    for i in range(24,32):
        if i == 31:
            f.write(str(reg[i]))
            break
        f.write(str(reg[i]))
        f.write('\t')
    f.write('\n')
    return

def simulator(input):
    global PC
    global Cycle
    global reg
    global memory

    line_num = PC/4 - 63
    f_simu = open("simulation.txt", "w")
    # f_disa = open("disassembly.txt", "r")
    # line = f_disa.readline()
    line = linecache.getline(input, int(line_num))
    f_simu.write("--------------------" + '\n')
    while line:
        inscode = line.strip()
        # print("inscode in simulator and PC")
        # print(inscode)
        # print(PC)

        # print(instr)
        fetchcode = inscode.split('\t')


        opcode = fetchcode[0]
        opcode = opcode[0:6]

        fetchcode = fetchcode[1:]
        # print(fetchcode)

        parsed_instr = searchkey(opcode)
        # print(parsed_instr)
        # print('pased_in======================')
        Cycle = Cycle + 1
        fetch_part1 = convert_list_to_string(fetchcode[0],'')
        fetch_part2 = convert_list_to_string(fetchcode[1], '')
        # print(fetch_part1)
        # print(fetch_part2)

        # print("***************************thsi sis fetch code")
        # print(fetchcode)

        f_simu.write("Cycle " + str(Cycle) + ":" + '\t' + fetch_part1 + '\t' + fetch_part2 + '\n')
        if parsed_instr == "NOP":
            pass
        elif parsed_instr == 'BREAK':
            PC = PC + 4
            printRegister(f_simu)
            printmemory(f_simu)
            break
        elif parsed_instr == "ADD":
            add(inscode)
        elif parsed_instr == "MUL":
            mul(inscode)
        elif parsed_instr == "SUB":
            sub(inscode)
        elif parsed_instr == "AND":
            func_and(inscode)
        elif parsed_instr == "OR":
            func_or(inscode)
        elif parsed_instr == "XOR":
            xor(inscode)
        elif parsed_instr == "NOR":
            nor(inscode)
        elif parsed_instr == "SLT":
            slt(inscode)
        elif parsed_instr == "ADDI":
            addi(inscode)
        elif parsed_instr == "ANDI":
            andi(inscode)
        elif parsed_instr == "ORI":
            ori(inscode)
        elif parsed_instr == "XORI":
            xori(inscode)
        elif parsed_instr == "J":
            line_num = jump(inscode)
            line = linecache.getline(input, int(line_num))
            printRegister(f_simu)
            printmemory(f_simu)
            f_simu.write("--------------------" + "\n")
            continue
        elif parsed_instr == "JR":
            line_num = jr(inscode)
            line = linecache.getline(input, int(line_num))
            printRegister(f_simu)
            printmemory(f_simu)
            f_simu.write("--------------------" + "\n")
            continue
        elif parsed_instr == "BEQ":
            line_num, PC = beq(inscode)
            # print("line num _______________________")
            # print(line_num)
            line = linecache.getline(input, int(line_num))
            printRegister(f_simu)
            printmemory(f_simu)
            f_simu.write("--------------------" + "\n")
            continue
        elif parsed_instr =="BLTZ":
            line_num = bltz(inscode)
            line = linecache.getline(input, int(line_num))
            printRegister(f_simu)
            printmemory(f_simu)
            f_simu.write("--------------------" + "\n")
            continue
        elif parsed_instr == "BGTZ":
            line_num = bgtz(inscode)
            line = linecache.getline(input, int(line_num))
            printRegister(f_simu)
            printmemory(f_simu)
            f_simu.write("--------------------" + "\n")
            continue
        elif parsed_instr == "SW":
            sw(inscode)
        elif parsed_instr == "LW":
            lw(inscode)
        elif parsed_instr == "SLL":
            sll(inscode)
        elif parsed_instr == "SRL":
            srl(inscode)
        elif parsed_instr == "SRA":
            sra(inscode)

        printRegister(f_simu)
        printmemory(f_simu)
        f_simu.write("--------------------" + "\n")

        PC = PC + 4
        line_num = PC / 4 - 63
        line = linecache.getline(input, int(line_num))

    # f_disa.close()
    f_simu.close()




def disassembler(input):
    f_dis = open("disassembly.txt", 'w')
    f_sample = open(input, "r")
    line = f_sample.readline()
    global PC

    while line:
        PC += 4
        inscode = line.strip()
        opcode = inscode[0:6]
        f_dis.write(inscode + '\t' + str(PC) + '\t')
        # f_dis.write('\t')
        # f_dis.write(str(PC) + '\t')
        # f_dis.write('\t')

        parsed_instr = searchkey(opcode)
        if parsed_instr in regset:
            rd, rs, rt = getreg(inscode)
            f_dis.write(parsed_instr + " R"+ rd + ", R" + rs + ", R" + rt)
            f_dis.write('\n')
        elif parsed_instr in immeset:
            rt, rs, imme = getimme(inscode)
            f_dis.write(parsed_instr + " R"+ rt + ", R" + rs + ", #" + imme)
            f_dis.write('\n')
        elif parsed_instr in trisset:
            rd, rt, sa = tris(inscode)
            f_dis.write(parsed_instr + " R"+ rd + ", R" + rt + ", #" + sa)
            f_dis.write('\n')
        elif parsed_instr in bgltzset:
            rs, offset = bgltz(inscode)
            f_dis.write(parsed_instr + " R" + rs + ", " + "#" + offset)
            f_dis.write('\n')
        elif parsed_instr == "J":
            target = jump_code(inscode)
            f_dis.write(parsed_instr + " #" + target)
            f_dis.write('\n')
        elif parsed_instr == "JR":
            rs = jr_code(inscode)
            f_dis.write(parsed_instr + " R" + rs)
            f_dis.write('\n')
        elif parsed_instr == "BEQ":
            rs, rt, offset = beq_code(inscode)
            f_dis.write(parsed_instr + " R" + rs + ", R" + rt + ", #" + offset)
            f_dis.write('\n')
        elif parsed_instr == "BREAK":
            f_dis.write("BREAK")
            f_dis.write('\n')
        elif parsed_instr in slw_set:
            rt, offset, base = swlw(inscode)
            f_dis.write(parsed_instr + " R" + rt + ", " + offset + "(R" + base + ")")
            f_dis.write('\n')
        elif parsed_instr == "NOP":
            f_dis.write("NOP")
            f_dis.write('\n')
        else:
            re = handledata(inscode)
            memory[PC] = re
            f_dis.write(str(re))
            f_dis.write('\n')
        line = f_sample.readline()
    PC = 256
    f_sample.close()
    f_dis.close()

def main(argv):
    input = "disassembly.txt"
    argv = str(argv)
    # print(argv)
    disassembler(argv)
    simulator(input)


if __name__== "__main__":
    # main("sample.txt")
    main(sys.argv[1])

