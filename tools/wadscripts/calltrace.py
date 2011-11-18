#! /usr/bin/python
# -*- coding:utf-8 -*-

import sys;
import json;
import math;
import winappdbg as wad;
from optparse import OptionParser;

CALL_MAP = None;

def get_diff( runtime_addr, static_addr ):
	if static_addr >= runtime_addr:
		diff = static_addr - runtime_addr;
		return diff * -1;
	return runtime_addr - static_addr;

def hook_cb( event ):
	pass;


def map_hook( dbg, pid, base_addr ):
	diff = get_diff( base_addr, CALL_MAP[ "imagebase" ] );
	
	for callret in CALL_MAP[ "callrets" ]:
		call_addr = callret[0] + diff;
		dbg.hook

class HookInitiator( wad.EventHandler ):
	def load_dll( self, event ):
		mod = event.get_module();
		
		if mod.match_name( CALL_MAP[ "module_name" ].lower() ) == False:
			return;
		
		dbg = event.debug;
		pid = event.get_pid();
		diff = get_diff( event.get_module_base(), CALL_MAP[ "imagebase" ] );
		
		for callret in CALL_MAP[ "callrets" ]:
			call_addr = callret[0] + diff;
			dbg.break_at( call_addr, pid, hook_cb );

def main( opts, args ):
	debug = wad.Debug( HookInitiator() );
	
	if opts.pid != None:
		proc = debug.attach( int( debug.pid ) );
		
	else:
		debug.execv( [ opts.exe ] + args );
	
	debug.loop();

if __name__ == "__main__":
	opt_parser = OptionParser();
	opt_parser.add_option( "-p", dest="pid" );
	opt_parser.add_option( "-e", dest="exe" );
	opt_parser.add_option( "-c", dest="callmap" );
	( opts, args ) = opt_parser.parse_args();
	
	if opts.calllist == None:
		opt_parser.error( "calllist file must be specified" );
	
	if ( opts.pid == None and opts.exe == None ) or ( opts.pid != None and opts.exe != None ):
		opt_parser.error( "invalid target" );
	
	try:
		with open( opts.callmap ) as fd:
			CALL_MAP = json.load( fd );
	except:
		sys.stderr.write( "callmap file {0} not found\n".format( opts.callmap ) );
		sys.exit( -1 );
	
	try:
		main( opts, args );
	except Exception as E:
		print( E );



