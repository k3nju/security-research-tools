#! /usr/bin/env python
# -*- coding:utf-8 -*-

import re
import traceback
from collections import namedtuple

RE_STACK_DEPTH = re.compile(b"(\d|[A-F]){3}")
RE_PROC_NEAR = re.compile(b"proc\s+near")
# CallRet defines lines of codes where calling function and returning from it
CallRet = namedtuple("CallRet", ["caddr", "dst_name", "raddr"])
# Proc is abstraction of function appeared in disassembly
Proc = namedtuple("Proc", ["addr", "name"])


def parse_parts(line):
	return [i for i in line.strip().replace(b"\t", b" ").split(b" ") if len(i) > 0]

class ProcSet:
	def __init__(self):
		self.__addrs_names = {}
		self.__names_addrs = {}

	def add(self, addr, name):
		self.__addrs_names[addr] = name
		self.__names_addrs[name] = addr

	def find_by_name(self, name):
		# returns "string" or None
		return self.__names_addrs.get(name)

	def find_by_addr(self, addr):
		return self.__addrs_names.get(addr)

	def __iter__(self):
		for addr in sorted(self.__addrs_names):
			#yield (addr, self.__addrs_names[addr])
                        yield Proc(addr, self.__addrs_names[addr])

	def update_addr_offset(self, offset):
		# update addrs_names
		new = {}
		for addr in self.__addrs_names:
			new[addr + offset] = self.__addrs_names[addr]
		self.__addrs_names = new

		# update names_addrs
		for name in self.__names_addrs:
			self.__names_addrs[name] += offset
			

class CallRetSet:
	def __init__(self):
		# just implement ret addr mapping.
		self.__raddrs_map = {
			# key: raddr
			# value: (caddr, name)
		}

	def add(self, caddr, name, raddr):
		self.__raddrs_map[raddr] = (caddr, name)

	def find_by_ret_addr(self, raddr):
		return self.__raddrs_map.get(raddr)

	def __iter__(self):
		# sort by caddr. not raddr
		for item in sorted(self.__raddrs_map.items(), key=lambda i:i[1][0]):
			#yield (item[1][0], item[1][1], item[0]) # (caddr, "function name", raddr)
                        yield CallRet(item[1][0], item[1][1], item[0])

	def update_addr_offset(self, offset):
		new = {}
		for raddr in self.__raddrs_map:
			v = self.__raddrs_map[raddr]
			new[raddr + offset] = (v[0] + offset, v[1])
		self.__raddrs_map = new

class LstFile:
	def __init__(self, filename):
		self.__fd = open(filename, "rb")
		self.__imagebase = None
		self.__module_name = None
		self.__proc_set = ProcSet()
		self.__callret_set = CallRetSet()
		self.__call_parts = None
		self.__handlers = [
			self.__find_module_name,
			self.__find_imagebase,
			self.__find_proc,
			self.__find_callret,
			]

	@property
	def imagebase(self):
		return self.__imagebase

	@property
	def module_name(self):
		return self.__module_name

	@property
	def proc_set(self):
		return self.__proc_set

	@property
	def callret_set(self):
		return self.__callret_set
	
	def parse(self):
		for line in self.__fd:
			for handler in self.__handlers:
				try:
					handler(line)
				except Exception as E:
					traceback.print_exc()
					
	def __find_module_name(self, line):
		# .text:10001000	; File Name   :	C:\Program Files\Hoge\Hige.dll
		if line.find(b"File Name") == -1:
			return

		self.__module_name = parse_parts(line)[-1].split(b"\\")[-1]
		# removing me in a "for loop" againt list that holds me is ok
		self.__handlers.remove(self.__find_module_name)

	def __find_imagebase(self, line):
		# .text:10001000	; Imagebase   :	10000000
		if line.find(b"Imagebase") == -1:
			return
		self.__imagebase = int(parse_parts(line)[-1], 16)
		self.__handlers.remove(self.__find_imagebase)

	def __find_proc(self, line):
		# .text:100013B2	hogehoge_111 proc	near
		if RE_PROC_NEAR.search(line) is None:
			return
		
		parts = parse_parts(line)
		unused, addr = parts[0].split(b":", 2)
		self.__proc_set.add(int(addr, 16), parts[1]) # (addr, "function name")

	def __find_callret(self, line):
		parts = parse_parts(line)
		# remove stack position if it exists.
		# ex. .text:10000000 012 call hoge -> .text:10000000 call hoge
		#                    ^^^remove this
		
		#  ['.text:10000000', '012', 'call', 'hoge']
		if len(parts) >= 2 and RE_STACK_DEPTH.search(parts[1]):
			parts.remove(parts[1]);

		# skip empty line
		if len(parts) <= 1:
			return
		
		# first, check given line is ret point or not
		# taking care of cascade calls like below
		#
		# .text:10000000 call hoge
		# .text:10000005 call hige <- this line is ret point from hoge and new call point
		if self.__call_parts != None:
			# __call_parts != None means that given line is return points
			#  from previous call
			
			# .text:1000123A	mov	esi, eax
			# 0 : "section name":"address"
			unused, addr = parts[0].split(b":", 2)
			
			self.__callret_set.add(
				int(self.__call_parts[0], 16), # call addr
				self.__call_parts[1], # dst function name
				int(addr, 16),        # ret addr
				)

			self.__call_parts = None

		#  ['.text:10000000', 'call', 'hoge']
		if line.find(b"call") != -1 and parts[1] == b"call":
			# ex1.|.text:10001234	call	hogehoge_111
			# ex2.|.text:10001234	call	dword ptr [esi+10h] ; comment
			# 0 : "section name":"address"
			# 2-: function name
			unused, addr = parts[0].split(b":", 2)
			asm = b" ".join(parts[2:]).split(b";")[0];
			self.__call_parts = (addr, asm) # (addr, "function name")

	def update_base_addr(self, addr):
		offset = addr - self.imagebase
		self.__imagebase += offset
		self.__proc_set.update_addr_offset(offset)
		self.__callret_set.update_addr_offset(offset)

	def dump_procs(self):
		for i in self.proc_set:
			print("{0:08x} {1}".format(*i))
			
	def dump_callrets(self):
		callrets = self.callret_set
		for i in callrets:
			print("{0:08x} {1} {2:08x}".format(*i))
		

if __name__ == "__main__":
	lf = LstFile("/tmp/some.lst")
	lf.parse()
	#lf.update_base_addr(0x00aa0000);
	print(lf.module_name)
	print(lf.imagebase)
	#lf.dump_procs()
	lf.dump_callrets()
	
