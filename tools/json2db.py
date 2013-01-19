#! /usr/bin/python
# -*- coding:utf-8 -*-

import sys;
import sqlite3;
import json;
import traceback;

SCHEMA = open( "./cm_schema.sql", "rb" ).read().decode();

def init_db( db_file ):
	try:
		with sqlite3.connect( db_file ) as conn:
			for stmt in SCHEMA.split( ";" ):
				conn.execute( stmt );
	except:
		traceback.print_exc();

def get_cur_and_dst( conn, mod_id, call_src, call_dst ):
	cursor = conn.cursor();
	cursor.execute(
		"select proc_id from procs where mod_id = ? and ? between start_addr and end_addr",
		( mod_id,
		  call_src )
		);
	row = cursor.fetchone();
	if row != None:
		current_proc_id = row[0];
	else:
		current_proc_id = -1;

	cursor.execute(
		"select proc_id from procs where mod_id = ? and name = ?",
		( mod_id,
		  call_dst )
		);
	row = cursor.fetchone();
	if row != None:
		dst_proc_id = row[0];
	else:
		dst_proc_id = -1;

	return ( current_proc_id, dst_proc_id );

def conv_to_sqlite3( db_file, callmap ):
	with sqlite3.connect( db_file ) as conn:
		cursor = conn.cursor();
		# insert to modules table
		cursor.execute(
			"insert into modules ( name, imagebase ) values( ?, ? )",
			( callmap[ "module_name" ]
			  ,callmap[ "imagebase" ] )
			);
		mod_id = cursor.lastrowid;

		# insert to procs table
		for ( proc_start, proc_end, name )  in callmap[ "procs" ]:
			cursor.execute(
				"insert into procs ( mod_id, start_addr, end_addr, name ) values( ?, ?, ?, ? )",
				( mod_id,
				  proc_start,
				  proc_end,
				  name ) );

		# insert to callrets table
		for ( call_addr, call_dst, ret_addr ) in callmap[ "callrets" ]:
			( cur_proc_id, dst_proc_id ) = get_cur_and_dst( conn, mod_id, call_addr, call_dst );
			cursor.execute(
				"insert into callrets ( proc_id, call, ret, dst_proc_id ) values( ?, ?, ?, ? )",
				( cur_proc_id,
				  call_addr,
				  ret_addr,
				  dst_proc_id ) );
		

if __name__ == "__main__":
	if len( sys.argv ) != 3:
		print( "$ {0} <callmap_file> <db_file>".format( sys.argv[0] ) );
		sys.exit( -1 );
	
	callmap_file = sys.argv[1];
	db_file = sys.argv[2];
	init_db( db_file );
	with open( callmap_file, "rb" ) as fd:
		decoded = fd.read().decode();
		conv_to_sqlite3( db_file, json.loads( decoded ) );
