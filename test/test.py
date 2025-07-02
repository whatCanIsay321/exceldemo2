
from modelscope import AutoModelForCausalLM, AutoTokenizer

import  pandas as pd
def get_current_temperature(location: str, unit: str) -> float:
    """
    Get the current temperature at a location.

    Args:
        location: The location to get the temperature for, in the format "City, Country"
        unit: The unit to return the temperature in. (choices: ["celsius", "fahrenheit"])
    Returns:
        The current temperature at the specified location in the specified units, as a float.
    """
    return 22.  # A real function should probably actually get the temperature!


def get_current_wind_speed(location: str) -> float:
    """
    Get the current wind speed in km/h at a given location.

    Args:
        location: The location to get the temperature for, in the format "City, Country"
    Returns:
        The current wind speed at the given location in km/h, as a float.
    """
    return 6.  # A real function should probably actually get the wind speed!


# tools = [get_current_temperature, get_current_wind_speed]

tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")
# tokeni.apply_chat_template()


excel_data = pd.read_excel("./excel/最最特殊20250102171501269.xlsx", header=None, sheet_name=None)
excel_df=  [df for sheet_name, df in excel_data.items()]
df = excel_df[0]
df = df.to_dict(orient="index")
message = [
    {"role": "system", "content": "你是一个智能助手"},
    {"role": "user", "content": f"json的输入是{df}"}]

text = tokenizer.apply_chat_template(
    message,
    tokenize=False,
    add_generation_prompt=True,
    # Switches between thinking and non-thinking modes. Default is True.
)
input_ids = tokenizer([text])

print(input_ids)
# messages = [
#     {
#       "from": "user",
#       "value": "你好，我出生于1990年5月15日。你能告诉我我今天几岁了吗？"
#     },
#     {
#       "from": "function_call",
#       "value": "{\"name\": \"calculate_age\", \"arguments\": {\"birthdate\": \"1990-05-15\"}}"
#     },
#     {
#       "from": "observation",
#       "value": "{\"age\": 31}"
#     },
#     {
#       "from": "gpt",
#       "value": "根据我的计算，你今天31岁了。"
#     }
#   ],

# tokenized_chat = tokenizer.apply_chat_template(example,tools=tools,tokenize=False, add_generation_prompt=True)
# print(tokenized_chat)
# print(tokenizer.chat_template)
