from openai import OpenAI,AsyncOpenAI
class OpenAIClientSingleton:
    _instance = None
    # url = 'https://api.deepseek.com'
    # ba = "http://10.60.200.100:11454/v1"
    def __new__(cls, api_key: str = 'sk-92ec31bcd1c743719fc9bda9b44b55ab', base_url: str = 'http://10.60.200.100:11454/v1'):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client = AsyncOpenAI(api_key=api_key, base_url=base_url,timeout=600)
            print("llm单例被创建")
        return cls._instance

    async def create_completion(self, messages: list, model: str = "Qwen/Qwen3-32B-AWQ", temperature: float = 0.0):
        # 调用 OpenAI API 的 chat.completions.create 方法
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            stream=False,
            temperature=0.0,

        )
        return response

    async def close(self):
        print("llm连接关闭")
        await self.client.close()