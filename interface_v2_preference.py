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
ip_port = 8006


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


def update_image(username):
    current_user_path = user_path + str(username) + "/"
    image_path = current_user_path + "interface_v2_preference_image.jpg"
    image_dic = get_random_image()
    image_file = image_dic["Path"] + image_dic["ImageName"] + ".jpg"
    image_id = int(image_dic["IndexID"])
    image_name = image_dic["Class0Name"]
    image_wnid = image_dic["Class0WNID"]


    trans_ja = japanese_dic[str(image_wnid)]
    trans_ch = chinese_dic[str(image_wnid)]

    
    img = cv2.imread(image_file)
    cv2.imwrite(image_path,img)

    with open(image_path,'r') as image_f:
        image_stream = image_f.read()
        image_stream = base64.b64encode(image_stream)

    return image_id,image_stream,image_name,image_wnid,trans_ja,trans_ch
    
    



app = flask.Flask(api_name)

@app.route('/home', methods = ['GET','POST'])
def home():
    return render_template('interface_v2_home.html',target = "preference")


@app.route('/login', methods = ['POST','GET'])
def login():
    username = request.form.get("username")
    
    print(username)
    if username==None:
        return render_template('interface_v2_home.html',target = "preference")

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

    image_id,image_stream,image_name,image_wnid,trans_ja,trans_ch = update_image(username)
    user_number = user_number_list[str(username)]
    user_level = user_level_list[str(username)]
    current_level_num = level_list[user_level]
    next_level_num = level_list[user_level + 1]
    complete_ratio = int((100 * (user_number - current_level_num))/(next_level_num - current_level_num))

    return render_template("interface_v2_preference.html",UserName = username,UserID = userid,
                           ImageID = image_id,
                           ImageStream = image_stream,
                           ImageName = image_name,
                           ImageWNID = image_wnid,
                           TranslateJa = trans_ja, TranslateCh = trans_ch,
                           UserNumber = user_number,UserLevel = user_level,
                           CompleteRatio = complete_ratio)
       


@app.route('/log', methods=['POST'])
def log():
    log_dic = {}
    username = request.form["UserName"]
    userid = request.form["UserID"]
    current_user_path = user_path + str(username) + "/"
    userinfo_file_path = current_user_path + "info.txt"
    userlog_file_path = current_user_path + "preference_log.txt"
    imageid = request.form["ImageID"]
    imagewnid = request.form["ImageWNID"]
    preference = request.form["Preference"]
    known = "yes"
    if (username == "test"):
        status = "test"
    else:
        status = "log"
    
    
    log_dic = {}
    log_dic["UserName"] = str(username)
    log_dic["UserID"] = str(userid)
    log_dic["ImageID"] = str(imageid)
    log_dic["ImageClassWNID"] = str(imagewnid)
    log_dic["Status"] = str(status)
    log_dic["Preference"] = str(preference)
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
    
        
    
    if os.path.exists(userlog_file_path):
        with open(userlog_file_path,'a') as userlog_f:
            userlog_f.write(json.dumps(log_dic) + "\n")
    else:
        with open(userlog_file_path,'w') as userlog_f:
            userlog_f.write(json.dumps(log_dic) + "\n")
        
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
   

@app.route('/wordcloud', methods=['GET','POST'])
def wordcloud():
    username = request.form.get("username")

    if username==None:
        return render_template('interface_v2_home_wordcloud.html',warning_message = "Please input your user name!")

        
    username = str(username).lower()
    if username not in user_id_list.keys():
        return render_template('interface_v2_home_wordcloud.html',warning_message = "Please input a registered user name! To generate new user name: 192.168.0.116:8006/home")


    wordcloud_language = request.form.get("wordcloudlanguage")
    userid = user_id_list[username]

    current_user_path = user_path + str(username) + "/"
    wordcloud_like_path = current_user_path + "wordcloud_like.jpg"
    wordcloud_dislike_path = current_user_path + "wordcloud_dislike.jpg"
    wordcloud_neutral_path = current_user_path + "wordcloud_neutral.jpg"

    where_dic = {}
    where_dic["UserName"] = str(username)

    result = db.select(preference_table,preference_columns,where_dic)
    record_num = len(result)
    like_list = []
    like_dic = {}
    dislike_list = []
    dislike_dic = {}
    neutral_list = []
    neutral_dic = {}

    for record in result:
        preference = str(record[0])
        wnid = str(record[1])
        if preference == "like":
            if wnid in like_list:
                like_dic[wnid] += 1
            else:
                like_dic[wnid] = 1
            like_list.append(wnid)
        elif preference == "dislike":
            if wnid in dislike_list:
                dislike_dic[wnid] += 1
            else:
                dislike_dic[wnid] = 1
            dislike_list.append(wnid)
        else:
            if wnid in neutral_list:
                neutral_dic[wnid] += 1
            else:
                neutral_dic[wnid] = 1
            neutral_list.append(wnid)

    like_frequencies = {}
    dislike_frequencies = {}
    neutral_frequencies = {}

    if wordcloud_language == "english":
        for wnid in like_list:
            like_frequencies[english_dic[wnid]] = int(like_dic[wnid])
        for wnid in dislike_list:
            dislike_frequencies[english_dic[wnid]] = int(dislike_dic[wnid])
        for wnid in neutral_list:
            neutral_frequencies[english_dic[wnid]] = int(neutral_dic[wnid])
        if len(like_frequencies.keys()) == 0:
            like_frequencies["NULL"] = 1
        if len(dislike_frequencies.keys()) == 0:
            dislike_frequencies["NULL"] = 1
        if len(neutral_frequencies.keys()) == 0:
            neutral_frequencies["NULL"] = 1
        wordcloud_like = WordCloud(width = wordcloud_width, height = wordcloud_height, prefer_horizontal = prefer_horizontal, max_words = max_words, max_font_size = max_font_size, min_font_size = min_font_size, background_color = background_color).fit_words(like_frequencies)
        wordcloud_dislike = WordCloud(width = wordcloud_width, height = wordcloud_height, prefer_horizontal = prefer_horizontal, max_words = max_words, max_font_size = max_font_size, min_font_size = min_font_size, background_color = background_color).fit_words(dislike_frequencies)
        wordcloud_neutral = WordCloud(width = wordcloud_width, height = wordcloud_height, prefer_horizontal = prefer_horizontal, max_words = max_words, max_font_size = max_font_size, min_font_size = min_font_size, background_color = background_color).fit_words(neutral_frequencies)
    elif wordcloud_language == "japanese":
        for wnid in like_list:
            like_frequencies[japanese_dic[wnid]] = int(like_dic[wnid])
        for wnid in dislike_list:
            dislike_frequencies[japanese_dic[wnid]] = int(dislike_dic[wnid])
        for wnid in neutral_list:
            neutral_frequencies[japanese_dic[wnid]] = int(neutral_dic[wnid])
        if len(like_frequencies.keys()) == 0:
            like_frequencies["NULL"] = 1
        if len(dislike_frequencies.keys()) == 0:
            dislike_frequencies["NULL"] = 1
        if len(neutral_frequencies.keys()) == 0:
            neutral_frequencies["NULL"] = 1
        wordcloud_like = WordCloud(font_path = japanese_fonts_path,width = wordcloud_width, height = wordcloud_height, prefer_horizontal = prefer_horizontal, max_words = max_words, max_font_size = max_font_size, min_font_size = min_font_size, background_color = background_color).fit_words(like_frequencies)
        wordcloud_dislike = WordCloud(font_path = japanese_fonts_path,width = wordcloud_width, height = wordcloud_height, prefer_horizontal = prefer_horizontal, max_words = max_words, max_font_size = max_font_size, min_font_size = min_font_size, background_color = background_color).fit_words(dislike_frequencies)
        wordcloud_neutral = WordCloud(font_path = japanese_fonts_path,width = wordcloud_width, height = wordcloud_height, prefer_horizontal = prefer_horizontal, max_words = max_words, max_font_size = max_font_size, min_font_size = min_font_size, background_color = background_color).fit_words(neutral_frequencies)
    elif wordcloud_language == "chinese":
        for wnid in like_list:
            like_frequencies[chinese_dic[wnid]] = int(like_dic[wnid])
        for wnid in dislike_list:
            dislike_frequencies[chinese_dic[wnid]] = int(dislike_dic[wnid])
        for wnid in neutral_list:
            neutral_frequencies[chinese_dic[wnid]] = int(neutral_dic[wnid])
        if len(like_frequencies.keys()) == 0:
            like_frequencies["NULL"] = 1
        if len(dislike_frequencies.keys()) == 0:
            dislike_frequencies["NULL"] = 1
        if len(neutral_frequencies.keys()) == 0:
            neutral_frequencies["NULL"] = 1
        wordcloud_like = WordCloud(font_path = chinese_fonts_path,width = wordcloud_width, height = wordcloud_height, prefer_horizontal = prefer_horizontal, max_words = max_words, max_font_size = max_font_size, min_font_size = min_font_size, background_color = background_color).fit_words(like_frequencies)
        wordcloud_dislike = WordCloud(font_path = chinese_fonts_path,width = wordcloud_width, height = wordcloud_height, prefer_horizontal = prefer_horizontal, max_words = max_words, max_font_size = max_font_size, min_font_size = min_font_size, background_color = background_color).fit_words(dislike_frequencies)
        wordcloud_neutral = WordCloud(font_path = chinese_fonts_path,width = wordcloud_width, height = wordcloud_height, prefer_horizontal = prefer_horizontal, max_words = max_words, max_font_size = max_font_size, min_font_size = min_font_size, background_color = background_color).fit_words(neutral_frequencies)

    wordcloud_like.to_file(wordcloud_like_path)
    wordcloud_dislike.to_file(wordcloud_dislike_path)
    wordcloud_neutral.to_file(wordcloud_neutral_path)


    with open(wordcloud_like_path,'r') as image_f:
        wordcloud_like_stream = image_f.read()
        wordcloud_like_stream = base64.b64encode(wordcloud_like_stream)

    with open(wordcloud_dislike_path,'r') as image_f:
        wordcloud_dislike_stream = image_f.read()
        wordcloud_dislike_stream = base64.b64encode(wordcloud_dislike_stream)

    with open(wordcloud_neutral_path,'r') as image_f:
        wordcloud_neutral_stream = image_f.read()
        wordcloud_neutral_stream = base64.b64encode(wordcloud_neutral_stream)
    
    
    return render_template("wordcloud_display.html",UserName = username,UserID = userid,
                           WordCloudLikeStream = wordcloud_like_stream,
                           WordCloudDislikeStream = wordcloud_dislike_stream,
                           WordCloudNeutralStream = wordcloud_neutral_stream)


if __name__ == '__main__':
    try:
        app.run(debug = True,host = ip_addr, port = ip_port)
        
    finally:
        print("server close!")
        db.close()
