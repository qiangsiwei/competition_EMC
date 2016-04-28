# -*- coding: utf-8 -*- 

import sys
from operator import add
from pyspark import SparkConf
from pyspark import SparkContext
 
def extract(line):
	import time
	try:
		fromaccount, toaccount, syscode, timestamp, amount = line.strip().split("\t")
		date, slot, amount = timestamp.split(" ")[0].replace("-",""), int(timestamp.split(" ")[1].split(":")[0])*6+int(timestamp.split(" ")[1].split(":")[1])/10, float(amount)/100
		pytime = time.strptime(timestamp,"%Y-%m-%d %H:%M:%S")
		wd = {0:"WD",1:"WD",2:"WD",3:"WD",4:"WD",5:"WE",6:"WE"}[pytime.tm_wday]
		account = accounts[fromaccount]
		gender, age, grade, stype = account["gender"], account["age"], account["grade"], account["stype"]
		merchant = merchants[toaccount]
		accountname, mtype = merchant["accountname"], merchant["mtype"]
		qixiang = qixiangs[date] if date in qixiangs else {"temp":"NA","rain":"NA","wind":"NA"}
		temp, rain, wind = qixiang["temp"], qixiang["rain"], qixiang["wind"]
		return (fromaccount, toaccount, timestamp, date, slot, wd, amount, gender, age, grade, stype, accountname, mtype, temp, rain, wind)
	except:
		return ("")

global accounts, merchants, qixiang

if __name__ == "__main__":
	accounts, merchants, qixiangs = {}, {}, {}
	import fileinput
	for line in fileinput.input("data_prepared/account.txt"):
		(account, studentcode, gender, yearofbirth, grade, stype) = line.strip().split("\t")
		gender, age, grade, stype = {"男":"M","女":"F"}[gender], 2015-int(yearofbirth), 2015-int(grade), {"本科":"U","硕士":"M","博士":"P"}[stype]
		accounts[account] = {"account":account,"gender":gender,"age":age,"grade":grade,"stype":stype}
	fileinput.close()
	# for account in accounts:
	# 	print accounts[account]
	for line in fileinput.input("data_prepared/merchant.txt"):
		syscode, codename, toaccount, accountname, address, opendata, mtype = line.strip().split("\t")
		if 1 <= int(mtype) <= 7:
			mtype = {"1":"一餐","2":"二餐","3":"三餐","4":"四餐","5":"五餐","6":"六餐","7":"哈乐"}[mtype]
			merchants[toaccount] = {"toaccount":toaccount,"accountname":accountname,"mtype":mtype}
	fileinput.close()
	# for merchant in merchants:
	# 	print merchants[merchant]
	for line in fileinput.input("data_prepared/qixiang/qixiang.txt"):
		date, temp, rain, wind = line.strip().split("\t")
		qixiangs[date] = {"date":date,"temp":float(temp),"rain":float(rain),"wind":float(wind)}
	fileinput.close()
	# for date in qixiangs:
	# 	print qixiangs[date]
	conf = (SparkConf()
    	.setMaster("spark://namenode.omnilab.sjtu.edu.cn:7077")
    	.setAppName("Extract")
    	.set("spark.cores.max", "32")
    	.set("spark.driver.memory", "4g")
		.set("spark.executor.memory", "6g"))
	sc = SparkContext(conf = conf)
	# sc = SparkContext('spark://namenode.omnilab.sjtu.edu.cn:7077',appName="Extract")
	lines = sc.textFile('hdfs://namenode.omnilab.sjtu.edu.cn/user/qiangsiwei/competition_EMC/trade.txt', 1)
	counts = lines.map(lambda x : extract(x)) \
				  .filter(lambda x : x != "") \
				  .distinct() \
				  .map(lambda x : "\t".join([str(i) for i in x]))
	output = counts.saveAsTextFile("./competition_EMC/transaction/data")
