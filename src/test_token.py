from token_singleton import TokenizerSingleton
import pandas as pd
import json
mytoken= TokenizerSingleton().get_tokenizer()
def count_token(tokenizer, messages):
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=True  # Switches between thinking and non-thinking modes. Default is True.
    )
    print(text)
    return len(tokenizer([text], return_tensors="pt").encodings[0].attention_mask)
excel_data = pd.read_excel("../excel/结算单-多表.xlsx", header=None, sheet_name=None)
excel_df=  [df for sheet_name, df in excel_data.items()]
df = excel_df[0]

df.dropna(how="all", inplace=True)
df.dropna(axis=1, how="all", inplace=True)
df.reset_index(drop=True, inplace=True)
excel_dict = json.loads(df.to_json(force_ascii=False, orient="index"))
dict_list = list(excel_dict.items())
x = dict_list[0]
system_p = '''你将要执行指定任务'''
# message_system =  [
#     {"role": "system", "content": system_p}
# ]
# message_0 = [
#     {"role": "user", "content": f'{x}'}
# ]
#
# message_1 = [
#     {"role": "system", "content": system_p},
#     {"role": "user", "content": f'{x}'}
# ]

# message12 = [
#     {"role": "system", "content": system_p},
#     {"role": "user", "content": {excel_dict[:2]}}
# ]

# print(count_token(mytoken,message_system))
# print(count_token(mytoken,message_0))
# print(count_token(mytoken,message_1))
texts = [
    mytoken.apply_chat_template(
        [{"role": "user", "content": f'{messages}'}],
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=True  # 可选参数
    )
    for messages in dict_list
]
# print(texts)

encodings = mytoken(texts, return_tensors="pt",padding=True, truncation=True,max_length=1024)
token_counts = [mask.sum().item() for mask in encodings["attention_mask"]]
# token_counts = [len(mask.attention_mask) for mask in encodings]
print(token_counts)