#! /usr/bin/python
# -*- coding:utf-8 -*-

import sys;
import re;
import json;

KEY_MOD_NAME  = "module_name";
KEY_IMAGEBASE = "imagebase";
KEY_PROCS     = "procs";
KEY_CALLRETS  = "callrets";

RE_PROC = re.compile( b"call ([^ ]+)" );


def split_line( line ):
	"""
	b'.itext:10001016\t\t\tcall\func' -> [ "10001016", "call", "func" ]
	"""
	line = line.replace( b"\t", b" " );
	line = re.sub( b"^\..{0,1}text:", b"", line );
	return [ i for i in line.split( b" " ) if len( i ) > 0 ];

def get_module_name( fd ):
	while True:
		line = fd.readline().strip();
		if len( line ) == 0:
			return None;
		if line.find( b"File Name" ) == -1:
			continue;
		items = split_line( line );
		return items[-1].split( b"\\" )[-1].decode().lower();

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
	proc_name = None;
	proc_start = 0;
	
	while True:
		line = fd.readline().strip();
		if len( line ) == 0:
			break;
		
		# find procedure start
		if line.find( b"proc near" ) != -1:
			items = split_line( line );
			proc_start = int( items[0], 16 );
			proc_name = items[1].lower();

		# find procedure end
		elif line.endswith( b"endp" ):
			items = split_line( line );
			proc_end = int( items[0], 16 );
			procs.append( ( proc_start,
							proc_end,
							proc_name.decode() ) );
			
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
			call_proc = RE_PROC.search( call_asm ).group( 1 ).decode();
			
			# ret porint
			line = fd.readline().strip();
			if len( line ) == 0:
				break;
			items = split_line( line );
			ret_addr = int( items[0], 16 );
			
			callrets.append( ( call_addr,
							   call_proc,
							   ret_addr ) );
	
	return ( procs, callrets );

def error( msg ):
	sys.stderr.write( msg + "\n" );
	sys.exit( -1 );

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
