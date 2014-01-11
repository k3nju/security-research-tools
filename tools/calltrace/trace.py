#
# Using hook model.
# Example of aquiring calltrace.
# 

import sys
import os
import traceback
import threading
from collections import namedtuple, defaultdict
import traceback
import json

from winappdbg import *
import pefile

# target exe path
EXE_PATH = "c:\\hoge.exe";
# list of calltrace logs
CALLTRACE_LOG = []

# Hook class.
# This example hooks ReadFile
class MyEventHandler(EventHandler):
	apiHooks = \
	{
	"kernel32.dll" : {
	("ReadFile", (win32.HANDLE, win32.LPVOID, win32.DWORD, win32.LPVOID, win32.LPVOID)),
	}
	}

	# Hook handler
	def pre_ReadFile(self, event, ra, *a):
		# Read stack and resolve return addresses.
		# This trivial method may give a false negative
		# if addresses are stacked on as variables.
		trace = []
		th = event.get_thread()
		proc = event.get_process()
		st = th.peek_stack_dwords(1024)
		for v in st:
			if proc.is_address_executable(v) == False:
				continue
			mod = proc.get_module_at_address(v)
			if mod == None:
				continue
			name = os.path.basename(mod.get_filename())
			base = mod.get_base()
			trace.append((name, base, v)) # module name, runtime module base address, return address
			
		CALLTRACE_LOG.append(trace)

def main(proc_name):
	dbg = Debug(MyEventHandler())
	dbg.system.request_debug_privileges()
	dbg.system.scan_processes()
	
	founds = dbg.system.find_processes_by_filename(proc_name);
	if len(founds) == 0:
		# if no process found, create new process
		dbg.execl(" ".join([EXE_PATH, "some arg"])).get_pid()
	else:
		# if processes found, attach them
		for (proc, name) in founds:
			dbg.attach(proc.get_pid())
	try:
		dbg.loop()
	except:
		traceback.print_exc()
	dbg.stop()
	
	json.dump(READFILE_LOG,open("c:\\tracelog.json","w"))


if __name__ == "__main__":	
	main(os.path.basename(EXE_PATH))


