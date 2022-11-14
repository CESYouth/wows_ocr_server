import requests
import json
import difflib
import re
from interval import Interval

kongge = ['wws', 'me', 'ship.rank','rank', 'recent','切换绑定' ,'绑定', '国服', '亚服', '俄服', '美服','cn','asia','na','eu','help','ship','bind']
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
    if texts_score[-1][1] > 0.5:
        match_value = texts_score[-1][0]
    else:
        match_value = ''
    return match_value

def Text_Chuli(rec):
    string = align_text(rec)
    string = string.replace(' ','')
    print(string)
    if len(string) > 50 or len(string) < 5:
        return "未匹配"
    switch = True
    if 'ship.rank' in string:
        switch = False
    for i in range(0, len(kongge)):
        if switch == False and kongge[i] in 'rank,ship':
            break
        dst_path = string.lower().find(kongge[i])
        if dst_path != -1 and dst_path + len(kongge[i]) < len(string) and string[dst_path + len(kongge[i])] != ' ':
            string = string[0:dst_path]+' '+string[dst_path:dst_path + len(kongge[i])] + ' ' + string[dst_path + len(kongge[i]):len(string)]
    #关键词后添加空格
    # print(string)
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
    # print(string)
    match = re.search(r"^(.*?)wws(.*?)$",string)
    if match:
        string = re.sub(r"^(.*?)(?=wws)","",string)
    else:
        string = '未匹配'
        return string
    list = string.split(' ')
    if len(list) < 3:
        for i in range(len(list)):
            if i != 0 and not(list[i-1] in 'recent' or list[i-1] in server or list[i-1] in server or list[i-1] in 'ship.rank'):
                list[i] = fuzzy_matching(kongge,list[i])
        string = ' '.join(list)
        return string
    #正则匹配
    # print(list)
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
    if list[2] == 'ship':
        list[3] = fuzzy_matching(name_list,list[3])
    if list[2] == 'ship' and len(list) > 4:
        # print(len(list))
        if list[4] != 'recent':
            for i in range(len(list)-1,3,-1):
                list.pop(i)
    elif list[2] == 'recent' and len(list) >= 3:
        for i in range(len(list)-1,3,-1):
            list.pop(i)
    # print(list)
    for i in range(len(list)):
        if i != 0 and not(list[i-1] in 'recent' or list[i-1] in server or list[i-1] in 'ship.rank'):
            list[i] = fuzzy_matching(kongge,list[i])
            
            
    string = ' '.join(list)
    return string

def align_text(res):
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