# from transformers import Qwen2TokenizerFast
from transformers import AutoModelForCausalLM, AutoTokenizer
class TokenizerSingleton:
    _instance = None
    def __new__(cls, url ="Qwen/Qwen2.5-0.5B-Instruct"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # local_files_only = True

            cls._instance.tokenizer = AutoTokenizer.from_pretrained(url,cache_dir="tokenizer",local_files_only=True)
            print("token单例被创建")
        return cls._instance

    def get_token_num(self,messages):
            text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            return len(self.tokenizer(text)["input_ids"])

    def get_tokenizer(self):
        return self.tokenizer
