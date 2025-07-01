from jinja2 import Template
from typing import Dict
from config import  Config
class PromptManager:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.prompts = {}
        return cls._instance

    def register(self, name: str, template: str):
        """注册一个 prompt 模板"""
        self.prompts[name] = Template(template)

    def get(self, name: str, **kwargs) -> str:
        """根据 name 和参数渲染 prompt"""
        if name not in self.prompts:
            raise KeyError(f"Prompt '{name}' not found.")
        return self.prompts[name].render(**kwargs)

    def update(self, name: str, new_template: str):
        """更新已有 prompt 模板"""
        self.prompts[name] = Template(new_template)

    def delete(self, name: str):
        """删除 prompt"""
        if name in self.prompts:
            del self.prompts[name]

    def list_prompts(self):
        """列出所有 prompt 名字"""
        return list(self.prompts.keys())
# config = Config()
# config = Config()
#
# # 获取所有字段 key
# keys = config.dict().keys()
# pm = PromptManager()
# pm.register(config.depart_system)
x = f'fdafdsa\nmlk'
print(x)