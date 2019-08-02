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
ip_port = 8005


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
db = databasehandler.DatabaseMySQL(database_ip,username,passwd,database_name)
user_info_columns = ["UserName","UserID"]
columns_imagetable = ["Class0WNID"]
re = db.selectdistinct(preference_table,user_info_columns)
user_id_list = {}
for user in re:
    user_id_list[user[0]] = int(user[1])
print(user_id_list)

#Variables
status = "test"


#Paths
base_path = "/home/li/webapi/"
user_path = base_path + "user/"
broken_image_list_path = "/home/li/datasets/broken_list_id.txt"
translate_file_path = "/home/li/datasets/imageinfo_wnid_translate.txt"
chinese_translate_file_path  = "/home/li/datasets/imageinfo_wnid_chinese.txt"
japanese_translate_file_path = "/home/li/datasets/imageinfo_wnid_japanese.txt"

################## Translate

chinese_dic = {}
japanese_dic = {}
wnid_list = []

re = db.selectdistinct(image_table,columns_imagetable)
for wnid_taple in re:
    wnid_list.append(wnid_taple[0])

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


def update_image(username):
    current_user_path = user_path + str(username) + "/"
    eva_image_path = current_user_path + "evaluate_image.jpg"
    com_image_path = current_user_path + "compare_image.jpg"
    imageinfo_file_path = current_user_path + "image_info.txt"
    eva_image_dic = get_random_image()
    eva_image_file = eva_image_dic["Path"] + eva_image_dic["ImageName"] + ".jpg"
    com_image_dic = get_random_image()
    com_image_file = com_image_dic["Path"] + com_image_dic["ImageName"] + ".jpg"
    eva_image_id = int(eva_image_dic["IndexID"])
    com_image_id = int(com_image_dic["IndexID"])
    eva_image_name = eva_image_dic["Class0Name"]
    eva_image_wnid = eva_image_dic["Class0WNID"]
    com_image_name = com_image_dic["Class0Name"]
    com_image_wnid = com_image_dic["Class0WNID"]
    img_dic = {}
    img_dic["Evaluation ID"] = eva_image_id
    img_dic["Compare ID"] = com_image_id
    img_dic["Evaluation Name"] = eva_image_name
    img_dic["Compare Name"] = com_image_name
    imageinfo_file = open(imageinfo_file_path,'w')
    imageinfo_file.write(json.dumps(img_dic))
    imageinfo_file.close()

    eva_trans_ja = japanese_dic[str(eva_image_wnid)]
    eva_trans_ch = chinese_dic[str(eva_image_wnid)]
    com_trans_ja = japanese_dic[str(com_image_wnid)]
    com_trans_ch = chinese_dic[str(com_image_wnid)]
    
    eva_img = cv2.imread(eva_image_file)
    cv2.imwrite(eva_image_path,eva_img)
    com_img = cv2.imread(com_image_file)
    cv2.imwrite(com_image_path,com_img)
    with open(eva_image_path,'r') as eva_image_f:
        eva_image_stream = eva_image_f.read()
        eva_image_stream = base64.b64encode(eva_image_stream)
    with open(com_image_path,'r') as com_image_f:
        com_image_stream = com_image_f.read()
        com_image_stream = base64.b64encode(com_image_stream)
    return eva_image_id,com_image_id,eva_image_stream,com_image_stream,eva_image_name,com_image_name,eva_image_wnid,com_image_wnid,eva_trans_ja,eva_trans_ch,com_trans_ja,com_trans_ch
    
    



app = flask.Flask(api_name)

@app.route('/home', methods = ['GET','POST'])
def home():
    return render_template('imagenet_home.html')


@app.route('/username', methods = ['POST','GET'])
def login():
    username = request.form.get("username")
    
    print(username)
    if username==None:
        return render_template('imagenet_home.html')

    username = str(username).lower()
    current_user_path = user_path + str(username) + "/"
    userinfo_file_path = current_user_path + "info.txt"
    userlog_file_path = current_user_path + "log.txt"

    
    if username in user_id_list.keys():
        userid = user_id_list[username]
    else:
        userid = len(user_id_list.keys())
        user_id_list[username] = int(userid)
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

    eva_image_id,com_image_id,eva_image_stream,com_image_stream,eva_image_name,com_image_name,eva_image_wnid,com_image_wnid,eva_trans_ja,eva_trans_ch,com_trans_ja,com_trans_ch = update_image(username)
    return render_template("imagenet_eva_touch.html",UserName = username,UserID = userid,
                           EvaluationID = eva_image_id,CompareID = com_image_id,
                           EvaImageStream = eva_image_stream, ComImageStream = com_image_stream,
                           EvaluationName = eva_image_name,CompareName = com_image_name,
                           EvaluationWNID = eva_image_wnid,CompareWNID = com_image_wnid,
                           EvaluationTranslateJa = eva_trans_ja, EvaluationTranslateCh = eva_trans_ch,
                           CompareTranslateJa = com_trans_ja, CompareTranslateCh = com_trans_ch)


@app.route('/log', methods=['POST'])
def log():
    log_dic = {}
    username = request.form["UserName"]
    userid = request.form["UserID"]
    current_user_path = user_path + str(username) + "/"
    userinfo_file_path = current_user_path + "info.txt"
    userlog_file_path = current_user_path + "log.txt"
    eva_imageid = request.form["EvaluationID"]
    com_imageid = request.form["CompareImageID"]
    eva_imagewnid = request.form["EvaluationWNID"]
    com_imagewnid = request.form["CompareWNID"]
    describe = request.form["Description"]
    preference_eva = request.form["Preference_Image_eva"]
    preference_com = request.form["Preference_Image_com"]
    known = "yes"
    if (username == "test"):
        status = "test"
    else:
        status = "log"
    
    relativity = request.form["Relativity"]
    
    log_dic = {}
    log_dic["UserName"] = str(username)
    log_dic["UserID"] = str(userid)
    log_dic["ImageID"] = str(eva_imageid)
    log_dic["ImageClassWNID"] = str(eva_imagewnid)
    log_dic["Status"] = str(status)
    log_dic["Preference"] = str(preference_eva)
    db.insert(preference_table,log_dic)

    log_dic = {}
    log_dic["UserName"] = str(username)
    log_dic["UserID"] = str(userid)
    log_dic["ImageID"] = str(com_imageid)
    log_dic["ImageClassWNID"] = str(com_imagewnid)
    log_dic["Status"] = str(status)
    log_dic["Preference"] = str(preference_com)
    db.insert(preference_table,log_dic)

    log_dic = {}
    log_dic["UserName"] = str(username)
    log_dic["UserID"] = str(userid)
    log_dic["ImageID_1"] = str(eva_imageid)
    log_dic["ImageID_2"] = str(com_imageid)
    log_dic["ImageClassWNID_1"] = str(eva_imagewnid)
    log_dic["ImageClassWNID_2"] = str(com_imagewnid)
    log_dic["Status"] = str(status)
    log_dic["Relativity"] = str(relativity)
    db.insert(relativity_table,log_dic)

    if describe != "NULL":
        log_dic = {}
        log_dic["UserName"] = str(username)
        log_dic["UserID"] = str(userid)
        log_dic["ImageID"] = str(com_imageid)
        log_dic["ImageClassWNID"] = str(com_imagewnid)
        log_dic["Status"] = str(status)
        log_dic["Description"] = str(describe.encode("utf-8"))
        db.insert(description_table,log_dic)
        
    
    if os.path.exists(userlog_file_path):
        with open(userlog_file_path,'a') as userlog_f:
            userlog_f.write(json.dumps(log_dic) + "\n")
    else:
        with open(userlog_file_path,'w') as userlog_f:
            userlog_f.write(json.dumps(log_dic) + "\n")
        
    
    
    eva_image_id,com_image_id,eva_image_stream,com_image_stream,eva_image_name,com_image_name,eva_image_wnid,com_image_wnid,eva_trans_ja,eva_trans_ch,com_trans_ja,com_trans_ch = update_image(username)
    return render_template("imagenet_eva_touch.html",UserName = username,UserID = userid,
                           EvaluationID = eva_image_id,CompareID = com_image_id,
                           EvaImageStream = eva_image_stream, ComImageStream = com_image_stream,
                           EvaluationName = eva_image_name,CompareName = com_image_name,
                           EvaluationWNID = eva_image_wnid,CompareWNID = com_image_wnid,
                           EvaluationTranslateJa = eva_trans_ja, EvaluationTranslateCh = eva_trans_ch,
                           CompareTranslateJa = com_trans_ja, CompareTranslateCh = com_trans_ch)


@app.route('/next', methods=['POST'])
def next_image():
    username = request.form["UserName"]
    userid = request.form["UserID"]   
    eva_image_id,com_image_id,eva_image_stream,com_image_stream,eva_image_name,com_image_name,eva_image_wnid,com_image_wnid,eva_trans_ja,eva_trans_ch,com_trans_ja,com_trans_ch = update_image(username)
    return render_template("imagenet_eva_touch.html",UserName = username,UserID = userid,
                           EvaluationID = eva_image_id,CompareID = com_image_id,
                           EvaImageStream = eva_image_stream, ComImageStream = com_image_stream,
                           EvaluationName = eva_image_name,CompareName = com_image_name,
                           EvaluationWNID = eva_image_wnid,CompareWNID = com_image_wnid,
                           EvaluationTranslateJa = eva_trans_ja, EvaluationTranslateCh = eva_trans_ch,
                           CompareTranslateJa = com_trans_ja, CompareTranslateCh = com_trans_ch)


@app.route('/broken', methods=['POST'])
def broken():
    username = request.form["UserName"]
    userid = request.form["UserID"]
    broken_imageid = request.form["BrokenID"]
    with open(broken_image_list_path,'a') as broken_f:
        broken_f.write(str(broken_imageid) + "\n")
        
    eva_image_id,com_image_id,eva_image_stream,com_image_stream,eva_image_name,com_image_name,eva_image_wnid,com_image_wnid,eva_trans_ja,eva_trans_ch,com_trans_ja,com_trans_ch = update_image(username)
    return render_template("imagenet_eva_touch.html",UserName = username,UserID = userid,
                           EvaluationID = eva_image_id,CompareID = com_image_id,
                           EvaImageStream = eva_image_stream, ComImageStream = com_image_stream,
                           EvaluationName = eva_image_name,CompareName = com_image_name,
                           EvaluationWNID = eva_image_wnid,CompareWNID = com_image_wnid,
                           EvaluationTranslateJa = eva_trans_ja, EvaluationTranslateCh = eva_trans_ch,
                           CompareTranslateJa = com_trans_ja, CompareTranslateCh = com_trans_ch)



if __name__ == '__main__':
    try:
        app.run(debug = True,host = ip_addr, port = ip_port)
        
    finally:
        print("server close!")
        db.close()
