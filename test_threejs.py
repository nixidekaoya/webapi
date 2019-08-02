#!/usr/bin/env python2
# -*- coding: UTF-8 -*-

import flask
import time
import databasehandler
import json
import os
import io
import random
import base64
from flask import request,Response,render_template,jsonify



#web api
api_name = "Test threejs"
ip_addr = "192.168.0.116"
ip_port = 8008


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




#Paths
base_path = "/home/li/webapi/"
user_path = base_path + "user/"
broken_image_list_path = "/home/li/datasets/broken_list_id.txt"
translate_file_path = "/home/li/datasets/imageinfo_wnid_translate.txt"
chinese_translate_file_path  ="/home/li/datasets/imageinfo_wnid_chinese.txt"
japanese_translate_file_path = "/home/li/datasets/imageinfo_wnid_japanese.txt"
valid_wnid_list_path = "/home/li/datasets/valid_wnid_list.txt"

japanese_fonts_path = "/usr/share/fonts/truetype/fonts-japanese-mincho.ttf"
chinese_fonts_path = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"

################## Translate
english_dic = {}
chinese_dic = {}
japanese_dic = {}
wnid_list = []

################## 

with open(valid_wnid_list_path,'r') as wnid_f:
    for line in wnid_f.readlines():
        wnid_list.append(str(line[:9]))



with io.open(japanese_translate_file_path,'r',encoding='utf-8') as translate_f:
    for line in translate_f.readlines():
        line = line.strip('\n')
        l_list = line.split('\t')
        wnid = str(l_list[0])
        english = l_list[1]
        japanese = l_list[2]
        english_dic[wnid] = english
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
    current_image_list = []
    item1_id,item1_stream,item1_name,item1_wnid,item1_trans_ja,item1_trans_ch = get_image("test")
    item2_id,item2_stream,item2_name,item2_wnid,item2_trans_ja,item2_trans_ch = get_image("test")
    return render_template('test_threejs.html',Item1Name = item1_trans_ja, Item2Name = item2_trans_ja,
                           Item1Stream = item1_stream,
                           Item2Stream = item2_stream)



if __name__ == '__main__':
    try:
        app.run(debug = True, host = ip_addr , port = ip_port)

    finally:
        db.close()
        print("server close!")
