#! /usr/bin/env python

import os;
import sys;
import json;
import argparse;
import re;

import lstparse;


SUPPRESS_DLLS = [
	# system
	"ntd.dll",
	"user32.dll",
	"comdlg32.dll",
	"comctl32.dll",
	"gdi32.dll",
	"msvcrt.dll",
	"msvcr90.dll",
	"windowscodecs.dll",

	# others
	"libsvn_tsvn32.dll",
	];

class CallStackSet:
	def __init__(self, callstack_json_file):
		with open(callstack_json_file) as fd:
			self.__callstacks = []
			for callstack in json.load(fd):
				new = []
				for name, base_addr, ret_addr in callstack:
					new.append((name.lower(), base_addr, ret_addr));
				self.__callstacks.append(new)

		self.__modules = {}
		self.__listup_modules();

	def __listup_modules(self):
		# format of callstack is
		# callstacks = [
		#   [ entry, entry, entry, ... ], # call stack of first call
		#   [ entry, entry, entry, ... ], # call stack of second call
		# ]
		#
		# format of entry is
		# ["module name", "module base addr at runtime", "return addr"]

		mods = set([]);
		
		for entries in self.__callstacks:
			for name, base_addr, _unused in entries:
				mods.add((name.lower(), base_addr));

		for i in mods:
			name, base_addr = i[0], i[1];
			if name in self.__modules:
				raise Exception("module:{0} is duplicated. This module may be reloaded");

			self.__modules[name] = base_addr;

	def get_base_addr_by_module_name(self, name):
		name = name.lower()
		if name not in self.__modules:
			return None
		return self.__modules[name]

	def get_callstacks(self):
		for callstack in self.__callstacks:
			# return "return addresses"
			yield (i for i in callstack)
		
def load_lstfiles(lstfile_dir):
	lstfiles = []
	
	for r, ds, fs in os.walk(lstfile_dir):
		for f in fs:
			if f.endswith("lst") == False:
				continue;
			lstfile = lstparse.LstFile(os.path.join(r,f))
			lstfile.parse();
			lstfiles.append(lstfile)
	
	return lstfiles

def print_text(callstack_set, lstfile_map):
	# render call stack for each
	for callstack in callstack_set.get_callstacks():
		# traverse callstack
		print("==========================================");
		for mod_name, _unused, ret_addr in callstack:
			if mod_name not in lstfile_map:
				print("Unknown_{0}_ret_{1:08X}".format(mod_name, ret_addr));
			else:
				# find lstfile by corresponding module name
				lstfile = lstfile_map[mod_name]
				e = lstfile.callret_set.find_by_ret_addr(ret_addr)
				if e == None:
					# may be, not return address but just a value.
					continue
				
				call_addr, func_name = e
				print("{0} 0x{1:08X} {2}".format(mod_name, call_addr, func_name.decode()));

def print_dot(callstack_set, lstfile_map):
	def str_node(s):
		return re.sub("\+|\.|\:|\[|\]|(\s+)", "_", s);
	
	call_set = set([]);
	for callstack in callstack_set.get_callstacks():
		callstack = list(callstack)
		callstack.reverse()
		caller_dll = ""
		prev_suppressed = None;
		caller = "root"
		for mod_name, _unused, ret_addr in callstack:
			if mod_name == caller_dll and mod_name in SUPPRESS_DLLS:
				suppressed = "SUPPRESSED_{0}".format(str_node(mod_name));
				call_set.add("{0} -> SUPRESSED_{1}".format(str_node(caller), suppressed));
				prev_suppressed = suppressed;
				continue;

				
			
			if prev_suppressed != None:
				callee = prev_suppressed;
			elif mod_name not in lstfile_map:
				callee = "Unknown_{0}_ret_{1:08X}".format( mod_name, ret_addr)
			else:
				lstfile = lstfile_map[mod_name]
				e = lstfile.callret_set.find_by_ret_addr(ret_addr)
				if e == None:
					continue
				
				call_addr, func_name = e
				callee = "{0}_{1:08X}_{2}".format(
					mod_name,
					call_addr,
					func_name.decode());
			
			call_set.add("{0} -> {1}".format(str_node(caller), str_node(callee)))
			caller = callee
			caller_dll = mod_name;
			

	print("digraph callstack {")
	for call in call_set:
		print(call)
	print("}")

def main(callstack_json_file, lstfiles_dir, dot):
	callstack_set = CallStackSet(callstack_json_file)
	lstfiles = load_lstfiles(lstfiles_dir)

	# update base address for each lstfiles
	# and map lstfiles
	lstfile_map = {}
	for lstfile in lstfiles:
		name = lstfile.module_name;
		name = name.lower().decode()
		base_addr = callstack_set.get_base_addr_by_module_name(name)
		if base_addr == None:
			continue;
		
		lstfile.update_base_addr(base_addr)
		lstfile_map[name] = lstfile;

	if dot == None:
		print_text(callstack_set, lstfile_map);
	else:
		print_dot(callstack_set, lstfile_map);

if __name__ == "__main__":
	# usage: python gen_trace.py --cs "path to callstack.json" --lstdir "path to directory of lstfiles"
	parser = argparse.ArgumentParser();
	parser.add_argument("--cs", dest = "cs", required = True); # path to callstack json file
	parser.add_argument("--lstdir", dest = "lstdir", required = True); # path to directory of lstfiles
	#parser.add_argument("--all_cs", dest = "all_cs", default = False, action = "store_true");
	parser.add_argument("--dot", dest = "dot", default = None, action = "store_true" ); # print as dot file format

	args = parser.parse_args();

	main(args.cs, args.lstdir, args.dot);
	
	
	
			

				
	
