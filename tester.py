from replit import db

try:
	tester_members = db["tester_members"]
except:
	db["tester_members"] = [123, 456]
	tester_members = db["tester_members"]

def list_testers():
	tester_members = db["tester_members"]
	for member_id in tester_members:
		print(member_id)

def add_tester(tester_id):
	tester_members = db["tester_members"]
	if tester_id not in tester_members:
		tester_members.append(tester_id)
		db["tester_members"] = tester_members
	else:
		return

def check_if_notified(tester_id):
	tester_members = db["tester_members"]
	if tester_id in tester_members:
		return tester_id
	else:
		return None

def clear_testers():
	tester_members = [123, 456]
	db["tester_members"] = tester_members

print('Loaded tester.py')