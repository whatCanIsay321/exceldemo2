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

semaphore = asyncio.Semaphore(20)



def get_graph():
    return app.state.graph

class Item(BaseModel):
    url_list: list



@app.post("/items/")
async def create_item(item: Item,graph=Depends(get_graph)):
    GREEN = "\033[92m"
    YELLOW = '\033[93m'
    CYAN ="\033[96m"
    BLUE ="\033[94m"
    RESET = "\033[0m"
    if not semaphore.locked():  # 如果 Semaphore 还未被完全占满
        async with semaphore:
            total_parse=[]
            excels = []
            success=[]

            url_list = item.url_list
            for index , url in enumerate(url_list):
                url = url.strip()
                flag, excel = await get_excel_data(url)
                if flag == False:
                    return {"error": f"获取第{index+1}excel出错,excel获取地址:{url}"}, 404
                else:
                    excels.append(excel)
            for excel in excels:
                for sheet in excel:
                    tasks = []
                    parse = []
                    flag = True
                    task = asyncio.create_task(graph.ainvoke({
                        "llm_window": 7000,
                        "excel_df": sheet,
                        "excel_dict": None,
                        "excel_type": None,
                        "flag": "",
                        "type_one_head": None,
                        "type_one_index": None,
                        'type_two_exe_prompts': None,
                        'chunks': None,
                        'result': None,
                        "error": None,
                        'json_lost': 0,
                    }))
                    tasks.append(task)
                reuslt = await asyncio.gather(*tasks)
                for index, item in enumerate(reuslt):
                    if item["error"] == None:
                        parse.extend(item["result"])
                        logger.info(
                            f"{BLUE}\n正在解析{url}\n第{index + 1}张表\n被分为{item["excel_type"]}类\n,通过{item["flag"]}提取出{len(item["result"])}{RESET}")
                    else:
                        flag = False
                        if item["json_lost"] == 0:
                            logger.error(
                                f"\n正在解析{url}\n第{index + 1}张表\n被分为{item["excel_type"]}类\n,通过{item["flag"]}提取失败。失败原因{item["error"]}{RESET}")
                        else:
                            logger.error(
                                f"{YELLOW}\n正在解析{url}\n第{index + 1}张表\n被分为{item["excel_type"]}类\n,通过{item["flag"]}提取发生丢失。丢失原因原因{item["error"]}，提取出{len(item["result"])}{RESET}")
                if flag:
                    total_parse.extend(parse)
                    success.append(url)
                logger.info(
                    f"{CYAN}\n成功解析{url}\n一共{len(tasks)}张表\n,共提取出{len(parse)}{RESET}")
            logger.info(
                f"{GREEN}成功解析{url_list}\n{success}\n,共提取出{len(total_parse)}{RESET}")
            return {"parse": total_parse}
    else:
        raise HTTPException(status_code=429, detail="Too many concurrent requests")









if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000,reload=True)



