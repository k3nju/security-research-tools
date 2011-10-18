from immlib import *;
import json;
import traceback as backtrace;

class CallRetHook( LogBpHook ):
	def __init__( self ):
		LogBpHook.__init__( self );
		self.__call_points = {};
		self.__ret_points = {};
	
	def add_call_point( self, addr, asm ):
		self.__call_points[ addr ] = asm;
		self.add( asm, addr );
	
	def add_ret_point( self, addr, asm ):
		self.__ret_points[ addr ] = asm;
		#self.add( asm, addr );

	def run( self, regs ):
		try:
			imm = Debugger();
			thread_id = imm.getThreadId();
			eip = regs[ "EIP" ];
			imm.log( "HIT:%x" % thread_id, address = eip );
		except StandardError as E:
			imm.log( E.message );

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
	except:
		return "Error: Failed parsing callmap file";
	
	# calculate diff between IDA outputs and debugee
	src_imagebage = callmap[ "imagebase" ];
	diff = get_imagebase_diff( loaded_imagebase, callmap[ "imagebase" ] );
	
	# map break points
	hook = CallRetHook();
	import datetime;
	start = datetime.datetime.now();
	for ( call_addr, call_asm, ret_addr, ret_asm ) in callmap[ "callrets" ][:5000]:
		call_addr += diff;
		hook.add_call_point( call_addr, call_asm );
		ret_addr += diff;
		hook.add_ret_point( ret_addr, ret_asm );
	fin = datetime.datetime.now();
	imm.log( repr( fin - start ) );
	imm.log( "Stop" );
	return "SUCCESS";

def main( args ):
	imm = Debugger();
	if len( args ) > 2:
		return "Error: Invalid args. !mapcall <mod_name> <callmap file>";
	
	# !mapcall <mod_name> <callmap file>
	mod_name = args[0].lower();
	callmap_file = args[1];
	try:
		return main_impl( imm, mod_name, callmap_file );
	except Exception as E:
		for line in backtrace.format_exc().split( "\n" ):
			imm.log( line );
		return "Error: %s" % E.message;

