import re
import json
from src.config import Config
from src.token_singleton import TokenizerSingleton
import pandas as pd

def build_messages(system_prompt,user_prompt,input):
    input = json.dumps(input, separators=(",", ":"),ensure_ascii=False,indent=1)
    return [ {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{user_prompt}\n{input}/no_think"}]


def extract_json(input_str):
    json_str =re.search(r'(\{.*\})', input_str, re.DOTALL).group(1)
    json_str = json.loads(json_str)
    # 使用正则表达式提取 JSON 字符串（以 ```json 开头，``` 结束）
    return json_str

def extract_json_list(input_str):
    json_str =re.search(r'(\[.*\])', input_str, re.DOTALL).group(1)
    json_str = json.loads(json_str)
    # 使用正则表达式提取 JSON 字符串（以 ```json 开头，``` 结束）
    return json_str

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

