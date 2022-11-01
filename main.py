# 导入Flask类
from gevent import monkey
monkey.patch_all()
from flask import Flask, request
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
import json
import base64
# from paddleocr import PaddleOCR
import os
# os.environ["CUDA_VISIBLE_DEVICES"] = '0'
import sys
sys.path.append('/home/youth/Desktop/PaddleOCR/')
import cv2
import threading
import socket
import traceback
import time
import random
import re
import numpy as np
import requests
import json
import difflib
import html
import httpx
import asyncio
import aiohttp
from PIL import Image, ImageDraw, ImageFont
from interval import Interval
from paddleocr import PaddleOCR, draw_ocr,logging

# 使用当前模块的名称构建Flask app
app = Flask(__name__)


kongge = ['wws', 'me', 'ship', 'recent', '绑定', '国服', '亚服', '俄服', '美服','cn','asia','na','eu']
server = '国服,亚服,俄服,美服,cn,asia,na,eu'


api_url = r'https://api.wows.shinoaki.com/public/wows/encyclopedia/ship/search'
res = requests.get(api_url)
res_data = json.loads(res.text).get('data')
name_list = []
for i in range(4, len(res_data)):
    name_list.append(res_data[i].get('shipNameNumbers'))
    name_list.append(res_data[i].get('shipNameCn'))
def fuzzy_matching(list,value):
    texts_score = {}
    for i in list:
        score = difflib.SequenceMatcher(None, i, value).quick_ratio()
        texts_score[i] = score
    texts_score = sorted(texts_score.items(), key=lambda x: x[1], reverse=False)
    # print(texts_score)
    match_value = texts_score[-1][0]
    return match_value
def Text_Chuli(string):
    for i in range(0, len(kongge)):
        dst_path = string.lower().find(kongge[i])
        if dst_path != -1 and dst_path + len(kongge[i]) < len(string) and string[dst_path + len(kongge[i])] != ' ':
            string = string[0:dst_path]+' '+string[dst_path:dst_path + len(kongge[i])] + ' ' + string[dst_path + len(kongge[i]):len(string)]
    #关键词后添加空格
    list = string.split(' ')
    while "" in list:  # 判断是否有空值在列表中
        list.remove("")  # 如果有就直接通过remove删除
    if_ch_text = False
    for i in range(0, len(list)):
        if if_ch_text == True and list[i].lower() != 'wws':
            pass
        else:
            list[i] = list[i].lower()
        if list[i] != '' and (list[i][-1] < u'\u4e00' or list[i][-1] > u'\u9fff'):
            if_ch_text = False
            list[i] = list[i].replace('--', '_')
        else:
            if_ch_text = True
            
    string = ' '.join(list)
    print(string)
    match = re.search(r"^(.*?)wws(.*?)$",string)
    if match:
        string = re.sub(r"^(.*?)(?=wws)","",string)
    else:
        string = '未匹配'
        return string
    list = string.split(' ')
    if len(list) < 3:
        return string
    #正则匹配
    for i in range(0, len(list)):
        for i in range(0, len(list)):
            if 'wws' in list[i]:
                a = list[i]
                list[i] = list[0]
                list[0] = a
            elif list[i] == 'me' or list[i] == '绑定':
                a = list[i]
                list[i] = list[1]
                list[1] = a
            elif list[i] == 'ship' or list[i] == 'recent':
                if list[1] in server:
                    a = list[i]
                    list[i] = list[3]
                    list[3] = a
                else:
                    a = list[i]
                    list[i] = list[2]
                    list[2] = a

    print(list)
    #排序
    intjishu = 0
    shanchu =0
    for i in range(0, len(list)):
        if i + 1 < len(list):
            if list[i] == 'wws' and ('e' in list[i + 1] or 'm' in list[i + 1]) and len(list[i + 1]) <= 2:
                list[i + 1] = 'me'
        if len(re.findall(r"\d+", list[i])) > 0:
            list[i] = re.findall(r"\d+", list[i])[0]
            
    for i in range(0, len(list)):
        if list[i-shanchu].isdigit():
            intjishu = intjishu+1
        if intjishu > 1:
            list.remove(list[i-shanchu])
            shanchu = shanchu+1
            
    #修复 me不完整
    
    if list[2] == 'ship' and len(list) >= 3:
        list[3] = fuzzy_matching(name_list,list[3])
        for i in range(len(list)-1,3,-1):
            list.pop(i)
    #修复 ship参数
    string = ' '.join(list)
    return string
# 获取分类列表
async def get_image_bytes(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.content
@app.route('/OCR/', methods=["GET","POST"])
def get_item_list():
    start = time.time()
    file_name = '/home/youth/Desktop/OCRServer/image' + str(random.randint(0, 1000)) + '.jpg'
    try:
        image_url = request.form['url']  # 获取图像数据,对应客户端的img_str
        #print(image_url)
        data = httpx.get(image_url).content
        # data = asyncio.run(get_image_bytes(image_url))
        datalong = len(data)/1024/1024
        if datalong > 1:
            datalongstr = str(round(datalong,4))+'MB'
        else:
            datalongstr = str(round(datalong*1024,4))+'KB'
        print('下载图片耗时:',time.time()-start,datalongstr)
        if tuple(data[0:4]) == (0x47,0x49,0x46,0x38):
            string = '未匹配'
            print("OCR耗时：", time.time() - start,string)
            return string
        img_np_arr = np.frombuffer(data, np.uint8)
        img = cv2.imdecode(img_np_arr, cv2.IMREAD_COLOR)
        try:
            shape = img.shape
        except:
            with open(file_name_debug,'wb') as f:
                f.write(data)
                # TODO: write code...
            string = '未匹配'
        suofangtime = time.time()
        if shape[0] > 1000 or shape[1] > 1000:
            if shape[0] > shape[1]:
                beishu =  round(800/shape[0],2)
            else:
                beishu =  round(800/shape[1],2)
            dst = cv2.resize(img,None, fy = beishu,fx=beishu, interpolation=cv2.INTER_AREA)  # 缩小
            dst = cv2.normalize(dst, dst=None, alpha=250, beta=5, norm_type=cv2.NORM_MINMAX)
            # dst = cv2.blur(dst,(3,3))#低值滤波
            dst = cv2.GaussianBlur(dst, (5, 5), 0, 0)  # 高斯滤波
            cv2.imwrite(file_name, dst)
        elif shape[0] < 450 and shape[1] < 450:
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
        # print('缩放耗时:',time.time()-suofangtime)
        result = ocr.ocr(file_name, cls=True)
        os.remove(file_name)
        if len(result) > 0 and len(result) < 12:
            # texttime = time.time()
            string = align_text(result)
            if len(string) > 50 or len(string) < 5:
                string ='未匹配'
            else:
                string = Text_Chuli(string)
            # print('文本处理耗时:',time.time()-texttime)
        else:
            string = '未匹配'
        print("OCR总耗时：", time.time() - start,dst.shape[1], '*', dst.shape[0],string,time.strftime('%Y-%m-%d-%Hh-%Mm-%Ss',time.localtime(time.time())))
        return string
    except Exception as e:
        traceback.print_exc()
        try:
            os.remove(file_name)
            return "未匹配"
        except:
            return "未匹配"
            pass



def align_text(res, threshold=0):
    res.sort(key=lambda i: (i[0][0][0]))  # 按照x排
    already_IN, line_list = [], []
    for i in range(len(res)):  # i当前
        if res[i][0][0] in already_IN:
            continue
        line_txt = res[i][1][0]
        already_IN.append(res[i][0][0])
        y_i_points = [res[i][0][0][1], res[i][0][1][1], res[i][0][3][1], res[i][0][2][1]]
        min_I_y, max_I_y = min(y_i_points), max(y_i_points)
        curr = Interval(min_I_y + (max_I_y - min_I_y) // 3, max_I_y)
        curr_mid = min_I_y + (max_I_y - min_I_y) // 2

        for j in range(i + 1, len(res)):  # j下一个
            if res[j][0][0] in already_IN:
                continue
            y_j_points = [res[j][0][0][1], res[j][0][1][1], res[j][0][3][1], res[j][0][2][1]]
            min_J_y, max_J_y = min(y_j_points), max(y_j_points)
            next_j = Interval(min_J_y, max_J_y - (max_J_y - min_J_y) // 3)

            if next_j.overlaps(curr) and curr_mid in Interval(min_J_y, max_J_y):
                line_txt += (res[j][1][0] + "  ")
                already_IN.append(res[j][0][0])
                curr = Interval(min_J_y + (max_J_y - min_J_y) // 3, max_J_y)
                curr_mid = min_J_y + (max_J_y - min_J_y) // 2
        line_list.append((res[i][0][0][1], line_txt))
    line_list.sort(key=lambda x: x[0])
    txt = ' '.join([i[1] for i in line_list])
    return txt
# 运行程序

if __name__ == '__main__':
    start = time.time()
    ocr = PaddleOCR(use_angle_cls=True, lang="ch", use_gpu=True,
                    rec_model_dir='./inference/ch_PP-OCRv3_rec_infer/',
                    cls_model_dir='./inference/ch_ppocr_mobile_v2.0_cls_infer/',
                    det_model_dir='./inference/ch_PP-OCRv3_det_infer/',
                    use_mp=True, total_process_num=6,show_log=False,
                    drop_score=0.4,precision='int8',use_tensorrt=False)  # need to run only once to download and load model into memory
    img = './a.jpg'
    result = ocr.ocr(img, cls=True)
    print("OCR初始化耗时：", time.time() - start)
    # app.run(host='192.168.1.110',port=23338,processes=True,use_reloader=False)
    server = pywsgi.WSGIServer(('192.168.1.110', 23338), app,handler_class=WebSocketHandler)
    server.serve_forever()