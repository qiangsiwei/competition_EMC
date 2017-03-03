# -*- coding: utf-8 -*-

import fileinput
import numpy as np
from sklearn.svm import SVR
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.cross_validation import KFold

#################### 特征抽取 ####################

canteen_map = {"一餐":[],"二餐":[],"三餐":[],"四餐":[],"五餐":[],"六餐":[],"哈乐":[]}
feature_map = {"一餐":[],"二餐":[],"三餐":[],"四餐":[],"五餐":[],"六餐":[],"哈乐":[]}
for line in fileinput.input("data/prediction_original.txt"):
	(canteen, date, weekday, temp, rain, wind, v1, v2, v3) = line.strip().split("\t")
	if 20141008 <= int(date) <= 20141231:
		canteen_map[canteen].append({"date":int(date),"month":int(date[4:6]),"weekday":int(weekday),"temp":float(temp),"rain":float(rain),"wind":float(wind),"v1":int(v1),"v2":float(v2)})
fileinput.close()
for canteen in canteen_map.keys():
	canteen_map[canteen] = sorted(canteen_map[canteen], key=lambda x:x["date"])
for canteen in canteen_map.keys():
	for i in xrange(1, len(canteen_map[canteen])):
		canteen_map[canteen][i]["prev_v1"] = canteen_map[canteen][i-1]["v1"]
		canteen_map[canteen][i]["prev_v2"] = canteen_map[canteen][i-1]["v2"]
		canteen_map[canteen][i]["prev_campus_v1"] = sum([canteen_map[ct][i-1]["v1"] for ct in ["一餐","二餐","三餐","四餐","五餐","六餐","哈乐"]])
		canteen_map[canteen][i]["prev_campus_v2"] = sum([canteen_map[ct][i-1]["v2"] for ct in ["一餐","二餐","三餐","四餐","五餐","六餐","哈乐"]])
		feature_map[canteen].append([canteen_map[canteen][i]["date"], canteen_map[canteen][i]["month"], canteen_map[canteen][i]["weekday"], canteen_map[canteen][i]["temp"], canteen_map[canteen][i]["rain"], canteen_map[canteen][i]["wind"], \
		canteen_map[canteen][i]["prev_v1"], canteen_map[canteen][i]["prev_v2"], canteen_map[canteen][i]["prev_campus_v1"], canteen_map[canteen][i]["prev_campus_v2"], \
		canteen_map[canteen][i]["v1"], canteen_map[canteen][i]["v2"]])

#################### 预测 ####################

for canteen in ["一餐","二餐","三餐","四餐","五餐","六餐","哈乐"]:
	kf = KFold(len(feature_map[canteen]), n_folds=10)
	X = np.array([feature_map[canteen][i][1:10] for i in xrange(len(feature_map[canteen]))])
	y1 = np.array([feature_map[canteen][i][10] for i in xrange(len(feature_map[canteen]))])
	y2 = np.array([feature_map[canteen][i][11] for i in xrange(len(feature_map[canteen]))])
	error1, error2 = 0, 0
	for train, test in kf:
		X_train, X_test, y1_train, y1_test, y2_train, y2_test = X[train], X[test], y1[train], y1[test], y2[train], y2[test]
		est1 = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=0, loss='ls').fit(X_train, y1_train)
		est2 = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=0, loss='ls').fit(X_train, y2_train)
		# est1 = SVR(C=1.0, cache_size=200, coef0=0.0, degree=3, epsilon=0.1, gamma=0.0, kernel='rbf', max_iter=-1, shrinking=True, tol=0.001, verbose=False).fit(X_train, y1_train)
		# est2 = SVR(C=1.0, cache_size=200, coef0=0.0, degree=3, epsilon=0.1, gamma=0.0, kernel='rbf', max_iter=-1, shrinking=True, tol=0.001, verbose=False).fit(X_train, y2_train)
		error1 += sum([abs(y1_test[i]-est1.predict(X_test[i])) for i in xrange(len(X_test))])/len(X_test)
		error2 += sum([abs(y2_test[i]-est2.predict(X_test[i])) for i in xrange(len(X_test))])/len(X_test)
	error1, error2 = error1/len(kf), error2/len(kf)
	avg1, avg2 = sum([feature_map[canteen][i][10] for i in xrange(len(feature_map[canteen]))])/len(feature_map[canteen]), sum([feature_map[canteen][i][11] for i in xrange(len(feature_map[canteen]))])/len(feature_map[canteen])
	print canteen, error1[0], error2[0], avg1, avg2, error1[0]/avg1, error2[0]/avg2
