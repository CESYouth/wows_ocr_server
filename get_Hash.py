import cv2
import numpy as np
import os
import json

def cmpHash(hash1, hash2):
    # Hash值对比
    # 算法中1和0顺序组合起来的即是图片的指纹hash。顺序不固定，但是比较的时候必须是相同的顺序。
    # 对比两幅图的指纹，计算汉明距离，即两个64位的hash值有多少是不一样的，不同的位数越小，图片越相似
    # 汉明距离：一组二进制数据变成另一组数据所需要的步骤，可以衡量两图的差异，汉明距离越小，则相似度越高。汉明距离为0，即两张图片完全一样
    n = 0
    # hash长度不同则返回-1代表传参出错
    if len(hash1) != len(hash2):
        return -1
    # 遍历判断
    for i in range(len(hash1)):
        # 不相等则n计数+1，n最终为相似度
        if hash1[i] != hash2[i]:
            n = n + 1
    return n
def pHash(img):
    img = cv2.resize(img, (48, 48))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    dct = cv2.dct(np.float32(gray))
    # print(dct.shape)
    dct_roi = dct[0:12, 0:12]
    # print(dct_roi.shape)
    hash = []
    avreage = np.mean(dct_roi)
    for i in range(dct_roi.shape[0]):
        for j in range(dct_roi.shape[1]):
            if dct_roi[i, j] > avreage:
                hash.append(1)
            else:
                hash.append(0)
    return hash
def get_MD5Hash(path):
    path_list = os.listdir(path)
    with open(path+'../data.json','r') as f:
        jsonData = f.read()
        f.close()
        # print(jsonData)
    text = json.loads(jsonData)
    jishu = 0
    for filename in path_list:
        if os.path.splitext(filename)[1] == ".jpg":
            try:
                text[filename.replace('.jpg','')]
            except Exception as e:
                img = cv2.imread(path+filename,1)
                # print(path+filename,type(img))
                Hash = pHash(img)
                # print(type(hash))
                wirte_if = True
                for key in text:
                    data = text[key].replace('[','').replace(']','').replace(' ','').split(',')
                    for i in range(len(data)):
                        data[i] = int(data[i])
                    # print(data)
                    dst = cmpHash(Hash,data)
                    if dst < 4:
                        print('OUT_IMG',filename,key+'.jpg',dst)
                        os.remove(path+filename)
                        wirte_if = False
                        break
                if wirte_if:
                    jishu = jishu + 1
                    text.update({filename.replace('.jpg',''):str(Hash)})
                    with open(path+'../data.json','w') as f:
                        f.write(str(text).replace('\'','\"'))
                        f.close()
    print('Add_Data:',jishu,'Data_Long:',len(text))
if __name__ == '__main__':
    get_MD5Hash('./save/')