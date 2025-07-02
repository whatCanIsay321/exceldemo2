from transformers import Qwen2TokenizerFast
class TokenizerSingleton:
    _instance = None
    def __new__(cls, url ="../tokenizer"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.tokenizer = Qwen2TokenizerFast.from_pretrained(url, local_files_only=True)
            print("token单例被创建")
        return cls._instance

    def get_token_num(self,messages):
            text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            return len(self.tokenizer(text)["input_ids"])

    def get_tokenizer(self):
        return self.tokenizer
