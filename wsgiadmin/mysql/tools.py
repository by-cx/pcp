# -*- coding: utf-8 -*-

def databases_list(u=None):
	"""
		Seznam databází
		Vrací (db.owner)
	"""

	data = do_sql_query("SHOW DATABASES;")
	
	databases = []
	
	for x in data:
		x = x[0].split("_",1)
		if len(x) == 2:
			if not u or u.username == x[0]:
				databases.append((x[0]+"_"+x[1],x[0]))

	return databases
