
def find_proc( debug, name ):
	debug.system.scan_processes();
	for proc in debug.system.iter_processes():
		filename = proc.get_filename();
		if filename == None:
			continue;
		if filename.lower().endswith( name ):
			return proc;
	return None;
