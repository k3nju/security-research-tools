#! /usr/bin/python
# -*- coding:utf-8 -*-

SELECT_ALL_MODULES = """
select * from modules
""";

SELECT_MODULES_BY_NAME = """
select * from modules where name = ?
""";

UPDATE_OFFSET_MODULES_BY_MOD_ID = """
update
  modules
set
  imagebase = imagebase + ?
where
  mod_id = ?
""";

UPDATE_OFFSET_PROCS_BY_MOD_ID = """
update
  procs
set
  start_addr = start_addr + ?,
  end_addr = end_addr + ?
where
  mod_id = ?
""";

UPDATE_OFFSET_CALLRETS_BY_MOD_ID = """
update
  callrets
set
  call = call + ?,
  ret = ret + ?
where
  mod_id = ?
""";
