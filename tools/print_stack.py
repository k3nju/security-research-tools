#! /usr/bin/python
# -*- coding:utf-8 -*-

import os;
import sys;
import json;
import callmapdb;

try:
	sys.path.append( "./wadscripts/" );
except:
	pass;

import wadutils;

def main():
	json_log = sys.argv[1];
	cmdb = callmapdb.CallMapDB( "/home/kj/vmshare/vulnresearch/taro/trace.json" );
	
	with open( json_log, "rb" ) as fd:
		data = fd.read();
		stacks = json.loads( data.decode() );
		for stack in stacks:
			for ( mod_path, image_base, ret_addr ) in stack:
				mod_name = os.path.basename( mod_path );
				
				

if __name__ == "__main__":
	main();
