from transformers import Qwen2TokenizerFast
class TokenizerSingleton:
    _instance = None
    # url = 'https://api.deepseek.com'
    # ba = "http://10.60.200.100:11454/v1"
    def __new__(cls, url ="../tokenizer"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.tokenizer = Qwen2TokenizerFast.from_pretrained(url, local_files_only=True)
            print("token单例被创建")
        return cls._instance

    def get_token_num(self,messages):
            text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            return len(tokenizer(text)["input_ids"])

    def get_tokenizer(self):
        return self.tokenizer
    #
    # def get_token_num_for_every_line(self,excel_dict):
    #     texts = [
    #         self.tokenizer.apply_chat_template(
    #             [{"role": "user", "content": f'{line}'}],
    #             tokenize=False,
    #             add_generation_prompt=True,
    #             enable_thinking=True  # 可选参数
    #         )
    #         for line in list(excel_dict.items())
    #     ]
    #     # print(texts)
    #
    #     encodings = self.tokenizer(texts, return_tensors="pt", padding=True, truncation=True, max_length=1024)
    #     token_counts = [mask.sum().item() for mask in encodings["attention_mask"]]
    #     return token_counts
    #
    # def get_input_window(self,system_prompt,user_prompt,excel_token,max_token):


# message = [
#     {"role": "system", "content": "system_prompt"},
#     {"role": "user", "content": f"no_think"}
# ]
x = TokenizerSingleton().get_tokenizer()

print(x.padding_side)
