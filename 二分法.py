from transformers import AutoTokenizer
import pandas as pd
# 初始化 tokenizer（根据你的模型名）
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct", trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token  # 防止出错

# 固定前置 system 消息
system_message = {"role": "system", "content": "你是一个智能助手"}
max_tokens = 8000

def count_tokens(messages):
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
    return len(tokenizer(text)["input_ids"])

def find_max_index(df,max_tokens,system_prompt,user_prompt):
    left, right = 0, len(df)
    best = 0
    while left < right:
        mid = (left + right) // 2
        user_message = {"role": "user", "content": f"json的输入是{df[:mid]}"}
        messages = [system_message, user_message]
        num_tokens = count_tokens(messages)

        if num_tokens <= max_tokens:
            best = mid
            left = mid + 1
        else:
            right = mid
    return best
excel_data = pd.read_excel("./excel/最最特殊20250102171501269.xlsx", header=None, sheet_name=None)
excel_df=  [df for sheet_name, df in excel_data.items()]
df = excel_df[0]
df = df.to_dict(orient="index")
df = list(df.items())
print(find_max_index(df))