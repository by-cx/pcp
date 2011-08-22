# -*- coding: utf-8 -*-

from subprocess import Popen,PIPE

def databases_list(u=None):
	"""
		Vrací seznam databází uživatele
	"""
	if u:
		name = u.username
	p = Popen(["psql","-l","-A","-t"],stdout=PIPE)
	data = p.stdout.readlines()
	p.wait()
	
	dbs = []
	
	for row in [x.strip().split("|")[0:2] for x in data if x.strip()]:
		if len(row) == 2:
			db = row[0]
			owner = row[1]
			if not u or owner == name:
				dbs.append((db,owner))
	
	return dbs