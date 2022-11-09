# 导入Flask类
from fastapi import FastAPI,Form
import json
import base64
# from paddleocr import PaddleOCR
import os
# os.environ["CUDA_VISIBLE_DEVICES"] = '0'
import image
import cv2
import threading
import socket
import traceback
import time
import random
import re
import os
import numpy as np
import requests
import json
import difflib
import html
import httpx
import asyncio
import aiohttp
import uvicorn
import shutil
import text
from PIL import Image, ImageDraw, ImageFont
from paddleocr import PaddleOCR
from distutils.util import strtobool

path = os.getcwd()
config = json.load(open('./config.json', 'r', encoding='utf8'))
# 使用当前模块的名称构建Flask app
app = FastAPI()


@app.post('/OCR/')
def get_item_list(url:str = Form()):
    start = time.time()#请求开始
    file_name = path+'/image'+str(random.randint(0, 1000)) + '.jpg'
    try:
        dowtime = time.time()
        imgdow = image.img_dow(url,file_name)
        dowtimend = time.time()
        if imgdow != '图片类型为GIF跳过':
            ocr_guolv = time.time()
            result = ocr2.ocr(file_name, rec=False,cls=False)
            ocr_guolv_end = time.time()
            if len(result) < 12 and len(result) > 0:
                result = ocr.ocr(file_name, cls=True)
                string = text.Text_Chuli(result)
            else:
                string = '未匹配'
            if 'wws ' in string and strtobool(config['save_image']):
                shutil.move(file_name,'./save/image'+str(len(os.listdir('./save/'))+1)+'.jpg')
            else:
                os.remove(file_name)
        else:
            string = '未匹配'
        if strtobool(config['time_log']):
            print('获取图片耗时:',dowtimend-dowtime,imgdow)
            if imgdow != '图片类型为GIF跳过':
                print('图片过滤耗时：',ocr_guolv_end-ocr_guolv)
            print("总耗时：", time.time() - start,time.strftime('%Y-%m-%d-%Hh-%Mm-%Ss',time.localtime(time.time())))
        
        print(string)
        return string
    except Exception as e:
        traceback.print_exc()
        try:
            os.remove(file_name)
            return "未匹配"
        except:
            return "未匹配"
            pass

# 运行程序
start = time.time()
ocr2 = PaddleOCR(use_gpu=True,
                det_model_dir='./inference/db_mv3_infer',
                use_mp=True, total_process_num=6,show_log=False)
ocr = PaddleOCR(use_angle_cls=True, lang="ch", use_gpu=strtobool(config['gpu']),
                rec_model_dir='./inference/ch_PP-OCRv3_rec_infer/',
                cls_model_dir='./inference/ch_ppocr_mobile_v2.0_cls_infer/',
                det_model_dir='./inference/ch_PP-OCRv3_det_infer/',
                use_mp=True, total_process_num=6,show_log=strtobool(config['ocr_log']),
                drop_score=0.4,precision='int8')
img = './a.jpg'
result = ocr.ocr(img, cls=True)
result = ocr2.ocr(img, cls=True)
print("OCR初始化耗时：", time.time() - start)
if __name__ == '__main__':
    uvicorn.run(app, host="192.168.1.110", port=int(config['port']),access_log=strtobool(config['api_log']))

