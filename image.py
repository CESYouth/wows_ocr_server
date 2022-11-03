import cv2
import numpy as np
import httpx
import json

config = json.load(open('./config.json', 'r', encoding='utf8'))
img_size_max = config['img_size_max'].split(',')
img_size_min = config['img_size_min'].split(',')
img_aim_long = int(config['img_aim_long'])
for i in range(2):
    img_size_max[i] = int(img_size_max[i])
    img_size_min[i] = int(img_size_min[i])
def img_dow(image_url,file_name):
    data = httpx.get(image_url).content
    datalong = len(data)/1024/1024
    if datalong > 1:
        datalongstr = str(round(datalong,4))+'MB'
    else:
        datalongstr = str(round(datalong*1024,4))+'KB'
    if tuple(data[0:4]) == (0x47,0x49,0x46,0x38):
        print("图片类型为GIF跳过")
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
        return "ok"