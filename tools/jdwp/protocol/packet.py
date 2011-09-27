#! /usr/bin/python

import struct;

# //-----------------------------------------------------------------------------------------//
class Command( object ):
	def __init__( self, _id, flags, cmd_set, cmd, data ):
		self.__id = _id;
		self.__flags = flags;
		self.__cmd_set = cmd_set;
		self.__cmd = cmd;
		self.__data = data;

# //-----------------------------------------------------------------------------------------//
def unpack( fmt, data, offset ):
	size = struct.calcsize( fmt );
	val = struct.unpack( fmt, data[offset:size] )[0]
	return ( val, offset + size );

class Response( object ):
	def __init__( self, raw_data ):
		off = 0;
		( self.__length, off ) = unpack( "I", raw_data, off );
		( self.__id, off ) = unpack( "I", raw_data, off );
		( self.__flags, off ) = unpack( "B", raw_data, off );
		( self.__error_code, off ) = unpack( "H", raw_data, off );
		self.__data = None;



