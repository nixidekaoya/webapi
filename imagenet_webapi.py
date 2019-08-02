#!/usr/bin/env python

import flask
import databasehandler
import json
import time
import os
import random
from flask import request,Response


#web api
api_name = "Imagenet Evaluation"
ip_addr = "192.168.0.116"
ip_port = 8003


#Database
'''
database_ip = "localhost"
username = "li"
passwd = "issysesosakau"
database_name = "ImagenetDBT"
image_table = "ImageInfo"
preference_table = "UserPreference"
db = databasehandler.DatabaseMySQL(database_ip,username,passwd,database_name)
'''
#Functions




#Variables


app = flask.Flask(api_name)

@app.route('/home', methods = ['GET','POST'])
def home():
    return flask.render_template('image_display.html')


@app.route('/getfile', methods = ['GET'])
def getfile():
    file_path = "/home/li/webapi/static/imageinfo.txt"
    
    print(file_path)
    #print(os.path.join(base_dir,file_path))
    resp = flask.make_response(open(file_path).read())
    resp.mimetype = "text/plain"
    print(resp.data)
    #resp.headers["Content-type"]="text/plan;charset=UTF-8"
    return resp
    

@app.route('/getimage',methods = ['GET'])
def getimage():
    image = file("/home/li/webapi/static/temp.jpg")
    resp = Response(image,mimetype="image/jpg")
    return resp


if __name__ == '__main__':
    try:
        app.run(debug = False,host = ip_addr, port = ip_port)
        
    finally:
        print("server close!")
        #db.close()
