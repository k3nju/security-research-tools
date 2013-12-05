#! /usr/bin/env python
# -*- coding:utf-8 -*-

import os

def parse_parts(line):
	return line.strip().replace(b"\t", b" ").split(b" ")

class LstFile:
	def __init__(self, filename):
		self.__fd = open(filename, "rb")
		self.__filename = None
		self.__imagebase = None
		self.__procs = []
		self.__callrets = []
		self.__call_line = None
		self.__ret_line = None
		self.__handlers = [
			self.__find_filename,
			self.__find_imagebase,
			self.__find_proc,
			#lambda *a: self.__find_callrets(*a),
			]
	
	def parse(self):
		for line in self.__fd:
			for handler in self.__handlers:
				handler(line)

	def __find_filename(self, line):
		# .text:10001000	; File Name   :	C:\Program Files\Hoge\Hige.dll
		if line.find(b"File Name") == -1:
			return

		self.__filename = parse_parts(line)[-1].split(b"\\")[-1]
		# removing me in a "for loop" againt list that holds me is ok
		self.__handlers.remove(self.__find_filename)

	def __find_imagebase(self, line):
		# .text:10001000	; Imagebase   :	10000000
		if line.find(b"Imagebase") == -1:
			return
		self.__imagebase = int(parse_parts(line)[-1], 16)
		self.__handlers.remove(self.__find_imagebase)

	def __find_proc(self, line):
		# .text:100013B2	hogehoge_111 proc	near
		if line.find(b"proc near") == -1:
			return

		parts = parse_parts(line)
		# -1 : near
		# -2 : proc
		# -3 : "function name"
		# -4 : "section name":"address"
		unused, addr = parts[-4].split(b":", 2)
		self.__procs.append((int(addr, 16), parts[-3]))

	def __find_callrets(self, line):
		if line.find(b"call") != -1:
			# .text:10001234	call	hogehoge_111
			parts = parse_parts(line)
			# -1 : "function name"
			# -2 : call
			# -3/0 : "section name":"address"
			unused, addr = parts[0].split(b":", 2)
			self.__call_line = (addr, parts[-1])
			return # must return
		elif self.__call_line != None:
			# .text:1000123A	mov	esi, eax
			# 0 : "section name":"address"
			unused, addr = parts[0].split(b":", 2)
			self.__callrets.append(
				(self.__call_line[0], # call addr
				 self.__call_line[1], # call function name
				 int(addr, 16),)
			)

			self.__call_parts = None
			
		

	def dump(self):
		for i in self.__procs:
			print(i)
		

if __name__ == "__main__":
	lf = LstFile("./some.lst")
	lf.parse()
	lf.dump()
