from jinja2 import Template
class PromptManager:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.prompts_base = {}
            cls._instance.prompts={}

        return cls._instance
    def get_primary_items(self):

        return self.primary_items

    def set_primary_items(self,items:list):

        self.primary_items= items

    def register_base(self, name: str, template: str):
        """注册一个 prompt 模板"""
        self.prompts_base[name] = Template(template)

    def render_base(self, name: str, **kwargs) -> str:
        """根据 name 和参数渲染 prompt"""
        if name not in self.prompts_base:
            raise KeyError(f"Prompt_base '{name}' not found.")
        self.prompts[name] =  self.prompts_base[name].render(**kwargs)


    def get(self, name: str, **kwargs) -> str:
        """根据 name 和参数渲染 prompt"""
        if name not in self.prompts:

            raise KeyError(f"Prompt '{name}' not found.")
        return self.prompts[name]

    # def update(self, name: str, new_template: str):
    #     """更新已有 prompt 模板"""
    #     self.prompts_base[name] = Template(new_template)

    # def delete(self, name: str):
    #     """删除 prompt"""
    #     if name in self.prompts_base:
    #         del self.prompts_base[name]

    def list_prompts(self):
        """列出所有 prompt 名字"""
        return list(self.prompts_base.keys())

