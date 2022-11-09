import cv2
import numpy as np
import requests
import threading
import json
import time
import random
from multiprocessing.dummy import Pool as ThreadPool

config = json.load(open('./config.json', 'r', encoding='utf8'))
img_size_max = config['img_size_max'].split(',')
img_size_min = config['img_size_min'].split(',')
img_aim_long = int(config['img_aim_long'])

path = []
imgdata = []
state = True
cancel_tmr = False

for i in range(2):
    img_size_max[i] = int(img_size_max[i])
    img_size_min[i] = int(img_size_min[i])

def dowm(string):
    data = requests.get(string)
    return data.content

def timer():
    global path
    global imgdata
    global state
    paths = path
    path = []
	# 打印当前时间
    if not cancel_tmr:
        if len(paths)!=0:
            state = False
            start = time.time()
            imgdata = pool.map(dowm, paths)
            # for i in imgdata:
            #     print(len(i))
            # print(time.time()-start,len(imgdata))
            state = True
        threading.Timer(0.1, timer).start()
    
def img_dow(image_url,file_name):
    global path
    global imgdata
    global state
    while not state:
        time.sleep(0.01)
    path.append(image_url)
    datatag = len(path)-1
    print(datatag)
    time.sleep(0.1)
    while True:
        time.sleep(0.01)
        # print('sleep')
        if state:
            data = imgdata[datatag]
            break
    # data = requests.get(image_url).content
    datalong = len(data)/1024/1024
    if datalong > 1:
        datalongstr = str(round(datalong,4))+'MB'
    else:
        datalongstr = str(round(datalong*1024,4))+'KB'
    if tuple(data[0:4]) == (0x47,0x49,0x46,0x38):
        # print("图片类型为GIF跳过")
        return "图片类型为GIF跳过"
    else:
        img_np_arr = np.frombuffer(data, np.uint8)
        img = cv2.imdecode(img_np_arr, cv2.IMREAD_COLOR)
        shape = img.shape
        if shape[0] > img_aim_long+200 or shape[1] > img_aim_long+200:
            if shape[0] > shape[1]:
                beishu =  round(img_aim_long/shape[0],2)
            else:
                beishu =  round(img_aim_long/shape[1],2)
            dst = cv2.resize(img,None, fy = beishu,fx=beishu, interpolation=cv2.INTER_AREA)  # 缩小
            dst = cv2.normalize(dst, dst=None, alpha=250, beta=5, norm_type=cv2.NORM_MINMAX)
            # dst = cv2.blur(dst,(3,3))#低值滤波
            dst = cv2.GaussianBlur(dst, (5, 5), 0, 0)  # 高斯滤波
            cv2.imwrite(file_name, dst)
        elif shape[0] < img_aim_long-300 and shape[1] < img_aim_long-300:
            if shape[0] > shape[1]:
                beishu =  round(800/shape[0],2)
            else:
                beishu =  round(800/shape[1],2)
            dst = cv2.resize(img, (int(beishu * shape[1]), int(beishu * shape[0])), interpolation=cv2.INTER_CUBIC)  # 放大2倍
            dst = cv2.normalize(dst, dst=None, alpha=250, beta=5, norm_type=cv2.NORM_MINMAX)
            # dst = cv2.blur(dst,(3,3))#低值滤波
            dst = cv2.GaussianBlur(dst, (5, 5), 0, 0)  # 高斯滤波
            cv2.imwrite(file_name, dst)
        else:
            dst = img
            cv2.imwrite(file_name, dst)
            # print()
        return datalongstr
        
pool = ThreadPool(6)
timer()