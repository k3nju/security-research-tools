from immlib import *;
from immutils import *;

class BackTraceHook( LogBpHook ):
	def __init__( self ):
		#super( BackTraceHook, self ).__init__();
		LogBpHook.__init__( self );
	
	def run( self, regs ):
		try:
			imm = Debugger();
			call_stacks = imm.callStack()
			n = 0;
			frame_low = regs["ESP"];
			for stack in call_stacks:
				proc = stack.getProcedure();
				if proc.startswith( " " ):
					pass;
				else:
					addr = stack.getAddress();
					called_from = stack.getCalledFrom();
					
					imm.log( "[*] %d ----------------------------" % n );
					imm.log( proc, address = regs["EIP"] );
					imm.log( "frame low  : 0x%08x" % frame_low, address = frame_low );
					imm.log( "frame high : 0x%08x" % addr, address = addr );
					imm.log( "Called from : 0x%08x" % called_from, address = called_from );
					
					n += 1;
					frame_low = addr + 4;
		except StandardError, E:
			imm.log( E.message );

def main( args ):
	imm = Debugger();
	func_name = args[0];
	addr = imm.getAddress( func_name );
	if addr == -1:
		return "Invalid address : 0x%08x" % addr;
	hooker = BackTraceHook();
	hooker.add( func_name, addr );
	return "Hook : 0x%08x" % addr;

