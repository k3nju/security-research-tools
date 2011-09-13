#! /usr/bin/python

import sys;
import re;
import json;

OUTPUT = {};

def split_line( line ):
	line = line.translate( None, "\n\r" );
	line = line.replace( "\t", " " );
	line = re.sub( "\..*text:", "", line );
	return [ i for i in line.split( " " ) if len( i ) > 0 ];


def get_imagebase( fd ):
	while True:
		line = fd.readline();
		if len( line ) == 0:
			return -1
		if line.find( "Imagebase" ) == -1:
			continue;
		items = split_line( line );
		return int( items[-1], 16 );

def get_callret_pairs( fd, libcall_only ):
	callret_pairs = [];
	while True:
		line = fd.readline();
		if len( line ) == 0:
			break;
		if line.find( "call" ) == -1:
			continue;
		
		items = split_line( line );
		if len( items ) < 3:
			sys.stderr.write( "Unkonwn call:%s\n" % line );
			continue;
		if items[1] != "call":
			continue;
		if items[2].find( "ds:" ) == -1 and libcall_only == True:
			continue;
		call_addr = int( items[0], 16 );
		call_asm = " ".join( items[2:] );
		
		line = fd.readline();
		if len( line ) == 0:
			break;
		items = split_line( line );
		ret_addr = int( items[0], 16 );
		ret_asm = " ".join( items[2:] );
		
		callret_pairs.append( ( call_addr, call_asm, ret_addr, ret_asm ) );
	return callret_pairs;


def error( msg ):
	sys.stderr.write( msg + "\n" );
	sys.exit( -1 );

KEY_IMAGEBASE = "imagebase";
KEY_CALLRETS = "callrets";

if __name__ == "__main__":
	if len( sys.argv ) < 2:
		print "$ gencalllist.py <source.lst> [-L (library call only)] ";
		sys.exit( -1 );

	output = {};
	is_libcall_only = "-L" in sys.argv;
	
	with open( sys.argv[1] ) as fd:
		imagebase = get_imagebase( fd );
		if imagebase == -1:
			error( "Imagebase not found" );

		callret_pairs = get_callret_pairs( fd, is_libcall_only );
		if len( callret_pairs ) == 0:
			error( "Callret pairs parse failed" );

		output[ KEY_IMAGEBASE ] = imagebase
		output[ KEY_CALLRETS ] = callret_pairs;

	print json.dumps( output );
