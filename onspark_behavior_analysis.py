# -*- coding: utf-8 -*- 

import sys
from operator import add
from pyspark import SparkConf
from pyspark import SparkContext

# ################ 用户行为分析 ################
def extract(line):
	try:
		(fromaccount, toaccount, timestamp, date, slot, wd, amount, gender, age, grade, stype, window, canteen, temp, rain, wind) = line.strip().split("\t")
		return ((fromaccount), (timestamp, canteen))
		# return ((fromaccount), (timestamp, window))
	except:
		return ("")

def proc(x):
	try:
		items = sorted([{"timestamp":item[0],"canteen":item[1]} for item in x], key=lambda x:x["timestamp"])
		return [items[i]["canteen"]+","+items[i+1]["canteen"] for i in xrange(0,len(items)-1)]
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
	def f(x): return x
	counts = lines.map(lambda x : extract(x)) \
				  .filter(lambda x : x != "") \
				  .groupByKey() \
				  .map(lambda x : (x[0], proc(x[1]))) \
				  .filter(lambda x : x != "") \
				  .flatMapValues(f) \
				  .map(lambda x : (x[1], 1)) \
				  .reduceByKey(lambda x,y : x+y) \
				  .sortByKey() \
				  .map(lambda x : x[0]+"\t"+str(x[1])) \
				  .repartition(1)
	output = counts.saveAsTextFile("./competition_EMC/transaction/chord_canteen_transfer")
	# output = counts.saveAsTextFile("./competition_EMC/transaction/chord_window_transfer")
