# from src.prompt_manager import PromptManager
# from src.config import Config
# from pydantic import BaseModel
# from src.llm_singleton import OpenAIClientSingleton
# from src.get_excel import get_excel_data
# from src.extract_graph import BuildGraph
# from src.my_logger import logger
# from src.extract_item import item
# config = Config()
# render_parameters = item().render_parameters
# for key, value in config.model_dump().items():
#     PromptManager().register_base(key,value)
#     if key in render_parameters:
#         PromptManager().render_base(key,**render_parameters.get(key))
#     else:
#         PromptManager().render_base()
x ={"1":[3,2,3],"2":[3,2,3]}
z = list(x.items())
print(z)
y = dict(z)
print(y)