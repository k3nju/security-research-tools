#! /usr/bin/python

import os;
import sys;

def read_stack( f ):
	recs = [ i.strip().decode( "utf-8" )
			 for i in open( f, "rb" ).readlines() if len( i.strip() ) >0 ];
	retval = [];
	for i in reversed( recs ):
		parts = i.split();
		last = parts[-1];
		
		pos = None;
		if last.startswith( "(" ):
			pos = last[1:-1];
		elif last.startswith( "0x" ):
			pos = last;
		else:
			continue;
		
		retval.append( '"{0}"'.format( pos ) );

	return retval;

stacks = [];

def main( d ):
	for i in os.listdir( d ):
		if i.endswith( "txt" ) == False:
			continue;
		i = os.path.join( d, i );
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

main( sys.argv[1] );
