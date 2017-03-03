# -*- coding: utf-8 -*- 

import sys
from operator import add
from pyspark import SparkConf
from pyspark import SparkContext

# ################ 基本统计分析 ################ 
def extract(line):
	import time
	try:
		(fromaccount, toaccount, timestamp, date, slot, wd, amount, gender, age, grade, stype, window, canteen, temp, rain, wind) = line.strip().split("\t")
		return ((canteen), (1,float(amount)))
		# return ((canteen+"\t"+window), (1,float(amount)))
		# return ((canteen, date), (1,float(amount)))
		# return ((canteen, str(time.strptime(timestamp,"%Y-%m-%d %H:%M:%S").tm_wday)), (1,float(amount)))
		# return ((canteen, slot.zfill(3)), (1,float(amount)))
		# return ((gender, canteen), (1,float(amount)))
		# return ((gender, window), (1,float(amount)))
		# grade = stype+grade if stype == "U" and 1 <= int(grade) <= 4 else stype if stype in ["M","P"] else "W"
		# return ((grade, canteen), (1,float(amount)))
		# return ((grade, window), (1,float(amount)))
		# temp = (max(min(int(float(temp)),29),5)-5)/5
		# return ((str(temp), date), (1,float(amount)))
		# rain = 0 if float(rain) <= 1 else 1 if float(rain) <=5 else 2 if float(rain) <=20 else 3 if float(rain) <=100 else 4
		# if wd == "WD" and 20141008 <= int(date) <= 20141231:
		# 	return ((str(rain), date), (1,float(amount)))
		# else:
		# 	return ("")
	except:
		return ("")

if __name__ == "__main__":
	conf = (SparkConf()
    	.setMaster("spark://namenode.omnilab.sjtu.edu.cn:7077")
    	.setAppName("Extract")
    	.set("spark.cores.max", "32")
    	.set("spark.driver.memory", "4g")
		.set("spark.executor.memory", "6g"))
	sc = SparkContext(conf = conf)
	lines = sc.textFile('hdfs://namenode.omnilab.sjtu.edu.cn/user/qiangsiwei/competition_EMC/transaction/data', 1)
	counts = lines.map(lambda x : extract(x)) \
				  .filter(lambda x : x != "") \
				  .reduceByKey(lambda x,y : (x[0]+y[0],x[1]+y[1])) \
				  .repartition(1) \
				  .map(lambda x : x[0][0]+"\t"+x[0][1]+"\t"+str(x[1][0])+"\t"+str(x[1][1])+"\t"+str(x[1][1]/x[1][0]))
	# counts = lines.map(lambda x : extract(x)) \
	# 			  .filter(lambda x : x != "") \
	# 			  .reduceByKey(lambda x,y : (x[0]+y[0],x[1]+y[1])) \
	# 			  .repartition(1) \
	# 			  .sortByKey() \
	# 			  .map(lambda x : (x[0][0],x[1])) \
	# 			  .groupByKey() \
	# 			  .map(lambda x : (x[0]+"\t"+str(int(sum([i[0] for i in x[1]])/len(x[1])))+"\t"+str(int(sum([i[1] for i in x[1]])/len(x[1])))))
	output = counts.saveAsTextFile("./competition_EMC/transaction/tree_canteen")
	# output = counts.saveAsTextFile("./competition_EMC/transaction/tree_window")
	# output = counts.saveAsTextFile("./competition_EMC/transaction/timeline_canteen_date")
	# output = counts.saveAsTextFile("./competition_EMC/transaction/timeline_canteen_slot")
	# output = counts.saveAsTextFile("./competition_EMC/transaction/radar_canteen_wd")
	# output = counts.saveAsTextFile("./competition_EMC/transaction/loop_gender_canteen")
	# output = counts.saveAsTextFile("./competition_EMC/transaction/loop_gender_window")
	# output = counts.saveAsTextFile("./competition_EMC/transaction/pie_grade_canteen")
	# output = counts.saveAsTextFile("./competition_EMC/transaction/pie_grade_window")
	# output = counts.saveAsTextFile("./competition_EMC/transaction/mix_temp")
	# output = counts.saveAsTextFile("./competition_EMC/transaction/mix_rain")
