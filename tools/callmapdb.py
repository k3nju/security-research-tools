#! /usr/bin/python
# -*- coding:utf-8 -*-

import os;
import sys;
import sqlite3;
import tempfile;
import shutil;
import wadutils;
import callmapdb_sql;

class CallMapDB( object ):
	def __init__( self, db_file ):
		self.__tmp_db_file = os.path.join( tempfile.gettempdir(), "tmp_cm.cb" );
		shutil.copyfile( db_file, self.__tmp_db_file );
		self.__conn = sqlite3.connect( self.__tmp_db_file );

	def update_offset( self, mod_name, runtime_base_addr ):
		mod_rec = self.get_modules_by_name( mod_name );
		mod_id = mod_rec[0];
		static_base_addr = mod_rec[2];
		offset = wadutils.get_offset( rumtime_base_addr, static_base_addr );
		
		cur = self.__conn.cursor();
		cur.execute(
			callmapdb_sql.UPDATE_OFFSET_MODULES_BY_MOD_ID,
			( offset, mod_id )
			);
		cur.execute(
			callmapdb_sql.UPDATE_OFFSET_PROCES_BY_MOD_ID,
			( offset, offset, mod_id, )
			);
		cur.execute(
			callmapdb_sql.UPDATE_OFFSET_CALLRETS_BY_MOD_ID,
			( offset, offset, mod_id )
			);
		
	def get_modules( self ):
		cur = self.__conn.cursor();
		cur.execute( callmapdb_sql.SELECT_ALL_MODULES );
		return cur.fetchall();
	
	def get_module_by_name( self, name ):
		cur = self.__conn.cursor();
		cur.execute( callmapdb_sql.SELECT_MODULES_BY_NAME, ( name.lower(), ) );
		return cur.fetchone();


if __name__ == "__main__":
	db = CallMapDB( "/tmp/a.db" );
	print( db.get_module_by_name( "TJSVDA.DLL" ) );
