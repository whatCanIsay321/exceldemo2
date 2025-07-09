import asyncio
from contextlib import asynccontextmanager
from src.prompt_manager import PromptManager
from src.config import Config
from pydantic import BaseModel
import json
import aiofiles
from fastapi import FastAPI, Depends,Request
import uvicorn
from src.llm_singleton import OpenAIClientSingleton
from src.get_excel import get_excel_data
from src.extract_graph import BuildGraph
from src.my_logger import logger
from src.extract_item import item
@asynccontextmanager
async def lifespan(app: FastAPI):
    config = Config()
    ex_item = item()
    render_parameters = ex_item.render_parameters
    for key, value in config.model_dump().items():
        PromptManager().register_base(key, value)
        if key in render_parameters:
            PromptManager().render_base(key, **render_parameters.get(key))
        else:
            PromptManager().render_base(key)
    PromptManager().set_primary_items(ex_item.primary_item)

    app.state.graph = BuildGraph().get_graph()
    logger.info("graph start")
    yield
    await OpenAIClientSingleton().close()
    logger.info("openai_client disconnect,app finished")



app = FastAPI(lifespan=lifespan)

def get_graph():
    return app.state.graph

class Item(BaseModel):
    url: str

@app.post("/items/")
async def create_item(item: Item,graph=Depends(get_graph)):
    url = item.url
    flag,excels =await get_excel_data(url)
    tasks=[]
    if flag==False:
        return {"error":"获取excel出错"},404
    else:
        for excel in excels:
            task = asyncio.create_task(graph.ainvoke({
                "llm_window": 7000,
                "excel_df":excel,
                "excel_dict": None,
                "excel_type": None,
                "flag":"",
                "type_one_head":None,
                "type_one_index":None,
                'type_two_exe_prompts': None,
                'chunks':  None,
                'result':  None,
                "error":None}))
            tasks.append(task)
        # loop = asyncio.get_running_loop()
        # logger.info(f"[create_item] gather即将运行在 loop id: {id(loop)}")
        reuslt = await asyncio.gather(*tasks)
        parse=[]
        for index,item in enumerate(reuslt):
            if item["error"]==None:
                parse.extend(item["result"])
                logger.info(f"{url}-第{index+1}张表-被分为{item["excel_type"]}类，通过{item["flag"]}提取出{len(item["result"])}")
            else:
                logger.error(f"{url}-第{index+1}张表-被分为{item["excel_type"]}类，通过{item["flag"]}提取失败。失败原因{item["error"]}")
        # async with aiofiles.open(output_filename, 'w', encoding="utf-8") as f:
        #     # 将list数据转换为JSON并写入文件
        #     await f.write(json.dumps(parse, ensure_ascii=False, indent=4))
        return {"parse":parse}






if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000)



