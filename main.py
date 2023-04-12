# 导入Flask类
from fastapi import FastAPI,Form
import image
import traceback
import time
import random
import os
import json
import uvicorn
import shutil
import text
import hashlib
import base64
import cv2
import get_Hash
from paddleocr import PaddleOCR
from distutils.util import strtobool

path = os.getcwd()
config = json.load(open('./config.json', 'r', encoding='utf8'))
# 使用当前模块的名称构建Flask app
app = FastAPI()
if not os.path.exists('./save'):
    os.madir('./save')
if not(os.path.exists('./data.json')):
        with open('./data.json','w') as f:
            f.write('{}')
            f.close()
@app.post('/OCR/') #OCR服务
def get_item_list(url:str = Form()):
    start = time.time()
    file_name = path+'/image'+str(random.randint(0, 1000)) + '.jpg'
    file_name_S = path+'/image'+str(random.randint(0, 1000)) + '_S.jpg'
    try:
        dowtime = time.time()
        imgdow = image.img_dow(url,file_name,file_name_S)
        dowtimend = time.time()
        if imgdow != '图像不符合':
            ocr_guolv = time.time()
            
            with open(path+'/data.json','r') as f:
                jsonData = f.read()
                f.close()
            # print(jsonData)
            Hash_list = json.loads(jsonData)
            Hashmatching = False
            img = cv2.imread(file_name_S,1)
            Hash = get_Hash.pHash(img)
            for key in Hash_list:
                    data = Hash_list[key].replace('[','').replace(']','').replace(' ','').split(',')
                    for i in range(len(data)):
                        data[i] = int(data[i])
                    # print(data)
                    dst = get_Hash.cmpHash(Hash,data)
                    if dst < 10:
                        print(key,file_name_S,dst)
                        Hashmatching = True
                        break
            # print(Hashmatching)
            if not Hashmatching:
                result = ocr2.ocr(file_name, rec=False,cls=False)
            else:
                result = '1'
            ocr_guolv_end = time.time()
            if len(result) < 12 and len(result) > 0:
                result = ocr.ocr(file_name, cls=True)
                string = text.Text_Chuli(result)
            else:
                string = '未匹配'
            if 'wws ' in string and strtobool(config['save_image']):
                with open(file_name_S,'rb') as f:
                    md = hashlib.md5()
                    md.update(f.read())
                    md5 = md.hexdigest()
                shutil.move(file_name_S,'./save/'+md5+'.jpg')
        else:
            string = '未匹配'
        if strtobool(config['time_log']):
            print('获取图片耗时:',dowtimend-dowtime,imgdow)
            if imgdow != '图像不符合':
                print('图片过滤耗时：',ocr_guolv_end-ocr_guolv)
            print("总耗时：", time.time() - start,time.strftime('%Y-%m-%d-%Hh-%Mm-%Ss',time.localtime(time.time())))
        try:
            os.remove(file_name)
        except:
            pass
        try:
            os.remove(file_name_S)
        except:
            pass
        print(string)
        return string
    except Exception as e:
        traceback.print_exc()
        try:
            os.remove(file_name)
        except:
            pass
        try:
            os.remove(file_name_S)
        except:
            pass
        return "未匹配"


@app.post('/ImageRandom/')#获取随机表情包
def get_image():
    global path
    file_list = os.listdir(path+'/save/')
    file_long = len(file_list)
    with open(path+'/save/'+file_list[random.randint(0, file_long-1)],'rb') as f:
        image = f.read()
        f.close()
    image_base64 = str(base64.b64encode(image), encoding='utf-8')
    return image_base64
    
    
    
start = time.time()
ocr2 = PaddleOCR(use_gpu=strtobool(config['gpu']),
                det_model_dir='./inference/db_mv3_infer',
                use_mp=True, total_process_num=6,show_log=False,drop_score=0.1)
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
    uvicorn.run(app, host="0.0.0.0", port=int(config['port']),access_log=strtobool(config['api_log']))
