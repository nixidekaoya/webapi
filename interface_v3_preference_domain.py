#!/usr/bin/env python2
# -*- coding: UTF-8 -*-

import flask
import databasehandler
import json
import time
import os
import io
import cv2
import random
import base64
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from flask import request,Response,render_template,jsonify


#web api
api_name = "Imagenet Evaluation"
ip_addr = "192.168.0.116"
ip_port = 8008


#Database
database_ip = "localhost"
username = "li"
passwd = "issysesosakau"
database_name = "ImagenetDBT"
image_table = "ImageInfo"
preference_table = "ItemPreference"
relativity_table = "ItemRelativity"
description_table = "ItemDescription"
raw_data_table = "DomainItemDataRaw"
userinfo_table = "UserInfo"
synset_table = "SynsetMap"
level_table = "LevelTable"
db = databasehandler.DatabaseMySQL(database_ip,username,passwd,database_name)
user_info_columns = ["UserName","UserID"]
level_column = ["PreferenceNum"]


domain_table = "DomainItem"


############################# Number and Level


user_id_list = {}
user_complete_dic = {}
user_number_list = {}
user_level_list = {}
level_list = []
level_list.append(int(0))
result_1 = db.select(level_table,level_column)

for level in result_1:
    level_list.append(int(level[0]))


re = db.selectdistinct(userinfo_table,user_info_columns)
for user in re:
    user_id_list[user[0]] = int(user[1])
    user_name = str(user[0])
    user_id = int(user[1])
    column = ["PreferenceNumber"]
    where_dic = {}
    where_dic["UserName"] = user_name
    result = db.select(userinfo_table,column,where_dic)
    user_number_list[user_name] = int(result[0][0])
    column = ["PreferenceLevel"]
    result = db.select(userinfo_table,column,where_dic)
    user_level_list[user_name] = int(result[0][0])
    user_complete_dic[user_name] = 0
    


#Variables
status = "test"
wordcloud_width = 600
wordcloud_height = 400
prefer_horizontal = 0.9
max_words = 30
max_font_size = 40
min_font_size = 10
background_color = "white"
item_number = 10


#CONST
ENGLISH = 1
JAPANESE = 2
CHINESE = 3



#Paths
base_path = "/home/li/webapi/"
user_path = base_path + "user/"
broken_image_list_path = "/home/li/datasets/broken_list_id.txt"


japanese_fonts_path = "/usr/share/fonts/truetype/fonts-japanese-mincho.ttf"
chinese_fonts_path = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"


domain_list_path = "/home/li/datasets/domain/domain_list.txt"
domain_table_path = "/home/li/datasets/domain/item_table.txt"
domain_item_name_path = "/home/li/datasets/domain/item_name.txt"

################## Translate

domain_list = []

item_name_dic = {}

with open(domain_list_path) as domain_list_file:
    for line in domain_list_file.readlines():
        domain_list.append(line.strip())

with io.open(domain_table_path,'r',encoding = "utf-8") as domain_table_file:
    for line in domain_table_file.readlines():
        lines = line.strip().split(',')
        item_origin_name = lines[0]
        item_domain = lines[1]
        item_domain_id = lines[2]
        item_name = lines[3]
        item_name_dic[str(item_name)] = item_origin_name
        #print(lines)



#print(wnid_list)
domain_num = len(domain_list)
print(domain_num)

##################

#Functions

def get_item_by_domain(domain):
    columns = ["ItemID","ItemDomainID","ItemName","ItemImagePath"]
    item_id_list = []
    item_domain_id_list = []
    item_name_list = []
    item_image_stream_list = []
    item_origin_name_list = []
    
    
    condition_dic = {}
    condition_dic["ItemDomain"] = str(domain)
    re = db.select(domain_table,columns,condition_dic)

    random_list = random.sample(range(len(re)),item_number)
    
    for number in random_list:
        sample = re[number]
        item_id_list.append(sample[0])
        item_domain_id_list.append(sample[1])
        item_name_list.append(sample[2])
        item_origin_name_list.append(item_name_dic[str(sample[2])])
        with open(str(sample[3]),'r') as image_f:
            image_stream = image_f.read()
            image_stream = base64.b64encode(image_stream)
        item_image_stream_list.append(image_stream)
    
    return item_id_list,item_domain_id_list,item_name_list,item_origin_name_list,item_image_stream_list
    



app = flask.Flask(api_name)
@app.route('/home', methods = ['GET','POST'])
def home():
    return render_template('interface_v3_home_preference_domain.html')



@app.route('/login', methods = ['POST','GET'])
def login():
    username = request.form.get("username")
    
    print(username)
    if username==None:
        return render_template('interface_v3_home_preference_domain.html')

    username = str(username).lower()
    current_user_path = user_path + str(username) + "/"
    userinfo_file_path = current_user_path + "info.txt"
    userlog_file_path = current_user_path + "preference_log.txt"

    
    if username in user_id_list.keys():
        userid = user_id_list[username]
    else:
        userid = len(user_id_list.keys())
        user_id_list[username] = int(userid)
        user_number_list[username] = 0
        user_level_list[username] = 0
        user_complete_dic[username] = 0
        userinfo_dic = {}
        userinfo_dic["UserName"] = username
        userinfo_dic["UserID"] = str(userid)
        userinfo_dic["PreferenceNumber"] = 0
        userinfo_dic["RelativityNumber"] = 0
        userinfo_dic["SimilarityNumber"] = 0
        userinfo_dic["PreferenceLevel"] = 0
        userinfo_dic["RelativityLevel"] = 0
        userinfo_dic["SimilarityLevel"] = 0
        db.insert(userinfo_table,userinfo_dic)
    
    if os.path.exists(current_user_path):
        i = 1
    else:
        os.mkdir(current_user_path)
        userinfo_file = open(userinfo_file_path,'w')
        userinfo_dic = {}
        userinfo_dic["UserName"] = username
        userinfo_dic["UserID"] = int(userid)
        userinfo_file.write(json.dumps(userinfo_dic) + "\n")
        userinfo_file.close()
        userlog_file = open(userlog_file_path,'w')
        userlog_file.close()


    domain_index = int(user_complete_dic[username])
    if domain_index >= domain_num:
        return render_template("interface_v3_over.html")

    domain = domain_list[domain_index]
    item_id_list,item_domain_id_list,item_name_list,item_origin_name_list,item_stream_list = get_item_by_domain(domain)
    

    return render_template("interface_v3_preference_domain.html",UserName = username,UserID = userid,
                           ItemID_0 = item_id_list[0], ItemDomainID_0 = item_domain_id_list[0], ItemName_0 = item_name_list[0], ItemOriginName_0 = item_origin_name_list[0], ItemStream_0 = item_stream_list[0],
                           ItemID_1 = item_id_list[1], ItemDomainID_1 = item_domain_id_list[1], ItemName_1 = item_name_list[1], ItemOriginName_1 = item_origin_name_list[1], ItemStream_1 = item_stream_list[1],
                           ItemID_2 = item_id_list[2], ItemDomainID_2 = item_domain_id_list[2], ItemName_2 = item_name_list[2], ItemOriginName_2 = item_origin_name_list[2], ItemStream_2 = item_stream_list[2],
                           ItemID_3 = item_id_list[3], ItemDomainID_3 = item_domain_id_list[3], ItemName_3 = item_name_list[3], ItemOriginName_3 = item_origin_name_list[3], ItemStream_3 = item_stream_list[3],
                           ItemID_4 = item_id_list[4], ItemDomainID_4 = item_domain_id_list[4], ItemName_4 = item_name_list[4], ItemOriginName_4 = item_origin_name_list[4], ItemStream_4 = item_stream_list[4],
                           ItemID_5 = item_id_list[5], ItemDomainID_5 = item_domain_id_list[5], ItemName_5 = item_name_list[5], ItemOriginName_5 = item_origin_name_list[5], ItemStream_5 = item_stream_list[5],
                           ItemID_6 = item_id_list[6], ItemDomainID_6 = item_domain_id_list[6], ItemName_6 = item_name_list[6], ItemOriginName_6 = item_origin_name_list[6], ItemStream_6 = item_stream_list[6],
                           ItemID_7 = item_id_list[7], ItemDomainID_7 = item_domain_id_list[7], ItemName_7 = item_name_list[7], ItemOriginName_7 = item_origin_name_list[7], ItemStream_7 = item_stream_list[7],
                           ItemID_8 = item_id_list[8], ItemDomainID_8 = item_domain_id_list[8], ItemName_8 = item_name_list[8], ItemOriginName_8 = item_origin_name_list[8], ItemStream_8 = item_stream_list[8],
                           ItemID_9 = item_id_list[9], ItemDomainID_9 = item_domain_id_list[9], ItemName_9 = item_name_list[9], ItemOriginName_9 = item_origin_name_list[9], ItemStream_9 = item_stream_list[9],
                           Domain = domain)
       


@app.route('/log', methods=['POST'])
def log():

    print(request.form)
    
    log_dic = {}
    username = request.form["UserName"]
    userid = request.form["UserID"]
    log_dic["UserName"] = str(username)
    log_dic["UserID"] = str(userid)
    log_dic["Attribute"] = "Preference"
    log_dic["ItemDomain"] = str(request.form["Domain"])
    current_user_path = user_path + str(username) + "/"
    userinfo_file_path = current_user_path + "info.txt"
    userlog_file_path = current_user_path + "preference_v3_log.txt"
    user_complete_dic[username] += 1

                

    if (username == "test"):
        status = "test"
    else:
        status = "log"

    log_dic["Status"] = status
    for i in range(item_number):
        id_text = "ItemID_" + str(i+1)
        name_text = "ItemName_" + str(i+1)
        x_coordinate_text = "X_Coordinate_" + str(i+1)
        y_coordinate_text = "Y_Coordinate_" + str(i+1)
        log_dic["ItemID"] = str(request.form[id_text])
        log_dic["ItemName"] = str(request.form[name_text])
        log_dic["CoordinatesX"] = "%.10f" % float(request.form[x_coordinate_text])
        log_dic["CoordinatesY"] = "%.10f" % float(request.form[y_coordinate_text])
        db.insert(raw_data_table,log_dic)
        
        
        
    
    if os.path.exists(userlog_file_path):
        with open(userlog_file_path,'a') as userlog_f:
            userlog_f.write(json.dumps(log_dic) + "\n")
    else:
        with open(userlog_file_path,'w') as userlog_f:
            userlog_f.write(json.dumps(log_dic) + "\n")
        
    return "yes"

   

   


if __name__ == '__main__':
    try:
        app.run(debug = True,host = ip_addr, port = ip_port)
        
    finally:
        print("server close!")
        db.close()
