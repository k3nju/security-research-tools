#! /usr/bin/python

import os;
import sys;

def read_stack( f ):
	recs = [ i.strip().split()[-1].decode( "utf-8" )
			 for i in open( f, "rb" ).readlines() if len( i.strip() ) >0 ];
	retval = [];
	for i in recs:
		parts = i.split();
		l = parts[-1].replace( "0x", "" );
		if l.startswith( "0x" ):
			l = l.replace( "0x", "" );
		elif l.startswith( "(" ):
			l = l[1:-1].split( "+", 2 )[0];
		
		retval.append( '"{0}"'.format( l ) );

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
	for c in reversed( stacks ):
		print( "{0} -> {1};".format( *c ) );
	print( "}" );

main( sys.argv[1] );
