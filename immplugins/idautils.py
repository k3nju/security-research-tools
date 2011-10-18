
def get_imagebase_diff( runtime_addr, src_addr ):
	diff = 0;
	if src_addr >= runtime_addr:
		diff = src_addr - runtime_addr;
		diff = diff * -1;
	else:
		diff = runtime_addr - src_addr;
	
	return diff;

def get_module_base_addr( imm, mod_name ):
	mod = None;
	mod_name = mod_name.lower();
	modules = imm.getAllModules();
	for name in modules.keys():
		k = name.lower().split( ".", 2 )[0];
		if k == mod_name:
			mod = modules[name];
			return mod.getBaseAddress();
	return None;

def main(args):
	return "SUCCESS";