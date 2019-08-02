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
import Image, ImageFont, ImageDraw


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
raw_data_table = "ItemDataRaw"
userinfo_table = "UserInfo"
synset_table = "SynsetMap"
level_table = "LevelTable"
db = databasehandler.DatabaseMySQL(database_ip,username,passwd,database_name)
user_info_columns = ["UserName","UserID"]
columns_imagetable = ["Class0WNID"]
level_column = ["PreferenceNum"]
preference_columns = ["Preference","ImageClassWNID"]

############################# Number and Level


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
    column = ["PreferenceNumber"]
    where_dic = {}
    where_dic["UserName"] = user_name
    result = db.select(userinfo_table,column,where_dic)
    user_number_list[user_name] = int(result[0][0])
    column = ["PreferenceLevel"]
    result = db.select(userinfo_table,column,where_dic)
    user_level_list[user_name] = int(result[0][0])
    
print(user_id_list)
print(user_number_list)
print(user_level_list)




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
font_size = 20


#CONST
ENGLISH = 1
JAPANESE = 2
CHINESE = 3



#Paths
base_path = "/home/li/webapi/"
user_path = base_path + "user/"
static_path = base_path + "static/"
broken_image_list_path = "/home/li/datasets/broken_list_id.txt"
translate_file_path = "/home/li/datasets/imageinfo_wnid_translate.txt"
chinese_translate_file_path  ="/home/li/datasets/imageinfo_wnid_chinese.txt"
japanese_translate_file_path = "/home/li/datasets/imageinfo_wnid_japanese.txt"

english_word_path = "/home/li/datasets/english_word.txt"
japanese_word_path = "/home/li/datasets/japanese_word.txt"
chinese_word_path = "/home/li/datasets/chinese_word.txt"
information_path = "/home/li/datasets/information.txt"
valid_wnid_list_path = "/home/li/datasets/valid_wnid_list.txt"

english_fonts_path = "/home/li/webapi/font/ubuntu-font-family/Ubuntu-B.ttf"
japanese_fonts_path = "/home/li/webapi/font/fonts-japanese-mincho.ttf"
chinese_fonts_path = "/home/li/webapi/font/wqy/wqy-microhei.ttc"

################## Translate
english_dic = {}
chinese_dic = {}
japanese_dic = {}
information_dic = {}
wnid_list = []

with open(valid_wnid_list_path,'r') as wnid_f:
    for line in wnid_f.readlines():
        wnid_list.append(str(line[:9]))



with io.open(english_word_path,'r',encoding='utf-8') as translate_f:
    for line in translate_f.readlines():
        line = line.strip('\n')
        l_list = line.split('\t')
        wnid = str(l_list[0])
        english = l_list[1]
        english_dic[wnid] = english


with io.open(japanese_word_path,'r',encoding='utf-8') as translate_f:
    for line in translate_f.readlines():
        line = line.strip('\n')
        l_list = line.split('\t')
        wnid = str(l_list[0])
        japanese = l_list[1]
        japanese_dic[wnid] = japanese


with io.open(chinese_word_path,'r',encoding='utf-8') as translate_f:
    for line in translate_f.readlines():
        line = line.strip('\n')
        l_list = line.split('\t')
        wnid = str(l_list[0])
        chinese = l_list[1]
        chinese_dic[wnid] = chinese


with io.open(information_path,'r',encoding='utf-8') as translate_f:
    for line in translate_f.readlines():
        line = line.strip('\n')
        l_list = line.split(':')
        wnid = str(l_list[0])
        information = l_list[1]
        #information = information.replace("\t"," ")
        information_dic[wnid] = information




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


def get_item():
    image_dic = get_random_image()
    image_file = image_dic["Path"] + image_dic["ImageName"] + ".jpg"
    image_id = int(image_dic["IndexID"])
    image_wnid = image_dic["Class0WNID"]
    trans_ja = japanese_dic[str(image_wnid)]
    trans_ch = chinese_dic[str(image_wnid)]
    trans_en = english_dic[str(image_wnid)]
    information = information_dic[str(image_wnid)]
    
    
    with open(image_file,'r') as image_f:
        image_stream = image_f.read()
        image_stream = base64.b64encode(image_stream)
    

    return image_id,image_wnid,trans_en,trans_ja,trans_ch,information,image_stream
    
    

def create_image(username,item_count,font_path,text):
    image_file_path = static_path + str(username) + "_preference_" + str(item_count) + ".png"
    im = Image.new("RGB",(128,32),(255,128,0))
    dr = ImageDraw.Draw(im)
    font = ImageFont.truetype(font_path,font_size)
    dr.text((20,6), text, font = font, fill = "#000000")
    im.save(image_file_path)
    
    



app = flask.Flask(api_name)
@app.route('/home', methods = ['GET','POST'])
def home():
    return render_template('interface_v3_home_preference.html')



@app.route('/login', methods = ['POST','GET'])
def login():
    username = request.form.get("username")
    
    print(username)
    if username==None:
        return render_template('interface_v3_home_preference.html')

    username = str(username).lower()
    current_user_path = user_path + str(username) + "/"
    userinfo_file_path = current_user_path + "info.txt"
    userlog_file_path = current_user_path + "preference_log.txt"
    language = int(request.form.get("language"))

    
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


    item_name_list = []
    item_wnid_list = []
    item_imageid_list = []
    item_info_list = []
    item_stream_list = []
    for i in range(item_number):
        image_id,image_wnid,trans_en,trans_ja,trans_ch,information,image_stream = get_item()
        while image_wnid in item_wnid_list:
            image_id,image_wnid,trans_en,trans_ja,trans_ch,information,image_stream = get_item()
        item_wnid_list.append(image_wnid)
        item_imageid_list.append(image_id)
        item_info_list.append(information)
        item_stream_list.append(image_stream)
        if language == ENGLISH:
            item_name_list.append(trans_en)
            display_language = "english"
            create_image(username, i, english_fonts_path, trans_en)
        elif language == JAPANESE:
            item_name_list.append(trans_ja)
            display_language = "japanese"
            create_image(username, i, japanese_fonts_path, trans_ja)
        elif language == CHINESE:
            item_name_list.append(trans_ch)
            display_language = "chinese"
            create_image(username, i, japanese_fonts_path, trans_ch)
            

        
    user_number = user_number_list[str(username)]
    user_level = user_level_list[str(username)]
    current_level_num = level_list[user_level]
    next_level_num = level_list[user_level + 1]
    complete_ratio = int((100 * (user_number - current_level_num))/(next_level_num - current_level_num))

    return render_template("interface_v3_preference.html",UserName = username,UserID = userid,
                           ItemWNID_0 = item_wnid_list[0], ItemID_0 = item_imageid_list[0], ItemName_0 = item_name_list[0], ItemInfo_0 = item_info_list[0], ItemStream_0 = item_stream_list[0],
                           ItemWNID_1 = item_wnid_list[1], ItemID_1 = item_imageid_list[1], ItemName_1 = item_name_list[1], ItemInfo_1 = item_info_list[1], ItemStream_1 = item_stream_list[1],
                           ItemWNID_2 = item_wnid_list[2], ItemID_2 = item_imageid_list[2], ItemName_2 = item_name_list[2], ItemInfo_2 = item_info_list[2], ItemStream_2 = item_stream_list[2],
                           ItemWNID_3 = item_wnid_list[3], ItemID_3 = item_imageid_list[3], ItemName_3 = item_name_list[3], ItemInfo_3 = item_info_list[3], ItemStream_3 = item_stream_list[3],
                           ItemWNID_4 = item_wnid_list[4], ItemID_4 = item_imageid_list[4], ItemName_4 = item_name_list[4], ItemInfo_4 = item_info_list[4], ItemStream_4 = item_stream_list[4],
                           ItemWNID_5 = item_wnid_list[5], ItemID_5 = item_imageid_list[5], ItemName_5 = item_name_list[5], ItemInfo_5 = item_info_list[5], ItemStream_5 = item_stream_list[5],
                           ItemWNID_6 = item_wnid_list[6], ItemID_6 = item_imageid_list[6], ItemName_6 = item_name_list[6], ItemInfo_6 = item_info_list[6], ItemStream_6 = item_stream_list[6],
                           ItemWNID_7 = item_wnid_list[7], ItemID_7 = item_imageid_list[7], ItemName_7 = item_name_list[7], ItemInfo_7 = item_info_list[7], ItemStream_7 = item_stream_list[7],
                           ItemWNID_8 = item_wnid_list[8], ItemID_8 = item_imageid_list[8], ItemName_8 = item_name_list[8], ItemInfo_8 = item_info_list[8], ItemStream_8 = item_stream_list[8],
                           ItemWNID_9 = item_wnid_list[9], ItemID_9 = item_imageid_list[9], ItemName_9 = item_name_list[9], ItemInfo_9 = item_info_list[9], ItemStream_9 = item_stream_list[9],
                           UserNumber = user_number,UserLevel = user_level, CompleteRatio = complete_ratio,
                           Language = display_language)
       


@app.route('/log', methods=['POST'])
def log():

    print(request.form)
    
    log_dic = {}
    username = request.form["UserName"]
    userid = request.form["UserID"]
    log_dic["UserName"] = str(username)
    log_dic["UserID"] = str(userid)
    log_dic["Attribute"] = "Preference"
    current_user_path = user_path + str(username) + "/"
    userinfo_file_path = current_user_path + "info.txt"
    userlog_file_path = current_user_path + "preference_log.txt"

                

    if (username == "test"):
        status = "test"
    else:
        status = "log"

    log_dic["Status"] = status
    for i in range(item_number):
        wnid_text = "ItemWNID_" + str(i+1)
        imageid_text = "ImageID_" + str(i+1)
        x_coordinate_text = "X_Coordinate_" + str(i+1)
        y_coordinate_text = "Y_Coordinate_" + str(i+1)
        log_dic["ItemWNID"] = str(request.form[wnid_text])
        log_dic["ImageID"] = str(request.form[imageid_text])
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
