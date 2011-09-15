from immlib import *;
import json;

class CallHook

def get_module_base_addr( imm, mod_name ):
	mod = None;
	mod_name = mod_name.lower();
	modules = imm.getAllModules();
	for name in modules.keys():
		k = name.lower().split( ".", 2 )[0];
		if k == mod_name:
			mod = modules[name];
			return mod.getBaseAddress();
	return None;

def get_imagebase_diff( mapped_addr, src_addr ):
	diff = 0;
	if src_addr >= mapped_addr:
		diff = src_addr - mapped_addr;
		diff = diff * -1;
	else:
		diff = mapped_addr - src_addr;
	
	return diff;

def main_impl( imm, mod_name, callmap_file ):
	# get loaded imagebase address
	loaded_imagebase = get_module_base_addr( imm, mod_name );
	if loaded_imagebase == None:
		return "Error: Not found %s" % ( mod_name );
	
	# get call map configulations
	callmap = None;
	try:
		with open( callmap_file ) as fd:
			callmap = json.load( fd );
			src_imagebage = callmap[ "imagebase" ];
	except Exception as E:
		return "Error: Failed parsing callmap file";
	
	# calculate diff between IDA outputs and debugee
	diff = get_imagebase_diff( loaded_imagebase, callmap[ "imagebase" ] );
	
	# map break points
	for ( call_addr, call_asm, ret_addr, ret_asm ) in callmap[ "callrets" ]:
		call_addr += diff;
		ret_addr += diff;
		imm.log( call_asm, address = call_addr );
		imm.log( ret_asm, address = ret_addr );
	
	return "SUCCESS";

def main( args ):
	if len( args ) != 2:
		return "Error: Invalid args. !callmap <mod_name> <callmap file>";
	
	imm = Debugger();
	# !mapcall <mod_name> <callmap file>
	mod_name = args[0].lower();
	callmap_file = args[1];
	try:
		return main_impl( imm, mod_name, callmap_file );
	except Exception as E:
		return "Error: %s" % E.message;

