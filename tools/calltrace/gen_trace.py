#! /usr/bin/env python

import os;
import sys;
import json;
#import argparse;

import lstparse;

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



if __name__ == "__main__":
	# usage: python gen_trace.py "path to callstack.json" "path to directory of lstfiles"
	callstack_json_file = sys.argv[1];
	lstfiles_dir = sys.argv[2];
	
	call_stack_set = CallStackSet(callstack_json_file)
	lstfiles = load_lstfiles(lstfiles_dir)

	# update base address for each lstfiles
	# and map lstfiles
	lstfile_map = {}
	for lstfile in lstfiles:
		name = lstfile.module_name;
		name = name.lower().decode()
		base_addr = call_stack_set.get_base_addr_by_module_name(name)
		if base_addr == None:
			continue;
		lstfile.update_base_addr(base_addr)

		lstfile_map[name] = lstfile;

		print( lstfile.callret_set);
		for _, _, i in lstfile.callret_set:
			print(hex(i))

	raise Exception("hoge")

	# render call stack for each
	for callstack in call_stack_set.get_callstacks():
		# traverse callstack
		print("==========================================");
		for mod_name, _unused, ret_addr in callstack:
			if mod_name not in lstfile_map:
				continue;

			# find lstfile by corresponding module name
			lstfile = lstfile_map[mod_name]
			e = lstfile.callret_set.find_by_ret_addr(ret_addr)
			if e == None:
				continue
			
			call_addr, func_name = e
			print("{0}.{1}".format(mod_name, func_name));
			
				
				
	
