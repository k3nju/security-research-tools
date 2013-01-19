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

def main( stack_file, root_dir, name ):
	with open( stack_file ) as fd:
		stacks = json.load( fd );

	# collect modules and set color per modules
	modules_colors = {};
	for stack in stacks:
		for entry in stack:
			mod = entry[1];
			if mod in modules_colors:
				continue;
			modules_colors[ mod ] = graphcolors.get();

	# generate dot files
	dst_dir = os.path.join( root_dir, name );
	if os.path.exists( dst_dir ) == False:
		os.path.mkdir( dst_dir );
	dot_files = [];
	no = 0;
	for stack in stacks:
		dst_file = os.path.join( dst_dir, str( no ) ) + ".dot";
		with open( dst_file, "wb" ) as fd:
			fd.write( b"digraph callstack {" );
			fd.write( b"graph [rankdir = LR];" );
			
			# define node color
			nodes = [];
			for node in stack:
				node_str = conv_str( node );

				if node_str in nodes:
					continue;
				nodes.append( node_str );

				fd.write(
					"\"{0}\" [ color = \"{1}\" ]".format(
						node_str,
						modules_colors[node[1]] ).encode() );

			# write node direction
			for pair in read_pairs( stack ):
				( caller, callee ) = pair;
				k = ( caller[0], callee[0] );
				fd.write(
					"\"{0}\" -> \"{1}\"".format(
						conv_str( caller ),
						conv_str( callee ),
						).encode() );
			fd.write( "}".encode() );
		no += 1;
		dot_files.append( dst_file );
	
	# generate images
	img_files = [];
	for f in dot_files:
		img_file = f.replace( "dot", "gif" );
		os.system( "dot -Tgif -o {0} {1}".format( img_file, f ) );
		img_files.append( img_file );
	
	# generate html file
	html_file = os.path.join( dst_dir, "index.html" );
	with open( html_file, "wb" ) as fd:
		fd.write( b"<html><body>" );
		for f in img_files:
			fd.write( "<img src='{0}' />".format( f ).encode() );
			fd.write( b"<hr>" );
		fd.write( b"</body></html>" );

if __name__ == "__main__":
	if len( sys.argv ) < 4:
		print( "{0} STACK_FILE.json OUTDIR NAME".format( sys.argv[0] ) );
		sys.exit( -1 );
	
	main( sys.argv[1], sys.argv[2], sys.argv[3] );
