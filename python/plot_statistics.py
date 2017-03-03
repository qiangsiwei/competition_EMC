# -*- coding: utf-8 -*-

import fileinput

#################### 数据预处理 ####################

def statistic_qixiang():
	days = {}
	for line in fileinput.input("data/prepared/qixiang/shanghaiqixiang_jiaoda.txt"):
		if not fileinput.isfirstline():
			try:
				part = line.strip().split("\t")
				date, temp, rain, wind = part[0][:8], float(part[2]), float(part[3]), float(part[5])
				days[date] = {"temp_max":temp, "rain":rain, "wind_max":wind} if not days.has_key(date) else {"temp_max":max(days[date]["temp_max"],temp), "rain":days[date]["rain"]+rain, "wind_max":max(days[date]["wind_max"],wind)}
			except:
				continue
	fileinput.close()

	with open("data/prepared/qixiang/qixiang.txt","w") as f:
		for date in sorted(days):
			f.write(date+"\t"+str(days[date]["temp_max"])+"\t"+str(days[date]["rain"])+"\t"+str(days[date]["wind_max"])+"\n")


#################### 可视化数据准备 ####################

def plot_timeline_canteen_date():
	dates, v1s, v2s, v3s = [], {}, {}, {}
	for line in fileinput.input("data_processed/timeline_canteen_date.txt"):
		(canteen, date, v1, v2, v3) = line.strip().split("\t")
		if canteen == "一餐":
			dates.append(date)
		if not v1s.has_key(canteen):
			v1s[canteen], v2s[canteen], v3s[canteen] = [], [], []
		v1s[canteen].append(v1)
		v2s[canteen].append(v2)
		v3s[canteen].append(v3)
	fileinput.close()

	with open("data2js.txt","w") as f:
		f.write("\""+"\",\"".join(dates)+"\"\n")
		for canteen in ["一餐","二餐","三餐","四餐","五餐","六餐","哈乐"]:
			f.write(",".join(v1s[canteen])+"\n")
		for canteen in ["一餐","二餐","三餐","四餐","五餐","六餐","哈乐"]:
			f.write(",".join(v2s[canteen])+"\n")
		for canteen in ["一餐","二餐","三餐","四餐","五餐","六餐","哈乐"]:
			f.write(",".join(v3s[canteen])+"\n")


def plot_timeline_canteen_slot():
	dates, v1s, v2s, v3s = [], {}, {}, {}
	for line in fileinput.input("data_processed/timeline_canteen_slot.txt"):
		(canteen, slot, v1, v2, v3) = line.strip().split("\t")
		if not v1s.has_key(canteen):
			v1s[canteen], v2s[canteen], v3s[canteen] = ["0" for i in xrange(24*6)], ["0" for i in xrange(24*6)], ["0" for i in xrange(24*6)]
		v1s[canteen][int(slot)] = v1
		v2s[canteen][int(slot)] = v2
		v3s[canteen][int(slot)] = v3
	fileinput.close()

	with open("data2js.txt","w") as f:
		for canteen in ["一餐","二餐","三餐","四餐","五餐","六餐","哈乐"]:
			f.write(",".join(v1s[canteen][37:93])+"\n")
		for canteen in ["一餐","二餐","三餐","四餐","五餐","六餐","哈乐"]:
			f.write(",".join(v2s[canteen][37:93])+"\n")
		for canteen in ["一餐","二餐","三餐","四餐","五餐","六餐","哈乐"]:
			f.write(",".join(v3s[canteen][37:93])+"\n")


def plot_radar_canteen_wd():
	canteen_map = {}
	for wday in [0,1,2,3,4,5,6]:
		canteen_map[wday] = {}
		for canteen in ["一餐","二餐","三餐","四餐","五餐","六餐","哈乐"]:
			canteen_map[wday][canteen] = 0
	for line in fileinput.input("data_processed/radar_canteen_wd.txt"):
		(canteen, wd, v1, v2, v3) = line.strip().split("\t")
		canteen_map[int(wd)][canteen] = v1
	fileinput.close()

	with open("data2js.txt","w") as f:
		for wday in [0,1,2,3,4,5,6]:
			f.write(",".join([canteen_map[wday][canteen] for canteen in ["一餐","二餐","三餐","四餐","五餐","六餐","哈乐"]])+"\n")


def plot_tree_canteen():
	with open("data2js.txt","w") as f:
		canteen_map, window_map, _id = {}, {}, 0
		for line in fileinput.input("data_processed/tree_canteen.txt"):
			_id += 1
			(name, v1, v2, v3) = line.strip().split("\t")
			f.write("{name:'"+name+"	日均客流"+v1+"',value:"+str(int(v1)/3)+",id:"+str(_id)+",depth:1,category:1},\n")
			canteen_map[name] = _id
		fileinput.close()

		for line in fileinput.input("data_processed/tree_window.txt"):
			_id += 1
			(canteen, name, v1, v2, v3) = line.strip().split("\t")
			f.write("{name:'"+name+"	日均客流"+v1+"',value:"+v1+",id:"+str(_id)+",depth:2,category:0},\n")
			window_map[name] = _id
		fileinput.close()

		for line in fileinput.input("data_processed/tree_canteen.txt"):
			(name, v1, v2, v3) = line.strip().split("\t")
			f.write("{source:"+str(0)+",target:"+str(canteen_map[name])+",weight:1},\n")
		fileinput.close()

		for line in fileinput.input("data_processed/tree_window.txt"):
			(canteen, name, v1, v2, v3) = line.strip().split("\t")
			f.write("{source:"+str(canteen_map[canteen])+",target:"+str(window_map[name])+",weight:1},\n")
		fileinput.close()


def plot_chord_canteen_transfer():
	canteen_list, canteen_map = [["0" for i in xrange(7)] for i in xrange(7)], {"一餐":0,"二餐":1,"三餐":2,"四餐":3,"五餐":4,"六餐":5,"哈乐":6}
	for line in fileinput.input("data_processed/chord_canteen_transfer.txt"):
		canteen_1, canteen_2, v = line.strip().split("\t")[0].split(",")[0], line.strip().split("\t")[0].split(",")[1], line.strip().split("\t")[1]
		canteen_list[canteen_map[canteen_1]][canteen_map[canteen_2]] = v
	fileinput.close()

	with open("data2js.txt","w") as f:
		for canteen in [0,1,2,3,4,5,6]:
			f.write(",".join(canteen_list[canteen])+"\n")


def plot_chord_window_transfer():
	window_map = {}
	for line in fileinput.input("data_processed/chord_window_transfer.txt"):
		window_1, window_2, v = line.strip().split("\t")[0].split(",")[0], line.strip().split("\t")[0].split(",")[1], line.strip().split("\t")[1]
		if not window_map.has_key(window_1):
			window_map[window_1] = {"canteen":"","total":0,"stay":0,"price":0}
		if window_2 == window_1:
			window_map[window_1]["stay"] = int(v)
		window_map[window_1]["total"] += int(v)
	fileinput.close()

	for line in fileinput.input("data_processed/tree_window.txt"):
		(canteen, window, v1, v2, v3) = line.strip().split("\t")
		window_map[window]["canteen"] = canteen
		window_map[window]["price"] = float(v3)
	fileinput.close()

	with open("data2js.txt","w") as f:
		for window, values in window_map.iteritems():
			if values["canteen"] == "一餐":
			# if values["canteen"] == "二餐":
			# if values["canteen"] == "三餐":
			# if values["canteen"] == "四餐":
			# if values["canteen"] == "五餐":
			# if values["canteen"] == "六餐":
			# if values["canteen"] == "哈乐":
				f.write("["+str(round(values["price"],2))+","+str(round(100.0*values["stay"]/values["total"],2))+"],\n")
				# print window, values["canteen"], 1.0*values["stay"]/values["total"], values["price"]


if __name__ == "__main__":
	statistic_qixiang()
	plot_timeline_canteen_date()
	plot_timeline_canteen_slot()
	plot_radar_canteen_wd()
	plot_tree_canteen()
	plot_chord_canteen_transfer()
	plot_chord_window_transfer()
