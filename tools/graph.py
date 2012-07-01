#! /usr/bin/python

import os;
import re;
RE_ENTRY = re.compile( "(.+)\s(.+)\s\((.+)!(.+)\+(.*)\)" );

def read_stack( f ):
	recs = [ i.strip().decode( "utf-8" )
			 for i in open( f, "rb" ).readlines() if len( i.strip() ) >0 ];
	retval = [];
	for i in reversed( recs ):
		parts = i.split();
		( dll, func ) = parts[2][1:-1].split( "!" );
		func = func.split( "+" )[0].replace( "0x", "_" );
		retval.append( dll + "_" + func );

	retval.append( "ReadFile" );
	
	return retval;

stacks = [];
dups = [];

def main( d ):
	for i in os.listdir( d ):
		if i.endswith( "txt" ) == False:
			continue;
		
		s = read_stack( i );
		prev = s[0];
		for addr in s[1:]:
			pair = ( prev, addr );
			if pair not in stacks:
				stacks.append( pair );
			prev = addr;

	print( "digraph callstack {" );
	for c in stacks:
		print( "{0} -> {1};".format( *c ) );
	print( "}" );

main( "./" );
