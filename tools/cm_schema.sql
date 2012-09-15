create table if not exists modules (
  mod_id    integer  not null primary key autoincrement
  ,name      text    not null
  ,imagebase integer not null
);

create table if not exists procs (
  proc_id     integer not null primary key autoincrement
  ,mod_id     integer not null
  ,start_addr integer not null
  ,end_addr   integer not null
  ,name       text    not null
  ,foreign key( mod_id ) references modules( mod_id ) on delete cascade
);

create table if not exists callrets (
  callret_id   integer primary key autoincrement
  ,proc_id     integer not null
  ,call        integer not null
  ,ret         integer not null
  ,dst_proc_id integer not null
  ,foreign key( proc_id ) references procs( proc_id ) on delete cascade
  ,foreign key( dst_proc_id ) references procs( proc_id ) on delete cascade
);
