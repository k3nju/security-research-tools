#! /usr/bin/python

import sys;
import re;
import json;

OUTPUT = {};

def split_line( line ):
	line = line.translate( None, b"\n\r" );
	line = line.replace( b"\t", b" " );
	line = re.sub( b"\..*text:", b"", line );
	return [ i for i in line.split( b" " ) if len( i ) > 0 ];

def get_module_name( fd ):
	while True:
		line = fd.readline().strip();
		if len( line ) == 0:
			return None;
		if line.find( b"File Name" ) == -1:
			continue;
		items = split_line( line );
		return items[-1].split( b"\\" )[-1].decode();

def get_imagebase( fd ):
	while True:
		line = fd.readline().strip();
		if len( line ) == 0:
			return -1
		if line.find( b"Imagebase" ) == -1:
			continue;
		items = split_line( line );
		return int( items[-1], 16 );

def get_procs_and_callrets( fd, libcall_only ):
	procs = [];
	callrets = [];
	
	while True:
		line = fd.readline().strip();
		if len( line ) == 0:
			break;
		
		# find procedure
		if line.endswith( b"proc near" ):
			items = split_line( line );
			proc_addr = int( items[0], 16 );
			proc_name = items[1];
			procs.append( proc_name.decode() );
			
		# find call and ret point
		elif line.find( b"call" ) != -1:
			items = split_line( line );

			# validations
			if len( items ) < 3:
				sys.stderr.write( b"Unkonwn call:%s\n" % line );
				continue;
			if items[1] != b"call":
				continue;
			if items[2].find( b"ds:" ) == -1 and libcall_only == True:
				continue;

			# call point
			call_addr = int( items[0], 16 );
			call_asm = b" ".join( items[1:] );
			
			# ret porint
			line = fd.readline().strip();
			if len( line ) == 0:
				break;
			items = split_line( line );
			ret_addr = int( items[0], 16 );
			#ret_asm = b" ".join( items[1:] );
			
			callrets.append( ( call_addr,
							   call_asm.decode(),
							   ret_addr ) );
	
	return ( procs, callrets );

def error( msg ):
	sys.stderr.write( msg + "\n" );
	sys.exit( -1 );

KEY_MOD_NAME  = "module_name";
KEY_IMAGEBASE = "imagebase";
KEY_PROCS     = "procs";
KEY_CALLRETS  = "callrets";

if __name__ == "__main__":
	if len( sys.argv ) < 2:
		print( "$ gencalllist.py <source.lst> [-L (library call only)] " );
		sys.exit( -1 );

	output = {};
	is_libcall_only = "-L" in sys.argv;
	
	with open( sys.argv[1], "rb" ) as fd:
		mod_name = get_module_name( fd );
		if mod_name == None:
			error( "Module name not found" );
		
		imagebase = get_imagebase( fd );
		if imagebase == -1:
			error( "Imagebase not found" );

		( procs, callrets ) = get_procs_and_callrets( fd, is_libcall_only );
		
		output[ KEY_MOD_NAME ]  = mod_name;
		output[ KEY_IMAGEBASE ] = imagebase;
		output[ KEY_PROCS ]     = procs;
		output[ KEY_CALLRETS ]  = callrets;
		
	print( json.dumps( output ) );
