import json
import asyncio

from datetime import datetime

import jionlp as jio

from src.utils import *
from langgraph.graph import StateGraph, MessagesState, START, END
from typing import TypedDict, Any
from langgraph.types import Command
from src.llm_singleton import OpenAIClientSingleton
from src.token_singleton import TokenizerSingleton
from src.config import Config
import pandas as pd
import aiofiles
from src.extract_item import item
from src.prompt_manager import PromptManager

class State(TypedDict):
    llm_window:int

    excel_df:Any
    excel_dict:Any
    excel_list:Any
    excel_type: dict | None
    flag :str

    type_one_head:dict | None
    type_one_index:dict | None
    type_one_common:dict | None

    type_two_exe_prompts :Any
    chunks:Any
    result:list | None

    error:str


class PreProcessNode:
    def __call__(self, state: State):
        df = state["excel_df"].dropna(how="all").dropna(axis=1, how="all").reset_index(drop=True)
        excel_dict = json.loads(df.to_json(force_ascii=False, orient="index"))
        clean_dict = {}
        for key, value in excel_dict.items():
            d_clean = {k: v for k, v in value.items() if v is not None}
            clean_dict[key] = d_clean
        excel_list = list(clean_dict.items())
        return Command(update={"excel_df":df,"excel_dict": clean_dict,"excel_list":excel_list}, goto="FineTypeBot")

class FineTypeNode:
    def __init__(self, type_system_prompt,count_system_prompt,final_system_prompt):
        self.type_system_prompt = type_system_prompt
        self.count_system_prompt = count_system_prompt
        self.final_system_prompt=final_system_prompt

    async def __call__(self, state: State):
        llm_window = state["llm_window"]
        excel_list = state["excel_list"]
        if excel_list != []:
            user_prompt = f"Json格式的Excel表格："
            type_flag,type_messages = get_window(excel_list,llm_window,self.type_system_prompt,user_prompt)
            count_flag,count_messages = get_window(excel_list,llm_window,self.count_system_prompt,user_prompt)

            try:
                type_response =await OpenAIClientSingleton().create_completion(messages=type_messages)
                type_result = type_response.choices[0].message.content
                type_result_json = extract_json(type_result)
                type_result_type = int(type_result_json["type"])

                count_response = await OpenAIClientSingleton().create_completion(messages=count_messages)
                count_result = count_response.choices[0].message.content
                count_result_json = extract_json(count_result)
                count_result_count = int(count_result_json["count"])

                final_messages = build_messages(self.final_system_prompt,user_prompt,dict(excel_list))
                token_num = TokenizerSingleton().get_token_num(final_messages)
                # return Command(update={"excel_type": type_result_type, "flag": "直接送入模型"},
                #                goto="OnlyllmBot")

                if type_result_type == 1:
                    if token_num > llm_window:
                        return Command(update={"excel_type": type_result_type, "flag": "通过函数"},
                                       goto="TypeOneGetHeadBot")
                    else:
                        if count_result_count>10:
                            return Command(update={"excel_type": type_result_type, "flag": "通过函数"},
                                           goto="TypeOneGetHeadBot")
                        else:
                            return Command(update={"excel_type": type_result_type, "flag": "直接送入模型"},
                                           goto="OnlyllmBot")
                else:
                    if token_num > llm_window:
                        return Command(update={"excel_type": type_result_type, "flag": "通过切片"},
                                       goto="TypeTwoGetChunksBot")
                    else:
                        return Command(update={"excel_type": type_result_type, "flag": "直接送入模型"}, goto="OnlyllmBot")

            except Exception as e:
                exception_message = str(e)
                return Command(update={"error": f"FineTypeNode出错：{exception_message}"}, goto='FinshBot')
        else:
            return Command(update={"excel_type": 1,"result": []}, goto='FinshBot')

class TypeOneGetHeadNode:
    def __init__(self, system_prompt):
        self.system_prompt = system_prompt

    async def __call__(self, state: State):
        head_index = 30
        llm_window = state["llm_window"]
        excel_list = state["excel_list"][:head_index]
        user_prompt = "JSON格式的Excel表格："
        flag, messages = get_window(excel_list, llm_window, self.system_prompt, user_prompt)
        try:
            response =await OpenAIClientSingleton().create_completion(messages=messages)
            result = response.choices[0].message.content
            result_json = extract_json(result)
            return Command(update={"type_one_head": result_json}, goto="TypeOneGetIndexBot")
        except Exception as e:
            exception_message = str(e)
            return Command(update={"error": f"TypeOneGetHeadNode出错：{exception_message}"}, goto='FinshBot')
class TypeOneGetIndexNode:
    def __init__(self, system_prompt):
        self.system_prompt = system_prompt

    async def __call__(self, state: State):
        head_index = 30
        llm_window = state["llm_window"]
        excel_list = state["excel_list"][:head_index]
        user_prompt = "JSON格式的Excel表格："
        flag, message = get_window(excel_list, llm_window, self.system_prompt, user_prompt)
        try:
            response = await OpenAIClientSingleton().create_completion(messages=message)
            result = response.choices[0].message.content
            result_json = extract_json(result)
            return Command(update={"type_one_index": result_json}, goto="TypeOneGetCommonBot")
        except Exception as e:
            exception_message = str(e)
            return Command(update={"error": f"TypeOneGetIndexNode出错：{exception_message}"}, goto='FinshBot')
class TypeOneGetCommonNode:
    def __init__(self, system_prompt):
        self.system_prompt = system_prompt

    async def __call__(self, state: State):
        llm_window = state["llm_window"]
        head_index = int(state["type_one_head"]["index"])
        excel_list = state["excel_list"][:head_index+1]


        user_prompt = "JSON格式的Excel表格："
        messages = build_messages(self.system_prompt, user_prompt,dict(excel_list))

        try:
            response = await OpenAIClientSingleton().create_completion(messages=messages)
            result = response.choices[0].message.content
            result_json = extract_json(result)
            return Command(update={"type_one_common": result_json}, goto="TypeOneExeBot")
        except Exception as e:
            exception_message = str(e)
            return Command(update={"error": f"TypeOneGetCommonNode出错：{exception_message}"}, goto='FinshBot')


class TypeOneExeNode:
     async def __call__(self, state: State):
         count=0
         result=[]
         index = state["type_one_index"]
         common = state["type_one_common"]
         start_row = int(state["type_one_head"]["index"])
         excel_list = list(state["excel_dict"].values())[start_row+1:]
         flag = False
         try:
             for i,data in enumerate(excel_list):
                 start_from_start = None
                 end_from_start = None
                 start_from_end = None
                 end_from_end = None
                 temp = {
                     key: data.get(str(value)) if value is not None else None
                     for key, value in index.items()
                 }
                 start_time_str = temp.get('start_time')
                 end_time_str = temp.get('end_time')
                 if start_time_str:
                    start_from_start,end_from_start = date_format(start_time_str)
                 if end_time_str:
                    start_from_end,end_from_end = date_format(end_time_str)


                 if start_from_start :
                     temp['start_time']=start_from_start
                 elif start_from_end:
                     temp['start_time'] = start_from_end
                 if end_from_end:
                     temp['end_time'] = end_from_end
                 elif end_from_start:
                     temp['end_time'] = end_from_start


                 temp = self.merge_dicts(temp,common)
                 fields = PromptManager().get_primary_items()

                 if any(str(temp.get(field)).isdigit() for field in fields if temp.get(field) is not None):


                     if flag == False:
                         count = self.count_non_empty_fields(temp)
                         flag=True
                         result.append(temp)
                     else:
                         #对字段做是数字验证。
                         if self.count_non_empty_fields(temp) >= count:
                             result.append(temp)
                         else:
                             continue


             return Command(update={"result":result},goto='FinshBot')
         except Exception as e:
                exception_message = str(e)
                return Command(update={"error": f"TypeOneExeNode出错：{exception_message}"}, goto='FinshBot')

     def merge_dicts(self,dict1,dict2):  #
         for key, value in dict2.items():  # 遍历第二个字典
             if key in dict1 and  dict1[key]!=None:  # 如果第一个字典已有该键
                 if value!=None:  # 如果第一个字典的值是None
                     dict1[key] = value  # 用第二个字典的值替换
             else:
                 dict1[key] = value  # 如果第一个字典没有该键，直接添加
         return dict1

     def count_non_empty_fields(self,dict):
         count = 0
         for value in dict.values():
             if value != None:  # 判断值是否为空
                 count += 1
         return count



class TypeTwoGetChunksNode:
    def __init__(self, system_prompt):
        self.system_prompt = system_prompt

    def process(self, chunks, start_index, next_start_index):
        result = []
        chunks_len = len(chunks)
        #如果沒有主要表格，直接將當前窗口内的excel算一個完整的块
        if chunks_len==0:
            result.append({
                "chunk": [start_index, next_start_index-1],
                "flag": True
            })
        else:
            for chunk in chunks:
                start = min(chunk[0],start_index)
                end = chunk[1]
                #如果這个块的最后一行不是当前窗口的最后一行，说明这个块肯定是完整的。
                if end < next_start_index-1:
                    result.append({
                        "chunk":[start,end],
                        "flag":True
                    })
                else:
                    # 如果這个块的最后一行是当前窗口的最后一行，说明这个块不一定是完整的。
                    result.append({
                        "chunk": [start, end],
                        "flag": False
                    })
                #下一个完整块的第一行肯定是当前完整快最后一行+1
                start_index= end+1
        return result

    async def __call__(self, state: State):
        llm_window = state["llm_window"]
        #当前从excel哪一行开始
        start_index =0
        next_start_index = 0
        stop = False
        chunks=[]
        excel_list = state["excel_list"]
        user_prompt=  f"Json格式的Excel表格："
        while stop==False:
            stop,messages,start_index,next_start_index = get_type_two_window(excel_list,llm_window,start_index,self.system_prompt,user_prompt)
            if stop:
                chunk = [start_index, next_start_index - 1]
                chunks.append(chunk)
                print(f"加载了{chunk}")
            else:
                try:
                    response = await OpenAIClientSingleton().create_completion(messages=messages)
                    result = response.choices[0].message.content
                    result_json = extract_json(result)
                    #在指定模型上下文长度之内，主要excel块和额外excel块
                    main_chunks = [[int(x) for x in inner] for inner in result_json["main"]]
                    extra_chunks = [[int(x) for x in inner] for inner in result_json["extra"]]
                    #将两种块合并，得到一个个完整的块。对于当前的上下文窗口来说
                    temp_chunks=self.process(main_chunks,start_index,next_start_index)
                    #将所有的合并块插入到一个列表中，如果当前块是主要块，但是不确定是否被截断，则将游标左移。
                    for i,item in enumerate(temp_chunks):
                        chunk = item["chunk"]
                        flag = item["flag"]
                        #如果是完整的主要快或者全部是次要块，则插入。
                        if flag == True or len(temp_chunks)==1:
                            chunks.append(chunk)
                            print(f"加载了{chunk}")
                            # 如果顺利的将所有块插入了，则下次的工作窗口就是这次的最后一行的下一行。
                            if i == len(temp_chunks) - 1:
                                start_index = chunk[1] + 1
                                break
                        else:
                            # 如果不是完整的主要快或者全部是次要块，则将游标左移。
                            start_index = chunk[0]
                            break
                except Exception as e:
                    exception_message = str(e)
                    return Command(update={"error": f"TypeTwoGetChunksNode出错：{exception_message}"}, goto='FinshBot')
        return Command(update={"chunks": chunks}, goto="TypeTwoGetPromptsBot")


class TypeTwoGetPromptsNode:
    def __init__(self, system_prompt):
        self.system_prompt = system_prompt

    def __call__(self, state: State):
        llm_window = state["llm_window"]
        excel_list = state["excel_list"]
        chunks =state["chunks"]
        user_prompt = f"'Json格式的Excel表格："
        result = get_parse_window(chunks,excel_list,llm_window,self.system_prompt,user_prompt)
        return Command(update={"type_two_exe_prompts": result}, goto="TypeTwoExeBot")

class TypeTwoExeNode():
    async def __call__(self, state: State):
        json_list=[]
        type_two_exe_prompt=state["type_two_exe_prompts"]
        tasks=[]
        try:
            for messages in type_two_exe_prompt:
                task = asyncio.create_task(OpenAIClientSingleton().create_completion(messages=messages[1]))
                tasks.append(task)
            task_reuslt = await asyncio.gather(*tasks)
            result = [response.choices[0].message.content for response in task_reuslt]
            json_list = []
            json_errors = []
            for i in result:
                items, errors = extract_json_list(i)  # 假设返回值是 (List[item], List[error])
                json_list.extend(items)
                json_errors.extend(errors)
            if True in json_errors:
                exception_message = "发生了json缺失"
                return Command(update={"result": json_list,"error": f"TypeTwoExeNode出错：{exception_message}"}, goto='FinshBot')
            else:
                return Command(update={"result": json_list},
                               goto='FinshBot')
        except Exception as e:
            exception_message = str(e)
            return Command(update={"error": f"TypeTwoExeNode出错：{exception_message}"}, goto='FinshBot')








class OnlyllmNode:
    def __init__(self, system_prompt):
        self.system_prompt = system_prompt
    async def __call__(self, state: State):
        excel_dict=state["excel_dict"]
        user_prompt = f"Json格式的Excel表格："
        messages = build_messages(self.system_prompt, user_prompt,excel_dict)
        try:
            # loop = asyncio.get_running_loop()
            # print(f"[create_item] gather即将运行在 loop id: {id(loop)}")

            response =await OpenAIClientSingleton().create_completion(messages=messages)
            result = response.choices[0].message.content
            json_list,error = extract_json_list(result)
            if error == True:
                exception_message = "发生了json缺失"
                return Command(update={"result": json_list, "error": f"TypeTwoExeNode出错：{exception_message}"},
                               goto='FinshBot')
            else:
                return Command(update={"result": json_list},
                               goto='FinshBot')

        except Exception as e:
            exception_message = str(e)
            return Command(update={"error": f"OnlyllmNode出错：{exception_message}"}, goto='FinshBot')

class FinishNode:
    async  def __call__(self, state: State):
        return



class BuildGraph:
    def __init__(self):
        self.graph = self.build_graph()

    def build_graph(self):
        config  = Config()
        graph_builder = StateGraph(State)
        PreProcessBot = PreProcessNode()
        ##################
        FineTypeBot = FineTypeNode(PromptManager().get("type_system"),PromptManager().get("count_items_system"),PromptManager().get("prompt"))
        TypeOneGetHeadBot = TypeOneGetHeadNode(PromptManager().get("get_head_system"))
        TypeOneGetIndexBot = TypeOneGetIndexNode(PromptManager().get("get_index_system"))
        TypeOneGetCommonBot = TypeOneGetCommonNode(PromptManager().get("get_head_common_system"))
        TypeOneExeBot = TypeOneExeNode()
        ##################
        TypeTwoGetChunksBot =TypeTwoGetChunksNode(PromptManager().get("depart_system"))
        TypeTwoGetPromptsBot=TypeTwoGetPromptsNode(PromptManager().get("prompt"))
        TypeTwoExeBot = TypeTwoExeNode()
        ##################
        OnlyllmBot = OnlyllmNode(PromptManager().get("prompt"))
        ##################
        FinshBot =FinishNode()

        ##################
        graph_builder.add_node("PreProcessBot", PreProcessBot)
        graph_builder.add_node("FineTypeBot", FineTypeBot)
        graph_builder.add_node("TypeOneGetHeadBot", TypeOneGetHeadBot)
        graph_builder.add_node("TypeOneGetIndexBot", TypeOneGetIndexBot)
        graph_builder.add_node("TypeOneGetCommonBot", TypeOneGetCommonBot)
        graph_builder.add_node("TypeOneExeBot", TypeOneExeBot)
        graph_builder.add_node("TypeTwoGetChunksBot",TypeTwoGetChunksBot)
        graph_builder.add_node("TypeTwoGetPromptsBot", TypeTwoGetPromptsBot)
        graph_builder.add_node("TypeTwoExeBot", TypeTwoExeBot)
        graph_builder.add_node("OnlyllmBot", OnlyllmBot)
        graph_builder.add_node("FinshBot", FinshBot)
        graph_builder.add_edge(START, "PreProcessBot")
        graph_builder.add_edge("FinshBot", END)

        ##################

        graph = graph_builder.compile()
        return graph

    def get_graph(self):
        return self.graph



if __name__ == "__main__":
    config = Config()
    ex_item = item()
    # tokenizer = TokenizerSingleton().get_tokenizer()
    # num1 = len(tokenizer(config.depart_system)["input_ids"])
    # num2 =len(tokenizer(config.prompt)["input_ids"])
    render_parameters = ex_item.render_parameters
    for key, value in config.model_dump().items():
        PromptManager().register_base(key,value)
        if key in render_parameters:
            PromptManager().render_base(key,**render_parameters.get(key))
        else:
            PromptManager().render_base(key)
    PromptManager().set_primary_items(ex_item.primary_item)
    excel_data = pd.read_excel("../excel/4分钟.xlsx", header=None, sheet_name=None)
    excel_df=  [df for sheet_name, df in excel_data.items()]
    df = excel_df[0]
    graph = BuildGraph().get_graph()
    async def get_item():
        result = await graph.ainvoke(input={
            "llm_window": 6000,
            "excel_df":df,
            "excel_dict": None,
            "excel_list":None,
            "excel_type": None,
            "type_one_head":None,
            "type_one_index":None,


            'type_two_exe_prompts': None,
            'chunks':  None,
            'result':  None,
        })  # 调用异步函数并等待结果
        print(f"获取的结果是: {result}")
        x = result["result"]

        async with aiofiles.open("output_filename.json", 'w', encoding="utf-8") as f:
            # 将list数据转换为JSON并写入文件
            await f.write(json.dumps(result["result"], ensure_ascii=False, indent=4))

    #
    #
    # # 运行异步事件循环
    asyncio.run(get_item())  # 在 Python 3.7+ 中，使用 asyncio.run 来执行主函数
