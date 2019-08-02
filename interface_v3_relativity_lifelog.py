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
import pandas as pd
from wordcloud import WordCloud
from flask import request,Response,render_template,jsonify


#web api
api_name = "Imagenet Evaluation"
ip_addr = "192.168.0.116"
ip_port = 8009


#Database
database_ip = "localhost"
username = "li"
passwd = "issysesosakau"
database_name = "ImagenetDBT"
raw_data_table = "LifeLogItemDataRaw"
userinfo_table = "UserInfo"
level_table = "LevelTable"
lifelog_table = "LifeLogItem"
db = databasehandler.DatabaseMySQL(database_ip,username,passwd,database_name)
user_info_columns = ["UserName","UserID"]


#Variables
status = "test"
wordcloud_width = 600
wordcloud_height = 400
prefer_horizontal = 0.9
max_words = 30
max_font_size = 40
min_font_size = 10
background_color = "white"
item_number = 8
item_total_number = 64
circle = item_total_number / item_number


#CONST
ENGLISH = 1
JAPANESE = 2
CHINESE = 3


############################# Number and Level

group_path = "/home/li/datasets/lifelog/Group1_64.txt"
lifelog_itemlist = "/home/li/datasets/lifelog/itemlist.csv"


lifelog_data = pd.read_csv(lifelog_itemlist)
user_id_list = {}
user_number_list = {}
user_eva_list = {}
group_list = []
group_item_name_list = []

with open(group_path,"r") as g_f:
    for line in g_f.readlines():
        group_list.append(int(line.strip()))
        group_item_name_list.append(lifelog_data.loc[int(line.strip()) -1,"Name"])

print(group_item_name_list)

re = db.selectdistinct(userinfo_table,user_info_columns)
for user in re:
    user_id_list[user[0]] = int(user[1])
    user_name = str(user[0])
    user_id = int(user[1])
    column = ["LifeLogRelativityNumber"]
    where_dic = {}
    where_dic["UserName"] = user_name
    result = db.select(userinfo_table,column,where_dic)
    user_number_list[user_name] = int(result[0][0])

    sample_list = []
    sample = random.sample(group_list,len(group_list))
    #print(sample)
    for i in range(circle):
        eva_sample = sample[item_number * i: item_number * (i + 1)]
        sample_list.append(eva_sample)
    user_eva_list[user_name] = sample_list

    

    

#print(user_eva_list)









#Paths
base_path = "/home/li/webapi/"
user_path = base_path + "user/"



japanese_fonts_path = "/usr/share/fonts/truetype/fonts-japanese-mincho.ttf"
chinese_fonts_path = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"


################## Dataset




#print(wnid_list)


##################

#Functions
def update_eva_list(user_name):
    sample_list = []
    sample = random.sample(group_list,len(group_list))
    for i in range(circle):
        eva_sample = sample[item_number * i: item_number * (i + 1)]
        sample_list.append(eva_sample)
    user_eva_list[user_name] = sample_list




def get_image_path(index_id):
    condition_dic = {}
    condition_dic["ItemID"] = str(index_id)
    columns = ["ImagePath"]
    re = db.select(lifelog_table,columns = columns, condition_dic = condition_dic)
    return str(re[0][0])



def get_item_list(username,eva_number,language):

    item_name_list = []
    item_id_list = []
    item_info_list = []
    item_stream_list = []
    item_origin_name_list = []

    sample_index = eva_number % circle
    if sample_index == 0:
        update_eva_list(username)

    sample = user_eva_list[username][sample_index]

    for index_id in sample:
        item_id_list.append(index_id)
        item_origin_name_list.append(unicode(lifelog_data.loc[int(index_id - 1),"Name"],"utf-8"))
        if language == ENGLISH:
            item_name_list.append(unicode(lifelog_data.loc[int(index_id - 1),"Name"],"utf-8"))
            display_language = "english"
        elif language == CHINESE:
            item_name_list.append(unicode(lifelog_data.loc[int(index_id - 1),"Chinese name"],"utf-8"))
            display_language = "chinese"
        elif language == JAPANESE:
            item_name_list.append(unicode(lifelog_data.loc[int(index_id - 1),"Japanese name"],"utf-8"))
            display_language = "japanese"
        information = str(lifelog_data.loc[int(index_id - 1),"Name"]) + "\t" + lifelog_data.loc[int(index_id - 1),"Chinese name"] + "\t" + lifelog_data.loc[int(index_id - 1),"Japanese name"] + "\t" + lifelog_data.loc[int(index_id - 1),"description"]
        information = unicode(information,"utf-8")
        item_info_list.append(information)
        print(information)
        image_path = get_image_path(index_id)
        with open(image_path,'r') as image_f:
            image_stream = image_f.read()
            image_stream = base64.b64encode(image_stream)
        item_stream_list.append(image_stream)
    

    return item_name_list,item_origin_name_list,item_id_list,item_info_list,item_stream_list,display_language
    
    



app = flask.Flask(api_name)
@app.route('/home', methods = ['GET','POST'])
def home():
    return render_template('interface_v3_home_relativity_lifelog.html')



@app.route('/login', methods = ['POST','GET'])
def login():
    username = request.form.get("username")
    
    print(username)
    if username==None:
        return render_template('interface_v3_home_relativity_lifelog.html')

    username = str(username).lower()
    current_user_path = user_path + str(username) + "/"
    userinfo_file_path = current_user_path + "info.txt"
    userlog_file_path = current_user_path + "relativity_log.txt"
    language = int(request.form.get("language"))

    
    if username in user_id_list.keys():
        userid = user_id_list[username]
    else:
        userid = len(user_id_list.keys())
        user_id_list[username] = int(userid)
        user_number_list[username] = 0
        user_eva_list[username] = 0
        userinfo_dic = {}
        userinfo_dic["UserName"] = username
        userinfo_dic["UserID"] = str(userid)
        userinfo_dic["PreferenceNumber"] = 0
        userinfo_dic["RelativityNumber"] = 0
        userinfo_dic["SimilarityNumber"] = 0
        userinfo_dic["PreferenceLevel"] = 0
        userinfo_dic["RelativityLevel"] = 0
        userinfo_dic["SimilarityLevel"] = 0
        userinfo_dic["LifeLogRelativityNumber"] = 0
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


    eva_number = user_number_list[username]
    item_name_list,item_origin_name_list,item_id_list,item_info_list,item_stream_list,display_language = get_item_list(username,eva_number,language)

    return render_template("interface_v3_relativity_lifelog.html",UserName = username,UserID = userid,
                           ItemID_0 = item_id_list[0], ItemOriginName_0 = item_origin_name_list[0], ItemName_0 = item_name_list[0], ItemInfo_0 = item_info_list[0], ItemStream_0 = item_stream_list[0],
                           ItemID_1 = item_id_list[1], ItemOriginName_1 = item_origin_name_list[1], ItemName_1 = item_name_list[1], ItemInfo_1 = item_info_list[1], ItemStream_1 = item_stream_list[1],
                           ItemID_2 = item_id_list[2], ItemOriginName_2 = item_origin_name_list[2], ItemName_2 = item_name_list[2], ItemInfo_2 = item_info_list[2], ItemStream_2 = item_stream_list[2],
                           ItemID_3 = item_id_list[3], ItemOriginName_3 = item_origin_name_list[3], ItemName_3 = item_name_list[3], ItemInfo_3 = item_info_list[3], ItemStream_3 = item_stream_list[3],
                           ItemID_4 = item_id_list[4], ItemOriginName_4 = item_origin_name_list[4], ItemName_4 = item_name_list[4], ItemInfo_4 = item_info_list[4], ItemStream_4 = item_stream_list[4],
                           ItemID_5 = item_id_list[5], ItemOriginName_5 = item_origin_name_list[5], ItemName_5 = item_name_list[5], ItemInfo_5 = item_info_list[5], ItemStream_5 = item_stream_list[5],
                           ItemID_6 = item_id_list[6], ItemOriginName_6 = item_origin_name_list[6], ItemName_6 = item_name_list[6], ItemInfo_6 = item_info_list[6], ItemStream_6 = item_stream_list[6],
                           ItemID_7 = item_id_list[7], ItemOriginName_7 = item_origin_name_list[7], ItemName_7 = item_name_list[7], ItemInfo_7 = item_info_list[7], ItemStream_7 = item_stream_list[7],
                           UserNumber = eva_number,
                           Language = display_language)
       


@app.route('/log', methods=['POST'])
def log():

    print(request.form)
    
    log_dic = {}
    username = request.form["UserName"]
    userid = request.form["UserID"]
    log_dic["UserName"] = str(username)
    log_dic["UserID"] = str(userid)
    log_dic["Attribute"] = "Relativity"
    current_user_path = user_path + str(username) + "/"
    userinfo_file_path = current_user_path + "info.txt"
    userlog_file_path = current_user_path + "relativity_v3_log.txt"


    where_dic = {}
    where_dic["UserID"] = str(userid)
    columns = ["UserRecordID"]
    user_number_list[username] += 1
    log_dic["UserRecordID"] = int(user_number_list[username])

    update_dic = {}
    update_dic["LifeLogRelativityNumber"] = str(user_number_list[username])
    db.update(userinfo_table,update_dic,where_dic)
    

    
                

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
        
        

    '''
    try:
        db.insert(preference_table,log_dic)
    except:
        pass

    user_number_list[str(username)] += 1
    user_log_dic = {}
    where_dic = {}
    where_dic["UserName"] = str(username)
    user_log_dic["PreferenceNumber"] = str(user_number_list[str(username)])
    if user_number_list[str(username)] >= level_list[user_level_list[str(username)] + 1]:
        user_level_list[str(username)] += 1
    user_log_dic["PreferenceLevel"] = str(user_level_list[str(username)])
    try:
        db.update(userinfo_table,user_log_dic,condition_dic = where_dic)
    except:
        pass
    '''
        
    
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
