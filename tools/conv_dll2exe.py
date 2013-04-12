#! /usr/bin/python

import sys;
import pefile;
import argparse;

#------------------// constants
DLL_CHAR = 0x200; # DLL characteristics


#------------------// functions
def get_entry_point_by_name( pe, name ):
	for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols:
		if exp.name != name :
			continue;
		return exp.address;
	return -1;

#------------------// main
parser = argparse.ArgumentParser(
	description = "Convert dll to executable"
	);
parser.add_argument( "dll_file" );
parser.add_argument( "entry_point" );
parser.add_argument( "-rva", dest = "rva", action="store_true" );
parser.add_argument( "-out", dest = "pe_file", default = None );

args = parser.parse_args();
pe = pefile.PE( args.dll_file );
new_entry_point = 0;

# get new entry point
if args.rva == False:
	new_entry_point = get_entry_point_by_name( pe, args.entry_point );
	if new_entry_point == -1:
		print(
			"[!] Error: not found exported function: {0}".format(
				args.entry_point
				)
			);
		sys.exit( -1 );
else:
	new_entry_point = int( args.entry_point, 16 );

# reset entry point
pe.OPTIONAL_HEADER.AddressOfEntryPoint = new_entry_point;	
# reset chars
pe.FILE_HEADER.Characteristics -= DLL_CHAR;

# write out
if args.pe_file != None:
	pe.write( args.pe_file );
else:
	pe.write( args.dll_file + ".ex_" );
	


