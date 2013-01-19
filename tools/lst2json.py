#! /usr/bin/python
# -*- coding:utf-8 -*-

import sys;
import re;
import json;
import traceback;

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

def tab2sp( line ):
	return line.strip().replace( b"\t", b" " );

def get_module_name( fd ):
	while True:
		line = tab2sp( fd.readline() );
		if len( line ) == 0:
			return None;
		if line.find( b"File Name" ) == -1:
			continue;
		items = split_line( line );
		return items[-1].split( b"\\" )[-1].decode().lower();

def get_imagebase( fd ):
	while True:
		line = tab2sp( fd.readline() );
		if len( line ) == 0:
			return -1
		if line.find( b"Imagebase" ) == -1:
			continue;
		items = split_line( line );
		return int( items[-1], 16 );

def read_proc( fd ):
	lines = [];
	
	# find "proc near"
	while True:
		line = tab2sp( fd.readline() );
		if len( line ) == 0:
			break;
		
		if line.find( b"proc near" ) != -1:
			lines.append( line );
			break;
	
	if len( lines ) == 0:
		return None;

	# find "endp"
	while True:
		line = fd.readline();
		if len( line ) == 0:
			break;

		lines.append( line );
		
		if line.find( b"endp" ) != -1:
			break;
	
	return lines;

def get_procs_and_callrets( fd, libcall_only ):
	procs = [];
	callrets = [];

	while True:
		proc_lines = read_proc( fd );
		if proc_lines == None:
			break;
		
		# add procs

		# get proc head
		head  = proc_lines[0];
		parts = split_line( head );
		start = int( parts[0], 16 );
		name  = parts[1] # proc name
		
		# get proc tail
		tail  = proc_lines[-1];
		parts = split_line( tail );
		end   = int( parts[0], 16 );
		
		procs.append( ( start, end, name.decode() ) );
		
		# add callrets
		for i in range( 0, len( proc_lines ) ):
			# call point
			line = proc_lines[i];
			if line.find( b"call" ) == -1:
				continue;
			
			parts = split_line( line );
			if parts[2].find( b"ds:" ) == -1 and libcall_only == True:
				continue;
			
			call_addr = int( parts[0], 16 );
			call_proc = RE_PROC.search( b" ".join( parts[1:] ) ).group( 1 ).decode();
			
			# ret point
			i += 1;
			line = proc_lines[i];
			parts = split_line( head );
			ret_addr = int( parts[0], 16 );

			callrets.append( ( call_addr, call_proc, ret_addr ) );

	return ( procs, callrets );

def error( msg ):
	sys.stderr.write( msg + "\n" );
	sys.exit( -1 );

if __name__ == "__main__":
	if len( sys.argv ) < 2:
		print( "$ {0} <source.lst> [-L (library call only)]".format( sys.argv[0] ) );
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
