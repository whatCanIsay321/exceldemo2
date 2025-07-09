import re
import json
from src.config import Config
from src.token_singleton import TokenizerSingleton
import pandas as pd
from datetime import datetime
import jionlp
def date_format(date_str):
    date_str=str(date_str)
    flag = is_valid_yyyymm(date_str)
    if flag:
        return date_str,date_str
    else:
        try :
            date_time =  jionlp.parse_time(date_str)
            if len(date_time.get('time'))>0:
                start_dt = datetime.strptime(date_time.get('time')[0], '%Y-%m-%d %H:%M:%S')
                start_yyyymm = start_dt.strftime('%Y%m')
                end_dt = datetime.strptime(date_time.get('time')[1], '%Y-%m-%d %H:%M:%S')
                end_yyyymm = end_dt.strftime('%Y%m')
                return start_yyyymm,end_yyyymm
            else:
                return date_str,date_str
        except Exception as e:
            return date_str,date_str




def is_valid_yyyymm(s):
    try:
        datetime.strptime(str(s), '%Y%m')
        return True
    except ValueError:
        return False
def build_messages(system_prompt,user_prompt,input):
    input = json.dumps(input, separators=(",", ":"),ensure_ascii=False,indent=1)
    return [ {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{user_prompt}\n{input}/no_think"}]


def extract_json(input_str):

    json_str =re.search(r'(\{.*\})', input_str, re.DOTALL).group(1)
    json_str = json.loads(json_str)
    # 使用正则表达式提取 JSON 字符串（以 ```json 开头，``` 结束）
    return json_str

def extract_json_list(text):
    tail = text[-10:]

    # 判断是否包含 ']'
    if ']' not in tail:
        error = True
    else:
        error = False
    # 1. 匹配所有 JSON 对象的字符串（非贪婪匹配）
    matches = re.findall(r'\{.*?\}', text, re.DOTALL)

    # 2. 拼接为 JSON 数组字符串
    json_array_str = '[\n' + ',\n'.join(matches) + '\n]'

    # 3. 尝试解析为 JSON 列表
    try:
        return json.loads(json_array_str), error
    except json.JSONDecodeError as e:
        print("JSON 解析出错:", e)
        return [], True  # 或者 raise e，如果你希望上抛异常

def find_max_index(df,max_tokens,system_prompt,user_prompt):
    left, right = 0, len(df)
    best = 0
    while left < right:
        mid = (left + right) // 2
        messages = build_messages(system_prompt,user_prompt,dict(df[:mid]))
        num_tokens = TokenizerSingleton().get_token_num(messages)
        if num_tokens <= max_tokens:
            best = mid
            left = mid + 1
        else:
            right = mid
    return best



def get_window(excel_list,window,system_prompt,user_prompt):
    flag=False
    messages = build_messages(system_prompt,user_prompt,dict(excel_list))

    token_num = TokenizerSingleton().get_token_num(messages)
    if token_num<=window:
        flag = True
        return flag,messages
    else:
        index = find_max_index(excel_list,window,system_prompt,user_prompt)
        messages = build_messages(system_prompt, user_prompt, dict(excel_list[:index]))
        return flag,messages

def get_type_two_window(excel_list,window,start_index,system_prompt,user_prompt):
    #获取当前解析到excel第几行了，对excel进行切片。
    dict_list = excel_list[start_index:]
    dict_len = len(dict_list)
    current_dict = dict(dict_list)
    messages = build_messages(system_prompt,user_prompt,current_dict)
    token_num = TokenizerSingleton().get_token_num(messages)
    if token_num<=window:
        stop =True
        start_index = start_index
        next_start_index = dict_len+start_index
    else:
        index = find_max_index(dict_list, window, system_prompt, user_prompt)
        messages = build_messages(system_prompt, user_prompt, dict(dict_list[:index]))
        stop = False
        start_index=start_index
        next_start_index =index+start_index
    return stop,messages,start_index,next_start_index

def get_parse_window(chunks,excel_list, window, system_prompt, user_prompt):
    index = 0
    temp=[]
    result = []
    #因为用到了数组切片，所有将chunk中的最后一行索引+1
    dict_chunks = [[start, end + 1] for start, end in chunks]

    while index < len(dict_chunks):
        #index当前读取的切片块
        #current当前的切片索引数组
        current = dict_chunks[index]
        #合并工作区间，多个切片数组组成
        temp.append(current)
        #正真的合并工作区间
        current_slot = [temp[0][0],temp[-1][1]]
        #获取工作区间对应的dict数据项list
        current_dict_list = excel_list[current_slot[0]:current_slot[1]]
        #将list转为dict
        current_dict = dict(current_dict_list)
        messages = build_messages(system_prompt, user_prompt, current_dict)
        #当前工作区间对应的token数
        token_num = TokenizerSingleton().get_token_num(messages)
        if token_num<=window :
            #小于窗口，将切片数组索引后移一位，这是为了将下一个chunk添加在temp中来扩充提示词所涵盖的excel字典范围。
            index=index+1
            #如果切片索引超过了长度，表面当前是最后一个切片了，索引将结果直接插入
            if index >=len(dict_chunks):
                result.append([window>token_num, messages])
                break
        else:
            #如果单个直接超窗口，直接插入，将切片数组索引后移一位。
            if(len(temp)==1):
                result.append([False,messages])
                index=index+1
                temp=[]
            else:
                #如果不是单个窗口，表面之前的窗口都满足要求
                temp=temp[:-1]
                current_slot = [temp[0][0], temp[-1][1]]

                # 获取工作区间对应的dict数据项list
                current_dict_list = excel_list[current_slot[0]:current_slot[1]]
                # 将list转为dict
                current_dict = dict(current_dict_list)
                messages = build_messages(system_prompt, user_prompt, current_dict)
                result.append([True,messages])
                temp=[]
    return result
#
# error='''<think>
#
# </think>
#
# ```json
# [
#   {
#     "start_time": "202409",
#     "end_time": "202409",
#     "total_electricity": 1786,
#     "grid_electricity": 1785,
#     "payable_fee": 705.3,
#     "payable_tax": 81.14,
#     "grid_price": null,
#     "power_station": "博山供电中心源泉供电所",
#     "power_company": "宁阳众创新能源科技有限公司",
#     "generation_account": 3750011452491,
#     "transaction_id": null,
#     "meter_id": null
#   },
#   {
#     "start_time": "202409",
#     "end_time": "202409",
#     "total_electricity": 2888,
#     "grid_electricity": 2888,
#     "payable_fee": 1140.47,
#     "payable_tax": 131.2,
#     "grid_price": null,
#     "power_station": "博山供电中心源泉供电所",
#     "power_company": "宁阳众创新能源科技有限公司",
#     "generation_account": 3750011272801,
#     "transaction_id": null,
#     "meter_id": null
#   },
#   {
#     "start_time": "202409",
#     "end_time": "202409",
#     "total_electricity": 1792,
#     "grid_electricity": 1792,
#     "payable_fee": 707.66,
#     "payable_tax": 81.41,
#     "grid_price": null,
#     "power_station": "博山供电中心源泉供电所",
#     "power_company": "淄博嘉扬新能源科技有限公司",
#     "generation_account": 3750011485107,
#     "transaction_id": null,
#     "meter_id": null
#   },
#   {
#     "start_time": "202409",
#     "end_time": "202409",
#     "total_electricity": 3191,
#     "grid_electricity": 3191,
#     "payable_fee": 1260.13,
#     "payable_tax": 144.97,
#     "grid_price": null,
#     "power_station": "博山供电中心源泉供电所",
#     "power_company": "淄博嘉扬新能源科技有限公司",
#     "generation_account": 3750011571394,
#     "transaction_id": null,
#     "meter_id": null
#   },
#   {
#     "start_time": "202409",
#     "end_time": "202409",
#     "total_electricity": 2306,
#     "grid_electricity": 2306,
#     "payable_fee": 910.64,
#     "payable_tax": 104.76,
#     "grid_price": null,
#     "power_station": "博山供电中心源泉供电所",
#     "power_company": "淄博嘉扬新能源科技有限公司",
#     "generation_account": 3750011254720,
#     "transaction_id": null,
#     "meter_id": null
#   },
#   {
#     "start_time": "202409",
#     "end_time": "202409",
#     "total_electricity": 2346,
#     "grid_electricity": 2346,
#     "payable_fee": 926.44,
#     "payable_tax": 106.58,
#     "grid_price": null,
#     "power_station": "博山供电中心源泉供电所",
#     "power_company": "淄博嘉扬新能源科技有限公司",
#     "generation_account": 3750011272801,
#     "transaction_id": null,
#     "meter_id": null
#   },
#   {
#     "start_time": "202409",
#     "end_time": "202409",
#     "total_electricity": 4213,
#     "grid_electricity": 4213,
#     "payable_fee": 1663.71,
#     "payable_tax": 191.4,
#     "grid_price": null,
#     "power_station": "博山供电中心源泉供电所",
#     "power_company": "淄博嘉扬新能源科技有限公司",
#     "generation_account": 3750011440535,
#     "transaction_id": null,
#     "meter_id": null
#   },
#   {
#     "start_time": "202409",
#     "end_time": "202409",
#     "total_electricity": 2174,
#     "grid_electricity": 2174,
#     "payable_fee": 858.51,
#     "payable_tax": 98.77,
#     "grid_price": null,
#     "power_station": "博山供电中心源泉供电所",
#     "power_company": "淄博嘉扬新能源科技有限公司",
#     "generation_account": 3750011481116,
#     "transaction_id": null,
#     "meter_id": null
#   },
#   {
#     "start_time": "202409",
#     "end_time": "202409",
#     "total_electricity": 2501,
#     "grid_electricity": 2501,
#     "payable_fee": 987.64,
#     "payable_tax": 113.62,
#     "grid_price": null,
#     "power_station": "博山供电中心源泉供电所",
#     "power_company": "淄博嘉扬新能源科技有限公司",
#     "generation_account": 3750012341697,
#     "transaction_id": null,
#     "meter_id": null
#   },
#   {
#     "start_time": "202409",
#     "end_time": "202409",
#     "total_electricity": 1582,
#     "grid_electricity": 1582,
#     "payable_fee": 624.73,
#     "payable_tax": 71.87,
#     "grid_price": null,
#     "power_station": "博山供电中心源泉供电所",
#     "power_company": "淄博嘉扬新能源科技有限公司",
#     "generation_account": 3750012463623,
#     "transaction_id": null,
#     "meter_id": null
#   },
#   {
#     "start_time": "202409",
#     "end_time": "202409",
#     "total_electricity": 1445,
#     "grid_electricity": 1445,
#     "payable_fee": 570.63,
#     "payable_tax": 65.65,
#     "grid_price": null,
#     "power_station": "博山供电中心源泉供电所",
#     "power_company": "淄博嘉扬新能源科技有限公司",
#     "generation_account": 3750012137593,
#     "transaction_id": null,
#     "meter_id": null
#   },
#   {
#     "start_time": "202409",
#     "end_time": "202409",
#     "total_electricity": 3468,
#     "grid_electricity": 3468,
#     "payable_fee": 1369.51,
#     "payable_tax": 157.55,
#     "grid_price": null,
#     "power_station": "博山供电中心源泉供电所",
#     "power_company": "淄博嘉扬新能源科技有限公司",
#     "generation_account": 3750012564564,
#     "transaction_id": null,
#     "meter_id": null
#   },
#   {
#     "start_time": "202409",
#     "end_time": "202409",
#     "total_electricity": 4199,
#     "grid_electricity": 4199,
#     "payable_fee": 1658.19,
#     "payable_tax": 190.77,
#     "grid_price": null,
#     "power_station": "博山供电中心源泉供电所",
#     "power_company": "淄博嘉扬新能源科技有限公司",
#     "generation_account": 3750011501532,
#     "transaction_id": null,
#     "meter_id": null
#   },
#   {
#     "start_time": "202409",
#     "end_time": "202409",
#     "total_electricity": 1547,
#     "grid_electricity": 1547,
#     "payable_fee": 610.91,
#     "payable_tax": 70.28,
#     "grid_price": null,
#     "power_station": "博山供电中心源泉供电所",
#     "power_company": "淄博嘉扬新能源科技有限公司",
#     "generation_account": 3750011521137,
#     "transaction_id": null,
#     "meter_id": null
#   },
#   {
#     "start_time": "202409",
#     "end_time": "202409",
#     "total_electricity": 1558,
#     "grid_electricity": 1558,
#     "payable_fee": 615.25,
#     "payable_tax": 70.78,
#     "grid_price": null,
#     "power_station": "博山供电中心源泉供电所",
#     "power_company": "淄博嘉扬新能源科技有限公司",
#     "generation_account": 3750012348316,
#     "transaction_id": null,
#     "meter_id": null
#   },
#   {
#     "start_time": "202409",
#     "end_time": "202409",
#     "total_electricity": 1438,
#     "grid_electricity": 1438,
#     "payable_fee": 567.87,
#     "payable_tax": 65.33,
#     "grid_price": null,
#     "power_station": "博山供电中心源泉供电所",
#     "power_company": "淄博嘉扬新能源科技有限公司",
#     "generation_account": 3750012296313,
#     "transaction_id": null,
#     "meter_id": null
#   },
#   {
#     "start_time": "202409",
#     "end_time": "202409",
#     "total_electricity": 5128,
#     "grid_electricity": 5128,
#     "payable_fee": 2025.05,
#     "payable_tax": 232.97,
#     "grid_price": null,
#     "power_station": "博山供电中心源泉供电所",
#     "power_company": "淄博嘉扬新能源科技有限公司",
#     "generation_account": 3750011461542,
#     "transaction_id": null,
#     "meter_id": null
#   },
#   {
#     "start_time": "202409",
#     "end_time": "202409",
#     "total_electricity": 1932,
#     "grid_electricity": 1932,
#     "payable_fee": 762.95,
#     "payable_tax": 87.77,
#     "grid_price": null,
#     "power_station": "博山供电中心源泉供电所",
#     "power_company": "淄博嘉扬新能源科技有限公司",
#     "generation_account": 3750012424935,
#     "transaction_id": null,
#     "meter_id": null
#   },
#   {
#     "start_time": "202409",
#     "end_time": "202409",
#     "total_electricity": 1279,
#     "grid_electricity": 1279,
#     "payable_fee": 505.08,
#     "payable_tax": 58.11,
#     "grid_price": null,
#     "power_station": "博山供电中心源泉供电所",
#     "power_company": "淄博嘉扬新能源科技有限公司",
#     "generation_account": 3750011164410,
#     "transaction_id": null,
#     "meter_id": null
#   },
#   {
#     "start_time": "202409",
#     "end_time": "202409",
#     "total_electricity": 2841,
#     "grid_electricity": 2841,
#     "payable_fee": 1121.91,
#     "payable_tax": 129.07,
#     "grid_price": null,
#     "power_station": "博山供电中心源泉供电所",
#     "power_company": "淄博嘉扬新能源科技有限公司",
#     "generation_account": 3750012553535,
#     "transaction_id": null,
#     "meter_id": null
#   },
#   {
#     "start_time": "202409",
#     "end_time": "202409",
#     "total_electricity": 2545,
#     "grid_electricity": 2545,
#     "payable_fee": 1005.02,
#     "payable_tax": 115.62,
#     "grid_price": null,
#     "power_station": "博山供电中心源泉供电所",
#     "power_company": "淄博嘉扬新能源科技有限公司",
#     "generation_account": 3750012630319,
#     "transaction_id": null,
#     "meter_id": null
#   },
#   {
#     "start_time": "202409",
#     "end_time": "202409",
#     "total_electricity": 2720,
#     "grid_electricity": 2720,
#     "payable_fee": 1074.13,
#     "payable_tax": 123.57,
#     "grid_price": null,
#     "power_station": "博山供电中心源泉供电所",
#     "power_company": "淄博嘉扬新能源科技有限公司",
#     "generation_account": 3750011425850,
#     "transaction_id": null,
#     "meter_id": null
#   },
#   {
#     "start_time": "202409",
#     "end_time": "202409",
#     "total_electricity": 2964,
#     "grid_electricity": 2964,
#     "payable_fee": 1170.48,
#     "payable_tax": 134.66,
#     "grid_price": null,
#     "power_station": "博山供电中心源泉供电所",
#     "power_company": "淄博嘉扬新能源科技有限公司",
#     "generation_account": 3750011561213,
#     "transaction_id": null,
#     "meter_id": null
#   },
#   {
#     "start_time": "202409",
#     "end_time": "202409",
#     "total_electricity": 1295,
#     "grid_electricity": 1295,
#     "payable_fee": 511.4,
#     "payable_tax": 58.83,
#     "grid_price": null,
#     "power_station": "博山供电中心源泉供电所",
#     "power_company": "淄博嘉扬新能源科技有限公司",
#     "generation_account": 3750011632361,
#     "transaction_id": null,
#     "meter_id": null
#   },
#   {
#     "start_time": "202409",
#     "end_time": "202409",
#     "total_electricity": 2692,
#     "grid_electricity": 2692,
#     "payable_fee": 1063.07,
#     "payable_tax": 122.3,
#     "grid_price": null,
#     "power_station": "博山供电中心源泉供电所",
#     "power_company": "淄博嘉扬新能源科技有限公司",
#     "generation_account": 3750011451207,
#     "transaction_id": null,
#     "meter_id": null
#   },
#   {
#     "start_time": "202409",
#     "end_time": "202409",
#     "total_electricity": 1912,
#     "grid_electricity": 1912,
#     "payable_fee": 755.05,
#     "payable_tax": 86.86,
#     "grid_price": null,
#     "power_station": "博山供电中心源泉供电所",
#     "power_company": "淄博嘉扬新能源科技有限公司",
#     "generation_account": 3750011507671,
#     "transaction_id": null,
#     "meter_id": null
#   },
#   {
#     "start_time": "202409",
#     "end_time": "202409",
#     "total_electricity": 2073,
#     "grid_electricity": 2073,
#     "payable_fee": 818.63,
#     "payable_tax": 94.18,
#     "grid_price": null,
#     "power_station": "博山供电中心源泉供电所",
#     "power_company": "淄博嘉扬新能源科技有限公司",
#     "generation_account": 3750012546784,
#     "transaction_id": null,
#     "meter_id": null
#   },
#   {
#     "start_time": "202409",
#     "end_time": "202409",
#     "total_electricity": 2126,
#     "grid_electricity": 2126,
#     "payable_fee": 839.56,
#     "payable_tax": 96.59,
#     "grid_price": null,
#     "power_station": "博山供电中心源泉供电所",
#     "power_company": "淄博嘉扬新能源科技有限公司",
#     "generation_account": 3750011425852,
#     "transaction_id": null,
#     "meter_id": null
#   },
#   {
#     "start_time": "202409",
#     "end_time": "202409",
#     "total_electricity": 2811,
#     "grid_electricity": 2811,
#     "payable_fee": 1110.06,
#     "payable_tax": 127.71,
#     "grid_price": null,
#     "power_station": "博山供电中心源泉供电所",
#     "power_company": "淄博嘉扬新能源科技有限公司",
#     "generation_account": 3750011638483,
#     "transaction_id": null,
#     "meter_id": null
#   },
#   {
#     "start_time": "202409",
#     "end_time": "202409",
#     "total_electricity": 2410,
#     "grid_electricity": 2410,
#     "payable_fee": 951.71,
#     "payable_tax": 109.49,
#     "grid_price": null,
#     "power_station": "博山供电中心源泉供电所",
#     "power_company": "淄博嘉扬新能源科技有限公司",
#     "generation_account": 3750012598358,
#     "transaction_id": null,
#     "meter_id": null
#   },
#   {
#     "start_time": "202409",
#     "end_time": "202409",
#     "total_electricity": 2677,
#     "grid_electricity": 2677,
#     "payable_fee": 1057.15,
#     "payable_tax": 121.62,
#     "grid_price": null,
#     "power_station": "博山供电中心源泉供电所",
#     "power_company": "淄博嘉扬新能源科技有限公司",
#     "generation_account": 3750011574729,
#     "transaction_id": null,
#     "meter_id": null
#   },
#   {
#     "start_time": "202409",
#     "end_time": "202409",
#     "total_electricity": 1238,
#     "grid_electricity": 1238,
#     "payable_fee": 488.89,
#     "payable_tax": 56.24,
#     "grid_price": null,
#     "power_station": "博山供电中心源泉供电所",
#     "power_company": "淄博嘉扬新能源科技有限公司",
#     "generation_account": 3750012471751,
#     "transaction_id": null,
#     "meter_id": null
#   },
#   {
#     "start_time": "202409",
#     "end_time": "202409",
#     "total_electricity": 4671,
#     "grid_electricity": 4671,
#     "payable_fee": 1844.58,
#     "payable_tax": 212.21,
#     "grid_price": null,
#     "power_station": "博山供电中心源泉供电所",
#     "power_company": "淄博嘉扬新能源科技有限公司",
#     "generation_account": 3750011501542,
#     "transaction_id": null,
#     "meter_id": null
#   },
#   {
#     "start_time": "202409",
#     "end_time": "202409",
#     "total_electricity": 1737,
#     "grid_electricity": 1737,
#     "payable_fee": 685.94,
#     "payable_tax": 78.91,
#     "grid_price": null,
#     "power_station": "博山供电中心源泉供电所",
#     "power_company": "淄博嘉扬新能源科技有限公司",
#     "generation_account": 3750011142592,
#     "transaction_id": null,
#     "meter_id": null
#   },
#   {
#     "start_time": "202409",
#     "end_time": "202409",
#     "total_electricity": 2870,
#     "grid_electricity": 2870,
#     "payable_fee": 1133.36,
#     "payable_tax": 130.39,
#     "grid_price": null,
#     "power_station": "博山供电中心源泉供电所",
#     "power_company": "淄博临淄星沅新能源科技有限公司",
#     "generation_account": 3750011245440,
#     "transaction_id": null,
#     "meter_id": null
#   },
#   {
#     "start_time": "202409",
#     "end_time": "202409",
#     "total_electricity": 1353,
#     "grid_electricity": 1353,
#     "payable_fee": 534.3,
#     "payable_tax": 61.47,
#     "grid_price": null,
#     "power_station": "博山供电中心源泉供电所",
#     "power_company": "淄博临淄星沅新能源科技有限公司",
#     "generation_account": 3750012346010,
#     "transaction_id": null,
#     "meter_id": null
#   },
#   {
#     "start_time": "202409",
#     "end_time": "202409",
#     "total_electricity": 4645,
#     "grid_electricity": 4645,
#     "payable_fee": 1834.31,
#     "payable_tax": 211.03,
#     "grid_price": null,
#     "power_station": "博山供电中心源泉供电所",
#     "power_company": "淄博临淄星沅新能源科技有限公司",
#     "generation_account": 3750011176436,
#     "transaction_id": null,
#     "meter_id": null
#   },
#   {
#     "start_time": "202409",
#     "end_time": "202409",
#     "total_electricity": 7778,
#     "grid_electricity": 7'''
# import re
# import json
# from typing import List, Dict, Any
#
# def extract_json_objects_from_text(text: str) -> List[Dict[str, Any]]:
#     """
#     从包含多个 JSON 对象的原始文本中提取所有合法的 JSON 对象，组成一个 JSON 数组返回。
#
#     参数:
#         text (str): 含有多个 JSON 对象的原始字符串（可能是 LLM 输出）
#
#     返回:
#         List[Dict[str, Any]]: 一个包含所有成功解析对象的 JSON 列表
#     """
#     tail = text[-10:]
#
#     # 判断是否包含 ']'
#     if ']' not in tail:
#        error=True
#     else:
#        error=False
#     # 1. 匹配所有 JSON 对象的字符串（非贪婪匹配）
#     matches = re.findall(r'\{.*?\}', text, re.DOTALL)
#
#     # 2. 拼接为 JSON 数组字符串
#     json_array_str = '[\n' + ',\n'.join(matches) + '\n]'
#
#     # 3. 尝试解析为 JSON 列表
#     try:
#         return json.loads(json_array_str),error
#     except json.JSONDecodeError as e:
#         print("JSON :", e)
#         return [],False  # 或者 raise e，如果你希望上抛异常
