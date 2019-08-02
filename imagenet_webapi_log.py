#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import flask
import databasehandler
import json
import time
import os
import cv2
import random
import base64
from flask import request,Response,render_template


#web api
api_name = "Imagenet Evaluation"
ip_addr = "192.168.0.116"
ip_port = 8004


#Database

database_ip = "localhost"
username = "li"
passwd = "issysesosakau"
database_name = "ImagenetDBT"
image_table = "ImageInfo"
preference_table = "UserPreference"
db = databasehandler.DatabaseMySQL(database_ip,username,passwd,database_name)
user_info_columns = ["UserName","UserID"]
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

#Functions
def get_random_image():
    columns = ["ImageName","IndexID","Path","Source","Class0Name"]
    re = db.selectrandom(image_table,columns)
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
    com_image_name = com_image_dic["Class0Name"]
    img_dic = {}
    img_dic["Evaluation ID"] = eva_image_id
    img_dic["Compare ID"] = com_image_id
    img_dic["Evaluation Name"] = eva_image_name
    img_dic["Compare Name"] = com_image_name
    imageinfo_file = open(imageinfo_file_path,'w')
    imageinfo_file.write(json.dumps(img_dic))
    imageinfo_file.close()
    
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
    return eva_image_id,com_image_id,eva_image_stream,com_image_stream,eva_image_name,com_image_name
    
    






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
    current_user_path = user_path + str(username) + "/"
    userinfo_file_path = current_user_path + "info.txt"
    userlog_file_path = current_user_path + "log.txt"
    if username in user_id_list.keys():
        userid = user_id_list[username]
    else:
        userid = len(user_id_list.keys())
        user_id_list[username] = int(userid)
    
    if os.path.exists(current_user_path):
        print()
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


    eva_image_id,com_image_id,eva_image_stream,com_image_stream,eva_image_name,com_image_name = update_image(username)
    return render_template("imagenet_eva.html",UserName = username,UserID = userid,
                           EvaluationID = eva_image_id,CompareID = com_image_id,
                           EvaImageStream = eva_image_stream, ComImageStream = com_image_stream,
                           EvaluationName = eva_image_name,CompareName = com_image_name)



@app.route('/log', methods=['POST'])
def log():
    log_dic = {}
    username = request.form.get("username")
    userid = request.form.get("userid")
    current_user_path = user_path + str(username) + "/"
    userinfo_file_path = current_user_path + "info.txt"
    userlog_file_path = current_user_path + "log.txt"
    eva_imageid = request.form.get("evaimageid")
    com_imageid = request.form.get("comimageid")
    describe = request.form.get("describe")
    preference = request.form.get("preference")
    known = request.form.get("known")
    relativity = request.form.get("relativity")
    log_dic["UserName"] = str(username)
    log_dic["UserID"] = str(userid)
    log_dic["ImageID"] = str(eva_imageid)
    log_dic["Status"] = str(status)
    log_dic["Preference"] = str(preference)
    log_dic["Known"] = str(known)
    log_dic["Attribute"] = describe
    log_dic["Relativity"] = str(relativity)
    log_dic["CompareImageID"] = str(com_imageid)
    
    
    
    if os.path.exists(userlog_file_path):
        with open(userlog_file_path,'a') as userlog_f:
            userlog_f.write(json.dumps(log_dic) + "\n")
    else:
        with open(userlog_file_path,'w') as userlog_f:
            userlog_f.write(json.dumps(log_dic) + "\n")
        
    log_dic["Attribute"] = str(describe.encode("utf-8"))
    db.insert(preference_table,log_dic)
    
    eva_image_id,com_image_id,eva_image_stream,com_image_stream,eva_image_name,com_image_name = update_image(username)
    return render_template("imagenet_eva.html",UserName = username,UserID = userid,
                           EvaluationID = eva_image_id,CompareID = com_image_id,
                           EvaImageStream = eva_image_stream, ComImageStream = com_image_stream,
                           EvaluationName = eva_image_name,CompareName = com_image_name)


@app.route('/broken', methods=['POST'])
def broken():
    username = request.form.get("username")
    userid = request.form.get("userid")
    imageid = request.form.get("evaimageid")
    with open(broken_image_list_path,'a') as broken_f:
        broken_f.write(str(imageid) + "\n")
        
    eva_image_id,com_image_id,eva_image_stream,com_image_stream,eva_image_name,com_image_name = update_image(username)
    return render_template("imagenet_eva.html",UserName = username,UserID = userid,
                           EvaluationID = eva_image_id,CompareID = com_image_id,
                           EvaImageStream = eva_image_stream, ComImageStream = com_image_stream,
                           EvaluationName = eva_image_name,CompareName = com_image_name)

if __name__ == '__main__':
    try:
        app.run(debug = True,host = ip_addr, port = ip_port)
        
    finally:
        print("server close!")
        db.close()
