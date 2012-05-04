import sys;
from winappdbg import *;
import pefile;
import threading;

class BPPoints( dict ):
	def __init__( self ):
		super( BPPoints, self ).__init__();
		self.__lock = threading.Lock();
		
	def __setitem__( self, key, value ):
		with self.__lock:
			super( BPPoints, self ).__setitem__( key, value );

	def __getitem__( self, key ):
		with self.__lock:
			return super( BPPoints, self ).__getitem__( key );

BP = BPPoints();

def bp_handler( event ):
	try:
		eip = event.get_thread().get_pc();
		print BP[eip];
	except:
		pass;

class MyEventHandler( EventHandler ):
	def load_dll( self, event ):
		module = event.get_module();
		filename = module.get_filename();
		if filename.lower().startswith( "c:\\program files" ) == False:
			return;

		try:
			pe = pefile.PE( filename );
		except:
			return;

		pid = event.get_pid();
		for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols:
			name = exp.name;
			if name == None:
				continue;
			addr = module.resolve( exp.name );
			if addr == None:
				continue;

			BP[addr] = name;
			event.debug.break_at( pid, addr, bp_handler );

def find_proc( debug, name ):
	debug.system.scan_processes();
	for proc in debug.system.iter_processes():
		filename = proc.get_filename();
		if filename == None:
			continue;
		if filename.lower().endswith( name ):
			return proc;
	return None;
			
def main():
	debug = Debug( MyEventHandler() );
	try:
		proc_name = sys.argv[1];
		proc = find_proc( debug, proc_name );
		if proc == None:
			print( "Not found {0}".format( proc_name ) );
		else:
			print( "Found {0}:{1}. attaching...".format( proc_name, proc.get_pid() ) );
			debug.attach( proc.get_pid() );
			debug.loop();
	except Exception as E:
		print( str( E ) );
	finally:
		debug.stop();

if __name__ == "__main__":
	main();
