#! /usr/bin/python
# -*- coding:utf-8 -*-

import sys;
import sqlite3;

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

def conv_to_sqlite3( db_file, callmap ):
	with sqlite3.connect( db_file ):
		conn.executemany( SCHEMA );

		# insert to modules table
		conn.execute(
			"insert into modules values( ?, ? )",
			( callmap[ "module_name" ]
			  ,callmap[ "imagebase" ] )
			);

		# insert to procs table
		for ( addr, name )  in callmap[ "procs" ]:
			conn.execute(
				"insert into procs values( ?, ? )",
				( addr,
				  name ) );

		# insert to callrets table
		for ( call_addr, call_dst, ret_addr ) in callmap[ "callrets" ]:
			conn.execute(
				"insert into callrets values( ?, ?, ? )",
				( call_addr,
				  ret_addr,
				  call_dst ) );

		
