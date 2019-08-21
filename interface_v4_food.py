#!/usr/bin/env python2
# -*- coding: UTF-8 -*-

import flask
import databasehandler
import json
import time
import os
import io
import random
import base64
import pandas as pd
from flask import request,Response,render_template,jsonify

#web api
api_name = "Food_Choice"
ip_addr = "192.168.0.116"
ip_port = 8009

#Database
database_ip = "localhost"
username = "li"
passwd = "issysesosakau"
database_name = "Interface2"
raw_data_table = "Interface2DataRawAB"
userinfo_table = "UserInfo"
db = databasehandler.DatabaseMySQL(database_ip, username, passwd, database_name)
user_info_columns = ["UserName","UserID","DataNumber"]


#Path
list_csv_path = "/home/li/webapi/domain/combine_lists.csv"
image_path = "/home/li/webapi/domain/domain_food/"
extra_txt_path = "/home/li/webapi/domain/extra.txt"

#Variables
status = "test"
item_number = 4
list_csv = pd.read_csv(list_csv_path)
A_list_len = len(list_csv.A)
B_list_len = len(list_csv.B)



########################################

#User List
user_id_dic = {}
user_number_dic = {}
re = db.selectdistinct(userinfo_table, user_info_columns)
for user in re:
    user_id_dic[user[0]] = int(user[1])
    user_number_dic[user[0]] = int(user[2])

#Image List
image_stream_list = []
for i in range(C_list_len):
    image_name = image_path + "re" + str(i) + ".jpg"
    #print(image_name)
    with open(image_name,'r') as image_f:
        image_stream = image_f.read()
        image_stream = base64.b64encode(image_stream)
    image_stream_list.append(image_stream)


#Extra
extra_list = []
with open(extra_txt_path, 'r') as extra_f:
    for line in extra_f.readlines():
        extra_list.append(unicode(str(line).strip(), "utf-8"))


app = flask.Flask(api_name)
@app.route('/home', methods = ['GET','POST'])
def home():
    return render_template('interface_v4_home.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    username = request.form.get("username")

    if username == None:
        return render_template('interface_v4_home.html')
    username = str(username).lower()
    if username in user_id_dic.keys():
        userid = user_id_dic[username]
    else:
        userid = len(user_id_dic.keys())
        user_number_dic[username] = 0
        userinfo_dic = {}
        userinfo_dic["UserName"] = username
        userinfo_dic["UserID"] = userid
        userinfo_dic["DataNumber"] = 0
        db.insert(userinfo_table, userinfo_dic)

    A_choice = random.choice(range(A_list_len))
    B_sample = random.sample(range(B_list_len), 4)

    print(A_choice)
    print(B_choice)
    print(C_sample)
    
    return render_template("interface_v4_food.html", UserName = username, UserID = userid, DataNumber = user_number_dic[username],
                           CONDITION_ID = A_choice, WHO_NAME = unicode(list_csv.loc[A_choice,"A"], "utf-8"),
                           CHOICE_1_ID = B_sample[0], CHOICE_1_NAME = unicode(list_csv.loc[B_sample[0],"B"], "utf-8"), CHOICE_1_ImageStream = image_stream_list[B_sample[0]],
                           CHOICE_2_ID = B_sample[1], CHOICE_2_NAME = unicode(list_csv.loc[B_sample[1],"B"], "utf-8"), CHOICE_2_ImageStream = image_stream_list[B_sample[1]],
                           CHOICE_3_ID = B_sample[2], CHOICE_3_NAME = unicode(list_csv.loc[B_sample[2],"B"], "utf-8"), CHOICE_3_ImageStream = image_stream_list[B_sample[2]],
                           CHOICE_4_ID = B_sample[3], CHOICE_4_NAME = unicode(list_csv.loc[B_sample[3],"B"], "utf-8"), CHOICE_4_ImageStream = image_stream_list[B_sample[3]],
                           EXTRA_1 = extra_list[1]
                           )


@app.route('/log', methods = ['POST'])
def log():
    log_dic = {}
    username = request.form["UserName"]
    userid = request.form["UserID"]
    log_dic["UserName"] = str(username)
    log_dic["UserID"] = str(userid)
    log_dic["Status"] = status
    log_dic["AListID"] = int(request.form["AListID"])
    log_dic["BListID"] = int(request.form["BListID"])
    log_dic["CListID1"] = int(request.form["CListID1"])
    log_dic["CListID2"] = int(request.form["CListID2"])
    log_dic["CListID3"] = int(request.form["CListID3"])
    log_dic["CListID4"] = int(request.form["CListID4"])
    log_dic["CListSelectID"] = int(request.form["CListSelectID"])
    log_dic["ResponseTime"] = "%.2f" % float(request.form["ResponseTime"])
    #print(log_dic)
    db.insert(raw_data_table, log_dic)

    user_number_dic[username] += 1
    update_dic = {}
    update_dic["DataNumber"] = str(user_number_dic[username])
    where_dic = {}
    where_dic["UserID"] = str(userid)
    db.update(userinfo_table, update_dic, where_dic)
    
    return "yes"



if __name__ == '__main__':
    try:
        app.run(debug = True, host = ip_addr, port = ip_port)
    finally:
        print("server close")
        db.close()

