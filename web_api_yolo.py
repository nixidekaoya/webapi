#!usr/bin/env python



import flask
import json
import darknet
import time

#web api
api_name = "yolo"
ip_addr = "192.168.0.116"
ip_port = 8001


#yolo
yolov3_config_path = "/home/li/darknet/cfg/yolov3.cfg"
yolov3_weights_path = "/home/li/darknet/yolov3.weights"
yolov3_data_path = "/home/li/darknet/cfg/coco.data"
yolov3_net = darknet.load_net(yolov3_config_path,yolov3_weights_path,0)
yolov3_meta = darknet.load_meta(yolov3_data_path)


app = flask.Flask(api_name)
#app.config["DEBUG"] = True

@app.route('/helloworld/', methods = ['GET'])
def home():
    return "Hello world!\n"

@app.route('/yolov3/detect/', methods = ['POST'])
def yolov3_detect():
    t1 = time.time()
    temp_jpg_file_path = "/home/li/webapi/tmp/"
    image_seq = "default"
    try:
        image_seq = flask.request.form.get('sequence')
    image_file = flask.request.files['image']
    t2 = time.time() - t1
    print(t2)
    #print(image_seq)
    #print(image_content)
    if image_file:
        temp_jpg_file = temp_jpg_file_path + "temp.jpg"
        image_file.save(temp_jpg_file)
        t2 = time.time() - t1
        print(t2)
        result = darknet.detect(yolov3_net,yolov3_meta,temp_jpg_file,thresh=.65)
        return_json = {"sequence":image_seq,"result":result}
        #print(return_json)
        t2 = time.time() - t1
        print(t2)
        return flask.jsonify(return_json)
    else:
        error_json = {}
        error_json["Error"] = "Image Error"
        return flask.jsonify(error_json)
        
        


if __name__ == '__main__':
    app.run(debug = False, host = ip_addr, port = ip_port)
