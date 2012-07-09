import sys;
from winappdbg import *;
import utils;
import traceback;
a

class ReadFileHook( EventHandler ):
	apiHooks = {
		"kernel32.dll" : [
			( "ReadFile", 5 ),
			],
		};
	
	def pre_ReadFile( self, event, ra,
					  hFile,
					  lpBuffer,
					  nNumberOfBytesToRead,
					  lpNumberOfBytesRead,
					  lpOverlapped ):
		trace = event.get_thread().get_stack_trace_with_labels();
		print( "-------------------------------------" );
		for i in trace:
			print( "{0:08x} {1}".format( i[0], i[1] ) );

def main():
	debug = Debug( ReadFileHook() );
	try:
		proc_name = sys.argv[1];
		proc = utils.find_proc( debug, proc_name );
		if proc == None:
			print( "Not found {0}".format( proc_name ) );
			sys.exit();
			
		debug.attach( proc.get_pid() );
		debug.loop();
	except Exception as E:
		traceback.print_exc();

if __name__ == "__main__":
	main();

