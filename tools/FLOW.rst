* IDA          -> lst
* lst          -> [lst2json] -> callmap.json
* callmap.json -> [json2db]  -> callmap.db
* trace.json + callmap.db -> [traceview] -> callgraph.json
* callgraph.json -> [ graph_X ] -> callgraph.dot
