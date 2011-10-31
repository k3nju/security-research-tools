from immlib import *;
from immutils import *;
from collections import defaultdict;

LOG_FILE_DIR = "c:\\tmp\\";

class ReadFileRetHook( LogBpHook ):
	def __init__( self ):
		LogBpHook.__init__( self );
	
	def run( self, regs ):
		imm = Debugger();
		
		size_read = imm.readLong( imm.readLong( regs["ESP"] + 0x10 ) );
		tid = imm.getThreadId();
		
		contexts = imm.getKnowledge( "contexts" );
		current_context = contexts[ tid ].pop();
		imm.addKnowledge( "contexts", contexts, force_add = 1 );
		wcount = imm.getKnowledge( "write_count" );
		imm.addKnowledge( "write_count", wcount + 1, force_add = 1 );
		
		imm.log( "read memory {0:08x},{1}({1:x})".format( current_context, size_read ) );
		buf = imm.readMemory( current_context, size_read );
		filename = LOG_FILE_DIR + "ReadFile_{0}".format( wcount );
		imm.log( "write to {0}".format( filename ) );
		open( filename, "wb" ).write( buf );

class ReadFileHook( LogBpHook ):
	def __init__( self ):
		#super( ReadFileHook, self ).__init__();
		LogBpHook.__init__( self );
	
	def run( self, regs ):
		imm = Debugger();
		buf_addr = imm.readLong( regs["ESP"] + 0x08 );
		#read_size = imm.readLong( regs["ESP"] + 0x0c );
		
		try:
			tid = imm.getThreadId();
			current_context = buf_addr;
			contexts = imm.getKnowledge( "contexts" );
			contexts[ tid ].append( current_context );
			imm.addKnowledge( "contexts", contexts, force_add = 1 );
		except StandardError, E:
			imm.log( E.message );

def main( args ):
	imm = Debugger();
	addr = imm.getAddress( "ReadFile" );
	if addr == -1:
		return "ReadFile not found";
	
	begin_hook = ReadFileHook();
	begin_hook.add( "ReadFile", addr );
	imm.log( "ReadFileHook is set at {0:08x}".format( addr ), address = addr );
	
	ret_hook = ReadFileRetHook();
	n = 0;
	for ret_addr in imm.getFunctionEnd( addr ):
		ret_hook.add( "ReadFileRet[{0}]".format( n ), ret_addr );
		imm.log( "ReadFileRetHook is set at {0:08x}".format( ret_addr ), address = ret_addr );
	
	imm.forgetKnowledge( "contexts" );
	imm.addKnowledge( "contexts", defaultdict( list ) );
	imm.forgetKnowledge( "write_count" );
	imm.addKnowledge( "write_count", 0 );
	return "SUCCESS";

