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
from flask import request,Response,render_template,jsonify


#web api
api_name = "Imagenet Evaluation"
ip_addr = "192.168.0.116"
ip_port = 8007


#Database

database_ip = "localhost"
username = "li"
passwd = "issysesosakau"
database_name = "ImagenetDBT"
image_table = "ImageInfo"
preference_table = "ImagePreference"
relativity_table = "ImageRelativity"
description_table = "ImageDescription"
userinfo_table = "UserInfo"
synset_table = "SynsetMap"
level_table = "LevelTable"
db = databasehandler.DatabaseMySQL(database_ip,username,passwd,database_name)
user_info_columns = ["UserName","UserID"]
columns_imagetable = ["Class0WNID"]
level_column = ["RelativityNum"]

########################### Number and Level


user_id_list = {}
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
    column = ["RelativityNumber"]
    where_dic = {}
    where_dic["UserName"] = user_name
    result = db.select(userinfo_table,column,where_dic)
    user_number_list[user_name] = int(result[0][0])
    column = ["RelativityLevel"]
    result = db.select(userinfo_table,column,where_dic)
    user_level_list[user_name] = int(result[0][0])

print(user_id_list)
print(user_number_list)
print(user_level_list)

#Variables
status = "test"

#Const
RESPONSE_YES = 1
RESPONSE_NO = 2
RESPONSE_UNKONWN = 3


#Paths
base_path = "/home/li/webapi/"
user_path = base_path + "user/"
broken_image_list_path = "/home/li/datasets/broken_list_id.txt"
translate_file_path = "/home/li/datasets/imageinfo_wnid_translate.txt"
chinese_translate_file_path  = "/home/li/datasets/imageinfo_wnid_chinese.txt"
japanese_translate_file_path = "/home/li/datasets/imageinfo_wnid_japanese.txt"
valid_wnid_list_path = "/home/li/datasets/valid_wnid_list.txt"

################## Translate

chinese_dic = {}
japanese_dic = {}
wnid_list = []

with open(valid_wnid_list_path,'r') as wnid_f:
    for line in wnid_f.readlines():
        wnid_list.append(str(line[:9]))


with io.open(japanese_translate_file_path,'r',encoding='utf-8') as translate_f:
    for line in translate_f.readlines():
        line = line.strip('\n')
        l_list = line.split('\t')
        wnid = str(l_list[0])
        japanese = l_list[2]
        japanese_dic[wnid] = japanese



with io.open(chinese_translate_file_path,'r',encoding='utf-8') as translate_f:
    for line in translate_f.readlines():
        line = line.strip('\n')
        l_list = line.split('\t')
        wnid = str(l_list[0])
        chinese = l_list[2]
        chinese_dic[wnid] = chinese


#print(wnid_list)
category_num = len(wnid_list)
print(category_num)

##################

#Functions
def get_random_image():
    random_category_index = random.randint(0,category_num - 1)
    condition_dic = {}
    condition_dic["Class0WNID"] = wnid_list[random_category_index]
    columns = ["ImageName","IndexID","Path","Source","Class0Name","Class0WNID"]
    re = db.selectrandom(image_table,columns = columns, condition_dic = condition_dic)
    return re


def get_image(username):
    current_user_path = user_path + str(username) + "/"
    image_dic = get_random_image()
    image_file = image_dic["Path"] + image_dic["ImageName"] + ".jpg"
    image_id = int(image_dic["IndexID"])
    image_name = image_dic["Class0Name"]
    image_wnid = image_dic["Class0WNID"]
    trans_ja = japanese_dic[str(image_wnid)]
    trans_ch = chinese_dic[str(image_wnid)]
    with open(image_file,'r') as image_f:
        image_stream = image_f.read()
        image_stream = base64.b64encode(image_stream)

    return image_id,image_stream,image_name,image_wnid,trans_ja,trans_ch
    
    



app = flask.Flask(api_name)

@app.route('/home', methods = ['GET','POST'])
def home():
    return render_template('interface_v2_home.html',target = "relativity")


@app.route('/login', methods = ['POST','GET'])
def login():
    username = request.form.get("username")
    
    print(username)
    if username==None:
        return render_template('interface_v2_home.html',target = "relativity")

    username = str(username).lower()
    current_user_path = user_path + str(username) + "/"
    userinfo_file_path = current_user_path + "info.txt"
    userlog_file_path = current_user_path + "relativity_log.txt"

    
    if username in user_id_list.keys():
        userid = user_id_list[username]
    else:
        userid = len(user_id_list.keys())
        user_id_list[username] = int(userid)
        user_number_list[username] = 0
        user_level_list[username] = 0
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

    current_image_list = []
    base_image_id,base_image_stream,base_image_name,base_image_wnid,base_image_trans_ja,base_image_trans_ch = get_image(username)
    current_image_list.append(base_image_wnid)
    
    sub_image1_id,sub_image1_stream,sub_image1_name,sub_image1_wnid,sub_image1_trans_ja,sub_image1_trans_ch = get_image(username)
    while sub_image1_wnid in current_image_list:
        sub_image1_id,sub_image1_stream,sub_image1_name,sub_image1_wnid,sub_image1_trans_ja,sub_image1_trans_ch = get_image(username)
    current_image_list.append(sub_image1_wnid)

    sub_image2_id,sub_image2_stream,sub_image2_name,sub_image2_wnid,sub_image2_trans_ja,sub_image2_trans_ch = get_image(username)
    while sub_image2_wnid in current_image_list:
        sub_image2_id,sub_image2_stream,sub_image2_name,sub_image2_wnid,sub_image2_trans_ja,sub_image2_trans_ch = get_image(username)
    current_image_list.append(sub_image2_wnid)

    sub_image3_id,sub_image3_stream,sub_image3_name,sub_image3_wnid,sub_image3_trans_ja,sub_image3_trans_ch = get_image(username)
    while sub_image3_wnid in current_image_list:
        sub_image3_id,sub_image3_stream,sub_image3_name,sub_image3_wnid,sub_image3_trans_ja,sub_image3_trans_ch = get_image(username)
    current_image_list.append(sub_image3_wnid)

    
    sub_image4_id,sub_image4_stream,sub_image4_name,sub_image4_wnid,sub_image4_trans_ja,sub_image4_trans_ch = get_image(username)
    while sub_image4_wnid in current_image_list:
        sub_image4_id,sub_image4_stream,sub_image4_name,sub_image4_wnid,sub_image4_trans_ja,sub_image4_trans_ch = get_image(username)
    current_image_list.append(sub_image4_wnid)

    user_number = user_number_list[str(username)]
    user_level = user_level_list[str(username)]
    current_level_num = level_list[user_level]
    next_level_num = level_list[user_level + 1]
    complete_ratio = int((100 * (user_number - current_level_num))/(next_level_num - current_level_num))
        

    return render_template("interface_v2_relativity_horizontal.html",UserName = username,UserID = userid,
                           BaseImageID = base_image_id,
                           BaseImageStream = base_image_stream,
                           BaseImageName = base_image_name,
                           BaseImageWNID = base_image_wnid,
                           BaseTranslateJa = base_image_trans_ja, BaseTranslateCh = base_image_trans_ch,
                           SubImageID1 = sub_image1_id,
                           SubImageStream1 = sub_image1_stream,
                           SubImageName1 = sub_image1_name,
                           SubImageWNID1 = sub_image1_wnid,
                           SubTranslateJa1 = sub_image1_trans_ja,SubTranslateCh1 = sub_image1_trans_ch,
                           SubImageID2 = sub_image2_id,
                           SubImageStream2 = sub_image2_stream,
                           SubImageName2 = sub_image2_name,
                           SubImageWNID2 = sub_image2_wnid,
                           SubTranslateJa2 = sub_image2_trans_ja,SubTranslateCh2 = sub_image2_trans_ch,
                           SubImageID3 = sub_image3_id,
                           SubImageStream3 = sub_image3_stream,
                           SubImageName3 = sub_image3_name,
                           SubImageWNID3 = sub_image3_wnid,
                           SubTranslateJa3 = sub_image3_trans_ja,SubTranslateCh3 = sub_image3_trans_ch,
                           SubImageID4 = sub_image4_id,
                           SubImageStream4 = sub_image4_stream,
                           SubImageName4 = sub_image4_name,
                           SubImageWNID4 = sub_image4_wnid,
                           SubTranslateJa4 = sub_image4_trans_ja,SubTranslateCh4 = sub_image4_trans_ch,
                           UserNumber = user_number, UserLevel = user_level,
                           CompleteRatio = complete_ratio)
       


@app.route('/log', methods=['POST'])
def log():
    log_dic = {}
    username = request.form["UserName"]
    userid = request.form["UserID"]
    current_user_path = user_path + str(username) + "/"
    userinfo_file_path = current_user_path + "info.txt"
    userlog_file_path = current_user_path + "relativity_log.txt"
    
    base_image_id = request.form["BaseImageID"]
    base_image_wnid = request.form["BaseImageWNID"]
    sub_image1_id = request.form["SubImage1ID"]
    sub_image1_wnid = request.form["SubImage1WNID"]
    sub_image2_id = request.form["SubImage2ID"]
    sub_image2_wnid = request.form["SubImage2WNID"]
    sub_image3_id = request.form["SubImage3ID"]
    sub_image3_wnid = request.form["SubImage3WNID"]
    sub_image4_id = request.form["SubImage4ID"]
    sub_image4_wnid = request.form["SubImage4WNID"]

    
    if (username == "test"):
        status = "test"
    else:
        status = "log"
    
    
    log_dic = {}
    log_dic["UserName"] = str(username)
    log_dic["UserID"] = str(userid)
    log_dic["ImageID_1"] = str(base_image_id)
    log_dic["ImageClassWNID_1"] = str(base_image_wnid)
    log_dic["Status"] = str(status)

    relativity1 = int(request.form["SubImage1Relativity"])
    if relativity1 == RESPONSE_YES:
        log_dic["ImageID_2"] = str(sub_image1_id)
        log_dic["ImageClassWNID_2"] = str(sub_image1_wnid)
        log_dic["Relativity"] = "yes"
        
    elif relativity1 == RESPONSE_NO:
        log_dic["ImageID_2"] = str(sub_image1_id)
        log_dic["ImageClassWNID_2"] = str(sub_image1_wnid)
        log_dic["Relativity"] = "no"
        
    else:
        log_dic["ImageID_2"] = str(sub_image1_id)
        log_dic["ImageClassWNID_2"] = str(sub_image1_wnid)
        log_dic["Relativity"] = "NULL"
        
    try:
        db.insert(relativity_table,log_dic)
    except:
        pass

    if os.path.exists(userlog_file_path):
        with open(userlog_file_path,'a') as userlog_f:
            userlog_f.write(json.dumps(log_dic) + "\n")
    else:
        with open(userlog_file_path,'w') as userlog_f:
            userlog_f.write(json.dumps(log_dic) + "\n")

    relativity2 = int(request.form["SubImage2Relativity"])
    if relativity2 == RESPONSE_YES:
        log_dic["ImageID_2"] = str(sub_image2_id)
        log_dic["ImageClassWNID_2"] = str(sub_image2_wnid)
        log_dic["Relativity"] = "yes"
        
    elif relativity2 == RESPONSE_NO:
        log_dic["ImageID_2"] = str(sub_image2_id)
        log_dic["ImageClassWNID_2"] = str(sub_image2_wnid)
        log_dic["Relativity"] = "no"
        
    else:
        log_dic["ImageID_2"] = str(sub_image2_id)
        log_dic["ImageClassWNID_2"] = str(sub_image2_wnid)
        log_dic["Relativity"] = "NULL"
        
    try:
        db.insert(relativity_table,log_dic)
    except:
        pass

    if os.path.exists(userlog_file_path):
        with open(userlog_file_path,'a') as userlog_f:
            userlog_f.write(json.dumps(log_dic) + "\n")
    else:
        with open(userlog_file_path,'w') as userlog_f:
            userlog_f.write(json.dumps(log_dic) + "\n")

    relativity3 = int(request.form["SubImage3Relativity"])
    if relativity3 == RESPONSE_YES:
        log_dic["ImageID_2"] = str(sub_image3_id)
        log_dic["ImageClassWNID_2"] = str(sub_image3_wnid)
        log_dic["Relativity"] = "yes"
        
    elif relativity3 == RESPONSE_NO:
        log_dic["ImageID_2"] = str(sub_image3_id)
        log_dic["ImageClassWNID_2"] = str(sub_image3_wnid)
        log_dic["Relativity"] = "no"
        
    else:
        log_dic["ImageID_2"] = str(sub_image3_id)
        log_dic["ImageClassWNID_2"] = str(sub_image3_wnid)
        log_dic["Relativity"] = "NULL"
        
    try:
        db.insert(relativity_table,log_dic)
    except:
        pass

    if os.path.exists(userlog_file_path):
        with open(userlog_file_path,'a') as userlog_f:
            userlog_f.write(json.dumps(log_dic) + "\n")
    else:
        with open(userlog_file_path,'w') as userlog_f:
            userlog_f.write(json.dumps(log_dic) + "\n")

    relativity4 = int(request.form["SubImage4Relativity"])
    if relativity4 == RESPONSE_YES:
        log_dic["ImageID_2"] = str(sub_image4_id)
        log_dic["ImageClassWNID_2"] = str(sub_image4_wnid)
        log_dic["Relativity"] = "yes"
        
    elif relativity4 == RESPONSE_NO:
        log_dic["ImageID_2"] = str(sub_image4_id)
        log_dic["ImageClassWNID_2"] = str(sub_image4_wnid)
        log_dic["Relativity"] = "no"
        
    else:
        log_dic["ImageID_2"] = str(sub_image4_id)
        log_dic["ImageClassWNID_2"] = str(sub_image4_wnid)
        log_dic["Relativity"] = "NULL"

    try:
        db.insert(relativity_table,log_dic)
    except:
        pass

    if os.path.exists(userlog_file_path):
        with open(userlog_file_path,'a') as userlog_f:
            userlog_f.write(json.dumps(log_dic) + "\n")
    else:
        with open(userlog_file_path,'w') as userlog_f:
            userlog_f.write(json.dumps(log_dic) + "\n")

    where_dic = {}
    where_dic["UserName"] = str(username)
    user_log_dic = {}
    user_number_list[str(username)] += 4
    user_log_dic["RelativityNumber"] = str(user_number_list[str(username)])
    if user_number_list[str(username)] >= level_list[user_level_list[str(username)] + 1]:
        user_level_list[str(username)] += 1
    user_log_dic["RelativityLevel"] = str(user_level_list[str(username)])
    try:
        db.update(userinfo_table,user_log_dic,condition_dic = where_dic)
    except:
        pass

    
    
        
    return "yes"


@app.route('/next', methods=['POST'])
def next_image():
    username = request.form["UserName"]
    userid = request.form["UserID"]
    
    return "yes"
   

@app.route('/broken', methods=['POST'])
def broken():
    username = request.form["UserName"]
    userid = request.form["UserID"]
    broken_imageid = request.form["BrokenID"]
    print(broken_imageid)
    with open(broken_image_list_path,'a') as broken_f:
        broken_f.write(str(broken_imageid) + "\n")
        
    return "yes"
   


if __name__ == '__main__':
    try:
        app.run(debug = True,host = ip_addr, port = ip_port)
        
    finally:
        print("server close!")
        db.close()
