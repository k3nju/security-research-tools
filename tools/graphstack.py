#! /usr/bin/python

import os;
import sys;
import json;

import graphcolors;

# stack file format
#
# -------------- # stack delimiter
# 12345AB some   # hex some data
#
def conv_str( r ):
	addr = r[0];
	mod	 = r[1];
	proc = r[2];
	return "{0:08x}_{1}_{2}".format( addr, mod, proc );

def read_pairs( stack ):
	stack = stack[:];
	stack.reverse();
	prev = stack[0];
	
	for cur in stack[1:]:
		yield ( prev, cur );
		prev = cur;

def main( stack_file ):
	with open( stack_file ) as fd:
		stacks = json.load( fd );

	# collect call pair count
	call_count = {};
	for stack in stacks:
		for pair in read_pairs( stack ):
			k = ( pair[0][0], pair[1][0] ); # caller and callee addr
			if k in call_count:
				call_count[ k ] += 1;
			else:
				call_count[ k ] = 1;

	# collect modules and set color per modules
	modules_colors = {};
	for stack in stacks:
		for entry in stack:
			mod = entry[1];
			if mod in modules_colors:
				continue;
			modules_colors[ mod ] = graphcolors.get();
	
	# print out
	print( "digraph callstack {" );
	nodes = [];
	for stack in stacks:
		for node in stack:
			node_str = conv_str( node );
			if node_str in nodes:
				continue;
			nodes.append( node_str );
			print(
				"\"{0}\" [ color = \"{1}\" ]".format(
					node_str,
					modules_colors[ node[1] ] ) );
	
	pairs = [];
	for stack in stacks:
		for pair in read_pairs( stack ):
			( caller, callee ) = pair;
			k = ( caller[0], callee[0] );
			
			if k in pairs:
				continue;
			pairs.append( k );
			
			print( "\"{0}\" -> \"{1}\" [label=\"{2}\"]".format(
					conv_str( caller ),
					conv_str( callee ),
					call_count[ k ],
					) );
	print( "}" );

if __name__ == "__main__":
	if len( sys.argv ) < 2:
		print( "{0} STACK_FILE.json".format( sys.argv[0] ) );
		sys.exit( -1 );
	
	main( sys.argv[1] );
