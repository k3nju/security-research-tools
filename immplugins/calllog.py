from immlib import *;
from immutils import *;
import json;
import idautils;

CALL_POINTS = {};

class CallHook( LogBpHook ):
	def __init__( self ):
		#super( BackTraceHook, self ).__init__();
		LogBpHook.__init__( self );
	
	def run( self, regs ):
		try:
			imm = Debugger();
			imm.log( "--calllog start--" );
			call_stacks = imm.callStack()
			imm.log( "stack len:%d" % len( call_stacks ) );
			for stack in call_stacks:
				proc = stack.getProcedure();
				if proc.startswith( " " ):
					pass;
				else:
					called_from = stack.getCalledFrom();
					if called_from not in CALL_POINTS:
						continue;
					imm.log( "%08x:%s" % CALL_POINTS[ called_from ] );
		except StandardError, E:
			imm.log( E.message );
		imm.log( "--call log fin--" );

def main( args ):
	imm = Debugger();
	func_name = args[0];
	image_name = args[1];
	callmap_file = args[2];
	
	loaded_imagebase = idautils.get_module_base_addr( imm, image_name );
	if loaded_imagebase == None:
		return "Error: Module not found";
	
	addr = imm.getAddress( func_name );	
	if addr == -1:
		return "Invalid address : 0x%08x" % addr;
	hooker = CallHook();
	hooker.add( func_name, addr );
	
	try:
		with open( callmap_file ) as fd:
			CALLMAP = json.load( fd );
	except:
		return "Error: Failed to read callmap file";
	
	diff = idautils.get_imagebase_diff( loaded_imagebase, CALLMAP[ "imagebase" ] );
	
	for call_addr, call_asm, ret_addr, ret_asm in CALLMAP[ "callrets" ]:
		mapped_call_addr = call_addr + diff;
		imm.log( "mapping %s" % call_asm, address = mapped_call_addr );
		CALL_POINTS[ mapped_call_addr ] = ( call_addr, call_asm );
	
	return "Hook : 0x%08x" % addr;


