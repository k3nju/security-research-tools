#! /usr/bin/python

import sys;
import re;

if len( sys.argv ) < 3:
	print "$ gencalllist.py <source.lst> <call.list> <-L (library call only)> ";
	sys.exit( -1 );

isLibCallOnly = "-L" in sys.argv;
source = open( sys.argv[1] );
callList = open( sys.argv[2], "w" );

def Filter( line ):
	line = line.translate( None, "\n\r" );
	line = line.replace( "\t", " " );
	line = re.sub( "\..*text:", "", line );
	return [ i for i in line.split( " " ) if len( i ) > 0 ];

def Write( buf ):
	global callList;
	callList.write( buf );
	return True;

def WriteLibCall( buf ):
	global callList;
	if buf.startswith( "C" ) == True and buf.find( "ds:" ) == -1:
		return False;
	return Write( buf );

Writer = Write;
if isLibCallOnly == True:
	Writer = WriteLibCall;

while True:
	line = source.readline();
	if len( line ) == 0:
		break;
	if line.find( "Imagebase" ) == -1:
		continue;
	line = Filter( line );
	Writer( "Imagebase:" + line[4] + "\n" );
	break;
	
while True:
	line = source.readline();
	if len( line ) == 0:
		break;
	if line.find( "text" ) == -1:
		continue;
	if line.find( "call" ) == -1:
		continue;
	ci = line.find( ";" );
	if ci != -1 and ci < line.find( "call" ):
		continue;
	items = Filter( line );
	if Writer( "C " + items[0] + " " + " ".join( items[1:] ) + "\n" ) == False:
		continue;
	line = source.readline();
	if len( line ) == 0:
		break;
	items = Filter( line );
	Writer( "R " + items[0] + "\n" )

callList.close();

