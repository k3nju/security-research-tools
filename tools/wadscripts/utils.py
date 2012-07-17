
def find_proc( debug, name ):
	debug.system.scan_processes();
	for proc in debug.system.iter_processes():
		filename = proc.get_filename();
		if filename == None:
			continue;
		if filename.lower().endswith( name ):
			return proc;
	return None;

def get_diff( runtime_addr, static_addr ):
	if static_addr >= runtime_addr:
		diff = static_addr - runtime_addr;
		return diff * -1;
	return runtime_addr - static_addr;

def remap_callmap( callmap, diff ):
	callmap[ "imagebase" ] += diff;
	for callret in callmap[ "callrets" ]:
		callret[0] += diff; # call point
		callret[2] += diff; # ret point
	return callmap;
		
