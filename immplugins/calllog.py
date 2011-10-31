from immlib import *;
from immutils import *;
import json;
import idautils;

class CallHook( LogBpHook ):
	def __init__( self ):
		#super( BackTraceHook, self ).__init__();
		LogBpHook.__init__( self );
	
	def run( self, regs ):
		try:
			imm = Debugger();
			call_points = imm.getKnowledge( "call_points" );
			imm.log( "--calllog--" );
			call_stacks = imm.callStack()
			for stack in call_stacks:
				proc = stack.getProcedure();
				if proc.startswith( " " ):
					pass;
				else:
					called_from = stack.getCalledFrom();
					if called_from not in call_points:
						continue;
					call_addr, call_asm = call_points[ called_from ];
					imm.log( "0x{0:08x} {1}".format( call_addr, call_asm ), address = called_from );
		except StandardError, E:
			imm.log( E.message );

def main( args ):
	imm = Debugger();
	addr = int( args[0], 16 );
	callmap_file = args[1];
	
	try:
		with open( callmap_file ) as fd:
			CALLMAP = json.load( fd );
	except:
		return "Error: Failed to read callmap file";
	
	module_name = CALLMAP[ "module_name" ];
	loaded_imagebase = idautils.get_module_base_addr( imm, module_name );
	if loaded_imagebase == None:
		return "Error: Module not found";
	
	hooker = CallHook();
	hooker.add( "callog hook", addr );
	call_points = {};
	diff = idautils.get_imagebase_diff( loaded_imagebase, CALLMAP[ "imagebase" ] );
	for call_addr, call_asm, ret_addr, ret_asm in CALLMAP[ "callrets" ]:
		mapped_call_addr = call_addr + diff;
		imm.log( "mapping %s" % call_asm, address = mapped_call_addr );
		call_points[ mapped_call_addr ] = ( call_addr, call_asm );
	imm.addKnowledge( "call_points", call_points );
	return "Hook : 0x%08x" % addr;


