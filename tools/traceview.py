#! /usr/bin/python
# -*- coding:utf-8 -*-

import os;
import sys;
import json;

try:
	# import some local environment settings.
	import localenv;
except:
	pass;

import callmapdb;

if __name__ == "__main__":
	if len( sys.argv ) < 3:
		print( "{0} TRACE_LOG_JSON DB_FILE [JSON]".format( sys.argv[0] ) );
		sys.exit( -1 );

	st_file = sys.argv[1];
	db_file = sys.argv[2];

	# load stack trace
	with open( st_file ) as fd:
		# stack trace format
		# [
		#  [
		#   [ "module path", base_address, return_address ],
		#  ]
		# ]
		stack_trace = json.load( fd );
	
	# load callmap database
	cmdb = callmapdb.CallMapDB( db_file );
	
	# calc base address map
	base_addr_map = {};
	for stack in stack_trace:
		for ( mod_path, base_addr, ret_addr ) in stack:
			mod_name = mod_path.split( "\\" )[-1];
			if mod_name in base_addr_map:
				continue;
			base_addr_map[ mod_name ] = base_addr;
			cmdb.update_offset( mod_name, base_addr );
	
	# view stack trace
	output = [];
	for stack in stack_trace:
		op_stack = [];
		for ( mod_path, base_addr, ret_addr ) in stack:
			mod_name = mod_path.split( "\\" )[-1];
			rs = cmdb.get_procs_by_ret_addr( ret_addr );
			if len( rs ) >= 1:
				r = rs[0];
				op_stack.append( ( ret_addr, mod_name, r[-1] ) );
			else:
				op_stack.append( ( ret_addr, mod_name, "" ) );
		output.append( op_stack );
	
	print( json.dumps( output ) );
