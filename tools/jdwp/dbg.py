#! /usr/bin/python

import sys;
import socket;
import subprocess;

PID = 221;
PORT = 56000;
DST = ( "localhost", PORT );

def command( _id, flags, cmd_set, cmd, data ):

subprocess.call( "adb forword jdwp:{0} tcp:{1}".format( PID, PORT ) );

sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM );
sock.connect( DST );

# handshake
sock.send( "JDWP-Handshake" );
sock.recv( 0xff );



# EOF
