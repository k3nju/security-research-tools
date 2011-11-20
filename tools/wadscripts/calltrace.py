#! /usr/bin/python
# -*- coding:utf-8 -*-

import sys;
import json;
import traceback as backtrace;
import winappdbg as wad;
from optparse import OptionParser;

CALL_MAP = None;
MAPPED_CALL_MAP = {};
THREAD_TAB_COUNT = {};

def get_diff( runtime_addr, static_addr ):
	if static_addr >= runtime_addr:
		diff = static_addr - runtime_addr;
		return diff * -1;
	return runtime_addr - static_addr;

def hook_cb( event ):
	tid = event.get_tid();
	eip = event.get_thread().get_pc();
	call_point = MAPPED_CALL_MAP[eip][0:2];
	print "{0:08x} {1}".format( call_point[0], call_point[1] );

def pre_hook_cb( event, *params ):
	tid = event.get_tid();
	eip = event.get_thread().get_pc();
	
	# FIXME: use mutex.
	if tid in THREAD_TAB_COUNT:
		THREAD_TAB_COUNT[tid] += 1;
	else:
		THREAD_TAB_COUNT[tid] = 0;
	
	print "{0}{1}".format( " " * THREAD_TAB_COUNT[tid], MAPPED_CALL_MAP[eip] );

def post_hook_cb( event ):
	# FIXME: use mutex.
	THREAD_TAB_COUNT[ event.get_tid() ] -= 1;

def map_hook( dbg, pid, base_addr ):
	diff = get_diff( base_addr, CALL_MAP[ "imagebase" ] );
	
	for callret in CALL_MAP[ "callrets" ]:
		call_addr = callret[0] + diff;
		#dbg.hook_function( pid, call_addr, preCB = pre_hook_cb, postCB = post_hook_cb );
		dbg.break_at( pid, call_addr, action = hook_cb );
		MAPPED_CALL_MAP[call_addr] = callret;

class HookInitiator( wad.EventHandler ):
	def load_dll( self, event ):
		mod = event.get_module();
		if mod.match_name( CALL_MAP[ "module_name" ].lower() ) == False:
			return;
		
		map_hook( event.debug, event.get_pid(), mod.get_base() );

def main( opts, args ):
	debug = None;
	
	if opts.pid != None:
		debug = wad.Debug();
		proc = debug.attach( int( opts.pid ) );
		mod = None;
		for mod in proc.iter_modules():
			if mod.match_name( CALL_MAP[ "module_name" ].lower() ) == True:
				break;
		else:
			raise StandardError( "Module not found" );
		
		map_hook( debug, proc.get_pid(), mod.get_base() );
	else:
		debug = wad.Debug( HookInitiator() );
		proc = debug.execv( [ opts.exe ] + args );
	
	debug.loop();

if __name__ == "__main__":
	opt_parser = OptionParser();
	opt_parser.add_option( "-p", dest="pid" );
	opt_parser.add_option( "-e", dest="exe" );
	opt_parser.add_option( "-c", dest="callmap" );
	( opts, args ) = opt_parser.parse_args();
	
	if opts.callmap == None:
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
		backtrace.print_exc();
		print( E );



