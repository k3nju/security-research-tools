#! /usr/bin/python
# -*- coding:utf-8 -*-

import os;
import sys;
import sqlite3;
import tempfile;
import shutil;
import callmapdb_sql;

try:
	sys.path.append( "./wadscripts" );
except:
	pass;

import wadutils;

class CallMapDB( object ):
	def __init__( self, db_file ):
		self.__tmp_db_file = os.path.join( tempfile.gettempdir(), "tmp_cm.cb" );
		shutil.copyfile( db_file, self.__tmp_db_file );
		self.__conn = sqlite3.connect( self.__tmp_db_file );
	
	@property
	def tmp_db_file( self ):
		return self.__tmp_db_file;
	

	def __fetchall( self, sql, params ):
		cur = self.__conn.cursor();
		cur.execute( sql, params );
		return cur.fetchall();

	def __fetchone( self, sql, params ):
		cur = self.__conn.cursor();
		cur.execute( sql, params );
		return cur.fetchone();

	def update_offset( self, mod_name, runtime_base_addr ):
		mod_rec = self.get_module_by_name( mod_name.lower() );
		if mod_rec == None:
			return False;
		
		mod_id = mod_rec[0];
		static_base_addr = mod_rec[2];
		offset = wadutils.get_offset( runtime_base_addr, static_base_addr );
		
		cur = self.__conn.cursor();
		cur.execute(
			callmapdb_sql.UPDATE_OFFSET_MODULES_BY_MOD_ID,
			( offset, mod_id )
			);

		cur.execute(
			callmapdb_sql.UPDATE_OFFSET_PROCS_BY_MOD_ID,
			( offset, offset, mod_id, )
			);

		proc_recs = self.get_procs_by_mod_id( mod_id );
		for r in proc_recs:
			proc_id = r[0];
			cur.execute(
				callmapdb_sql.UPDATE_OFFSET_CALLRETS_BY_MOD_ID,
				( offset, offset, proc_id )
				);

		self.__conn.commit();
		
		return True;
		
	def get_modules( self ):
		return self.__fetchall( callmapdb_sql.SELECT_ALL_MODULES, () );
	
	def get_module_by_name( self, name ):
		return self.__fetchone( callmapdb_sql.SELECT_MODULES_BY_NAME, ( name.lower(), ) );
	
	def get_procs_by_mod_id( self, mod_id ):
		return self.__fetchall( callmapdb_sql.SELECT_PROCS_BY_MOD_ID, ( mod_id, ) );
	
	def get_procs_by_ret_addr( self, ret_addr ):
		return self.__fetchall( callmapdb_sql.SELECT_PROCS_BY_RET_ADDR, ( ret_addr, ) );

if __name__ == "__main__":
	pass
