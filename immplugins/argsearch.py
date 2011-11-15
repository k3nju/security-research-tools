from immlib import *;
from immutils import *;
import idautils;


class CallHook( LogBpHook ):
	def __init__( self ):
		LogBpHook.__init__( self );

	def run( self, regs ):
		imm = Debugger();
		imm.log( "---------" );
		hit_count = imm.getKnowledge( "hit_count" );
		imm.log( "hit count: {0}".format( hit_count ) );
		imm.addKnowledge( "hit_count", hit_count + 1, force_add = True );
		
		esp_offset = imm.getKnowledge( "esp_offset" );
		val = "{0:08X}".format( imm.readLong( regs[ "ESP" ] + esp_offset ) );
		imm.log( "Arg value: " + val );
		
		current_func = None;
		last_func = None;
		arg_pos = None;
		call_stacks = imm.callStack();
		
		for stack in call_stacks:
			proc = stack.getProcedure();
			if proc.startswith( " " ):
				if proc.split()[-1] == val:
					last_func = current_func;
					arg_pos = proc;
				else:
					# don't substitute to last_func
					pass;
			else:
				current_func = proc;
				imm.log( proc );
		imm.log( "------" );
		imm.log( last_func );
		imm.log( arg_pos );

def main( args ):
	imm = Debugger();
	hook_point = int( args[0], 16 );
	esp_offset = int( args[1], 16 );
	imm.addKnowledge( "esp_offset", esp_offset, force_add = True );
	imm.addKnowledge( "hit_count", 0, force_add = True );
	
	hooker = CallHook();
	hooker.add( hex( hook_point ), hook_point );
	
	return "SUCCESS";

