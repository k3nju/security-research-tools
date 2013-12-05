#! /usr/bin/env python
# -*- coding:utf-8 -*-

import os

def parse_parts(line):
	return line.strip().replace(b"\t", b" ").split(b" ")

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
			yield (addr, self.__addrs_names[addr])

class CallRetSet:
	def __init__(self):
		# just implement ret addr mapping.
		self.__raddrs_map = {}

	def add(self, caddr, name, raddr):
		self.__raddrs_map[raddr] = (caddr, name)

	def find_by_ret_addr(self, raddr):
		return self.__raddrs_map.get(raddr)

	def __iter__(self):
		# sort by caddr. not raddr
		for item in sorted(self.__raddrs_map.items(), key=lambda i:i[1][0]):
			yield (item[1][0], item[1][1], item[0]) # (caddr, "function name", raddr)
			

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
				except:
					pass

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
		parts = parse_parts(line)
		# -1 : near
		# -2 : proc
		# -3 : "function name"
		# -4 : "section name":"address"
		if line.find(b"proc near") == -1 or (parts[-2], parts[-1]) != (b"proc", b"near"):
			return
		
		unused, addr = parts[-4].split(b":", 2)
		self.__proc_set.add(int(addr, 16), parts[-3]) # (addr, "function name")

	def __find_callret(self, line):
		parts = parse_parts(line)
		# first, check given line is ret point or not
		# taking care of cascade calls like below
		#
		# .text:10000000  call hoge
		# .text:10000005  call hige <- this line is ret point from hoge and new call point
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
			
		if line.find(b"call") != -1 and parts[-2] == b"call":
			# .text:10001234	call	hogehoge_111
			# -1 : "function name"
			# -2 : call
			# -3/0 : "section name":"address"
			unused, addr = parts[0].split(b":", 2)
			self.__call_parts = (addr, parts[-1]) # (addr, "function name")
			

	def dump_procs(self):
		for i in self.proc_set:
			print(i)
			
	def dump_callrets(self):
		callrets = self.callret_set
		for i in callrets:
			print(i)
		

if __name__ == "__main__":
	lf = LstFile("/tmp/some.lst")
	lf.parse()
	lf.dump_procs()
	lf.dump_callrets()
