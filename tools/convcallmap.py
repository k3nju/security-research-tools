#! /usr/bin/python
# -*- coding:utf-8 -*-

import sys;
import sqlite3;
import json;

SCHEMA = """
create table modules (
  PK integer primary key autoincrement,
  name text not null,
  imagebase integer not null
);

create table procs (
  PK integer primary key autoincrement,
  address integer not null,
  name text not null
);

create table callrets (
  PK integer primary key autoincrement,
  call integer not null,
  ret integer not null,
  call_dst integer not null
);
""";

def init_db( db_file ):
	try:
		with sqlite3.connect( db_file ) as conn:
			for stmt in SCHEMA.split( ";" ):
				conn.execute( stmt );
	except:
		pass;

def conv_to_sqlite3( db_file, callmap ):
	with sqlite3.connect( db_file ) as conn:
		# insert to modules table
		conn.execute(
			"insert into modules ( name, imagebase ) values( ?, ? )",
			( callmap[ "module_name" ]
			  ,callmap[ "imagebase" ] )
			);

		# insert to procs table
		for ( addr, name )  in callmap[ "procs" ]:
			conn.execute(
				"insert into procs ( address, name ) values( ?, ? )",
				( addr,
				  name ) );
		
		# insert to callrets table
		for ( call_addr, call_dst, ret_addr ) in callmap[ "callrets" ]:
			conn.execute(
				"insert into callrets ( call, ret, call_dst ) values( ?, ?, ? )",
				( call_addr,
				  ret_addr,
				  call_dst ) );

if __name__ == "__main__":
	callmap_file = sys.argv[1];
	db_file = sys.argv[2];
	init_db( db_file );
	with open( callmap_file, "rb" ) as fd:
		conv_to_sqlite3( db_file, json.load( fd ) );
