#! /usr/bin/python

import os;
import sys;
import json;

# stack file format
#
# -------------- # stack delimiter
# 12345AB some   # hex some data
#

def unpack( r ):
	addr = r[0];
	mod	 = r[1];
	proc = r[2];
	return "{0:08x}_{1}_{2}".format( addr, mod, proc );

def main( stack_file ):
	with open( stack_file ) as fd:
		stacks = json.load( fd );
	
	print( "digraph callstack {" );
	pairs = [];
	for stack in stacks:
		prev = None;
		for cur in reversed( stack ):
			if prev != None:
				prev_addr = prev[0];
				cur_addr = cur[0];
				if ( prev_addr, cur_addr ) not in pairs:
					print( "\"{0}\" -> \"{1}\"".format(
							unpack( prev ),
							unpack( cur ) ) );
					pairs.append( ( prev_addr, cur_addr ) );
			prev = cur;
	print( "}" );
	

if __name__ == "__main__":
	if len( sys.argv ) < 2:
		print( "{0} STACK_FILE.json".format( sys.argv[0] ) );
		sys.exit( -1 );
	
	main( sys.argv[1] );
