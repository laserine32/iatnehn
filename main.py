import os
import re
import json
import shutil
from datetime import datetime

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
		raw[i]["title"] = res["title"]
		raw[i]["groupId"] = res["groupId"]
		doned += 1
	print(len(raw), doned)
	with open("data.json", "w") as f:
		json.dump(raw, f, indent=2)


if __name__ == '__main__':
	os.system("cls")
	print("Ready")
	# main()
	comparedata()