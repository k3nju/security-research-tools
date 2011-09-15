from immlib import *;
import json;
import traceback as backtrace;

class CallRetsHook( LogBpHook ):
	def __init__( self, handler ):
		LogBpHook.__init__( self );
		self.__handler = handler;
		
	def run( self, regs ):
		try:
			imm = Debugger();
			thread_id = imm.getThreadId();
			eip = regs[ "EIP" ];
			self.__handler.on_hit( thread_id, eip );
		except StandardError as E:
			imm.log( E.message );

class CallStackManager( object ):
	def __init__( self ):
		self.__call_stacks = {};
		self.__call_points = {};
		self.__ret_points = {};
	
	def add_call_point( self, addr, asm ):
		self.__call_points[ addr ] = asm;
	
	def add_ret_point( self, addr, asm ):
		self.__ret_points[ addr ] = asm;
	
	"""
	def __on_point( self, tid, eip, stacks, points ):
		if tid not in stacks:
			stacks[ tid ] = ( 0, [] );
		asm = points[ eip ];
		nest_count = stacks[ tid ][ 0 ] + 1;
		paragrahp = " " * nest_count;
		stacks[ tid ][0] = nest_count;
		stacks[ tid ][1].append( paragraph + asm );
	"""
	
	def __on_call_point( self, tid, eip ):
		imm = Debugger();
		imm.log( "call: %x:%x" % ( tid, eip ), address = eip );
	
	def __on_ret_point( self, tid, eip ):
		imm = Debugger();
		imm.log( "ret: %x:%x" % ( tid, eip ), address = eip );
	
	def on_hit( self, tid, eip ):
		imm = Debugger();
		imm.log( "%x:%x" % ( tid, eip ) );

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
	manager = CallStackManager();
	callHook = CallRetsHook( manager );
	retHook = CallRetsHook( manager );
	for ( call_addr, call_asm, ret_addr, ret_asm ) in callmap[ "callrets" ]:
		call_addr += diff;
		ret_addr += diff;
		imm.log( repr( call_addr ) );
		callHook.add( call_asm, call_addr );
		retHook.add( ret_asm, ret_addr );
	
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
		for line in backtrace.format_exc().split( "\n" ):
			imm.log( line );
		return "Error: %s" % E.message;

