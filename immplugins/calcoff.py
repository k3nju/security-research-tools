from immlib import *


def main(args):
	imm = Debugger();
	addr = imm.getCurrentAddress()
	mod = imm.getModuleByAddress(addr)
	base_addr = mod.getBaseAddress()
	offset = addr - base_addr;
	print_str = hex(0x10000000 + offset)
	imm.log(print_str)
	return ""
