import os
import re
import json
import shutil
from datetime import datetime

def getnewmeta(path):
	data = []
	obj = os.scandir(path)
	for entry in obj:
		# if entry.is_file():
		if entry.is_dir():
			continue
		name = entry.name
		with open(os.path.join(path, name)) as f:
			tmp = json.load(f)
		data.append(tmp)
		# data.append((name, os.path.join(path, name)))
	return data

def short_hash(text, length=6):
	hash_value = 0
	for char in text:
		hash_value = (hash_value * 31 + ord(char)) & 0xFFFFFFFF
	return f"{hash_value:08x}"[:length]

def load_nh_json():
	path = os.path.join("../", "nhdata.json")
	# path = "../nh.json"
	with open(path) as f:
		data = json.load(f)
	sorted(data, key=lambda d: d['st_date'])
	return data

def save_group(lnj):
	raw_group = list(set([x["group"] if x["group"] != "" else "Other" for x in lnj]))
	group = []
	for i, rg in enumerate(raw_group):
		id = "GR"+str(i+1).rjust(6, "0")
		group.append({"id": id, "name": rg})
	with open("group.json", "w") as f:
		json.dump(group, f)
	return group

def find_group(group, name):
	ret = ""
	for g in group:
		if g["name"] == "Other":
			ret = g["id"]
		if g["name"] == name:
			return g["id"]
	return ret

def copy_file(old_path, new_path, data):
	cmd = [(os.path.join(old_path, x), os.path.join(new_path, x)) for x in data]
	for i, of in enumerate(cmd):
		if os.path.isfile(of[1]):
			continue
		shutil.copy(of[0], of[1])
		print("copy", of)
	# print(old_file)
	# print(new_file)

def clean_title(txt):
	# new_txt = txt.replace(r"((\[.*?\])|(\{.*?\})|(\(.*?\)))", "")
	regex = r"((\[.*?\])|(\{.*?\})|(\(.*?\)))"
	# regexs = [r"(\[.*?\])",r"(\{.*?\})",r"(\(.*?\))"]
	# new_txt = txt
	# for r in regexs:
	# 	result = re.sub(r, "", new_txt, 0)
	# 	if result:
	# 		return f"None -> {r} {new_txt}"
	# 	new_txt = result
	new_txt = re.sub(regex, "", txt, 0)
	if not new_txt:
		# return f"None -> {new_txt}"
		return new_txt
	new_txt = new_txt.replace("Milftoon - ", "")
	return new_txt.strip()

def main():
	gh_path = "https://raw.githubusercontent.com/laserine32/iatnehn/master/"
	lnj = load_nh_json()
	# group = save_group(lnj)
	data = []
	pth = []
	for i, d in enumerate(lnj):
		# print(json.dumps(d, indent=2))
		# print(d["title"])
		# print(clean_title(d["title"]))
		# print("\n")
		# continue
		id = "NH"+str(i+1).rjust(6, "0")
		op = d["path"].split("/")
		old_path = os.path.join("..", "static", op[0], op[1])
		path = os.path.join("data", short_hash(str(d)))
		print(id, path)
		if path in pth:
			print("DUPLICATE")
		pth.append(path)
		# os.makedirs(path, exist_ok=True)
		# copy_file(old_path, path, d["img"])
		thumb = gh_path + path.replace("\\", "/") + "/" + d["thumb"]
		dt_object = datetime.fromtimestamp(d["st_date"]).strftime("%Y-%m-%d %H:%M:%S")
		img = [gh_path + path.replace("\\", "/") + "/" + x for x in d["img"]]
		data.append({
			"id": id,
			"title": clean_title(d["title"]),
			"thumb":   thumb,
			"date": dt_object,
			"groupId": find_group(lnj, d["group"]),
			"img": img,
		})
		# break
	print(json.dumps(data, indent=2))
	with open("data.json", "w") as f:
		json.dump(data, f, indent=2)

def comparedata():
	with open("data.json") as f:
		raw = json.load(f)
	with open("tmp_nh.json") as f:
		data = json.load(f)
	def komparasi(a, b):
		for c in b:
			if (clean_title(c["title"]) == a["title"]) and (c["date"] == a["date"]):
				return c
		return None
	doned = 0
	for i, r in enumerate(raw):
		# print(r["date"])
		res = komparasi(r, data)
		if res == None:
			break
		raw[i]["id"] = res["id"]
		# raw[i]["title"] = res["title"]
		raw[i]["groupId"] = res["groupId"]
		doned += 1
	print(len(raw), doned)
	with open("data.json", "w") as f:
		json.dump(raw, f, indent=2)

def seachGroup(name):
	with open("group.json") as f:
		data = json.load(f)
	lend = len(data)
	# ret = ""
	for d in data:
		if d["name"] == name:
			return d["id"], None
			# return d["id"], f"""INSERT INTO "Group" (id, name) VALUES ('{d["id"]}', '{d["name"]}');"""
	id = "GR"+str(lend+1).rjust(6, "0")
	sql = f"""INSERT INTO "Group" (id, name) VALUES ('{id}', '{name}');"""
	data.append({"id": id, "name": name})
	with open("group.json", "w") as f:
		json.dump(data, f, indent=2)
	return id, sql

def repgh(data, gh):
	ret = []
	for d in data:
		ret.append(gh+d.replace("new\\", "").replace("\\", "/"))
	return ret

def genSqlManga(data):
	id, title, thumb, date, groupId, _ = data.values()
	sql = f"""INSERT INTO "Manga" (id, title, thumb, date, "groupId") VALUES ('{id}', '{title}', '{thumb}', '{date}', '{groupId}');"""
	return sql

def genSqlPeji(data):
	sqls = []
	for i, d in enumerate(data["img"]):
		mid = data["id"]
		id = mid + "_" + str(i+1).rjust(6, "0")
		sql = f"""('{id}', '{d}', '{mid}'),"""
		sqls.append(sql)
	return sqls

def readNew():
	gh_path = "https://raw.githubusercontent.com/laserine32/iatnehn/master/"
	pmetas = getnewmeta("new")
	# print(pmetas)
	data = []
	sql_group = []
	sql_manga = []
	sql_peji = ['INSERT INTO "Peji" (id, img, "mangaId") VALUES ']
	for m in pmetas:
		id = "NH" + str(m["id"])
		old_path = os.path.join("new", "data", str(m["id"]))
		new_path = os.path.join("data", str(m["id"]))
		if not os.path.isdir(new_path):
			shutil.move(old_path, new_path)
		m["id"] = id
		m["thumb"] = gh_path + m["thumb"].replace("new\\", "").replace("\\", "/")
		groupId, sqlg = seachGroup(m["group"].title())
		if sqlg != None:
			sql_group.append(sqlg)
		m["groupId"] = groupId
		img = repgh(m["img"], gh_path)
		del m["group"]
		del m["img"]
		m["img"] = img
		# print(json.dumps(m, indent=2)) 
		sql_manga.append(genSqlManga(m))
		sql_peji += genSqlPeji(m)
		data.append(m)
		# break
	all_sql = sql_group + sql_manga + sql_peji
	with open("tmp.sql", "w", encoding="utf-8") as f:
		f.write("\n".join(all_sql))
	with open("data.json") as f:
		old_data = json.load(f)
	old_data += data
	# print(json.dumps(old_data, indent=2))
	with open("data.json", "w") as f:
		json.dump(old_data, f, indent=2)


if __name__ == '__main__':
	os.system("cls")
	print("Ready")
	# main()
	# comparedata()
	readNew()