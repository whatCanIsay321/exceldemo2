import asyncio
import httpx
import time
import os
import random
import string
import json
# ✅ 替换为你的一批测试请求体（多个 URL）
# JSON_PAYLOADS = [
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250418/A3A35DAAA6D14BE09426E833F6C9655E_6801fba3e4b07fedbab4d20a.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250304/254E7A6C359A451E8E4F90A7A38F9532_67c6ac87e4b0e5530b926592.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250415/67FA9A7EF43C4C448C5DCCE65D4C6F91_67fe1621e4b07c9d995bc5dc.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/test/rsbu-mdm-contract-ps-api/20250221/4AEE2E04146D4F5885025C41E513E681_67b81706e4b07d3d4d6b4ee0.xls"]},
#     {"url_list": ["https://csde-file.trinablue.com/test/rsbu-mdm-contract-ps-api/20250305/965F681394FA4A41B5580E4583F01239_67c7b1dbe4b086e7ed9014ec.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/test/rsbu-mdm-contract-ps-api/20250319/938F4173E5204F218AA375CFFD704E41_67da348ae4b099c0e5123f9e.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250418/A3A35DAAA6D14BE09426E833F6C9655E_6801fba3e4b07fedbab4d20a.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250304/254E7A6C359A451E8E4F90A7A38F9532_67c6ac87e4b0e5530b926592.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250415/67FA9A7EF43C4C448C5DCCE65D4C6F91_67fe1621e4b07c9d995bc5dc.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/test/rsbu-mdm-contract-ps-api/20250221/4AEE2E04146D4F5885025C41E513E681_67b81706e4b07d3d4d6b4ee0.xls"]},
#     {"url_list": ["https://csde-file.trinablue.com/test/rsbu-mdm-contract-ps-api/20250305/965F681394FA4A41B5580E4583F01239_67c7b1dbe4b086e7ed9014ec.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/test/rsbu-mdm-contract-ps-api/20250319/938F4173E5204F218AA375CFFD704E41_67da348ae4b099c0e5123f9e.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250418/A3A35DAAA6D14BE09426E833F6C9655E_6801fba3e4b07fedbab4d20a.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250304/254E7A6C359A451E8E4F90A7A38F9532_67c6ac87e4b0e5530b926592.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250415/67FA9A7EF43C4C448C5DCCE65D4C6F91_67fe1621e4b07c9d995bc5dc.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/test/rsbu-mdm-contract-ps-api/20250221/4AEE2E04146D4F5885025C41E513E681_67b81706e4b07d3d4d6b4ee0.xls"]},
#     {"url_list": ["https://csde-file.trinablue.com/test/rsbu-mdm-contract-ps-api/20250305/965F681394FA4A41B5580E4583F01239_67c7b1dbe4b086e7ed9014ec.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/test/rsbu-mdm-contract-ps-api/20250319/938F4173E5204F218AA375CFFD704E41_67da348ae4b099c0e5123f9e.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]},
#     {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"]}]
ENDPOINT = "http://127.0.0.1:8000/items/"

RESULT_DIR = "results"
os.makedirs(RESULT_DIR, exist_ok=True)


# 输入数据（你的例子）
JSON_PAYLOADS = [
    {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250709/0DF1D41CAFD54622BDED4375AB79F319_686dc920e4b0d82d7d861453.xlsx"]},
    {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250709/D6F5303F87C34668B01DCB39049AD556_686dca00e4b0df2808c16196.xlsx"]},
    {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250709/0DF1D41CAFD54622BDED4375AB79F319_686dc920e4b0d82d7d861453.xlsx"]},
    {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250709/D6F5303F87C34668B01DCB39049AD556_686dca00e4b0df2808c16196.xlsx"]},
    {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250709/0DF1D41CAFD54622BDED4375AB79F319_686dc920e4b0d82d7d861453.xlsx"]},
    {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250709/D6F5303F87C34668B01DCB39049AD556_686dca00e4b0df2808c16196.xlsx"]},
    {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250709/0DF1D41CAFD54622BDED4375AB79F319_686dc920e4b0d82d7d861453.xlsx"]},
    {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250709/D6F5303F87C34668B01DCB39049AD556_686dca00e4b0df2808c16196.xlsx"]},
    {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250709/0DF1D41CAFD54622BDED4375AB79F319_686dc920e4b0d82d7d861453.xlsx"]},
    {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250709/D6F5303F87C34668B01DCB39049AD556_686dca00e4b0df2808c16196.xlsx"]},
    {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250709/0DF1D41CAFD54622BDED4375AB79F319_686dc920e4b0d82d7d861453.xlsx"]},
    {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250709/D6F5303F87C34668B01DCB39049AD556_686dca00e4b0df2808c16196.xlsx"]},
    {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250709/0DF1D41CAFD54622BDED4375AB79F319_686dc920e4b0d82d7d861453.xlsx"]},
    {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250709/D6F5303F87C34668B01DCB39049AD556_686dca00e4b0df2808c16196.xlsx"]},
    {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250709/0DF1D41CAFD54622BDED4375AB79F319_686dc920e4b0d82d7d861453.xlsx"]},
    {"url_list": ["https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250709/D6F5303F87C34668B01DCB39049AD556_686dca00e4b0df2808c16196.xlsx"]},
    {"url_list": [
        "https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250709/0DF1D41CAFD54622BDED4375AB79F319_686dc920e4b0d82d7d861453.xlsx"]},
    {"url_list": [
        "https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250709/D6F5303F87C34668B01DCB39049AD556_686dca00e4b0df2808c16196.xlsx"]},
    {"url_list": [
        "https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250709/0DF1D41CAFD54622BDED4375AB79F319_686dc920e4b0d82d7d861453.xlsx"]},
    {"url_list": [
        "https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250709/D6F5303F87C34668B01DCB39049AD556_686dca00e4b0df2808c16196.xlsx"]},
    {"url_list": [
        "https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250709/0DF1D41CAFD54622BDED4375AB79F319_686dc920e4b0d82d7d861453.xlsx"]},
    {"url_list": [
        "https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250709/D6F5303F87C34668B01DCB39049AD556_686dca00e4b0df2808c16196.xlsx"]},
    {"url_list": [
        "https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250709/0DF1D41CAFD54622BDED4375AB79F319_686dc920e4b0d82d7d861453.xlsx"]},
    {"url_list": [
        "https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250709/D6F5303F87C34668B01DCB39049AD556_686dca00e4b0df2808c16196.xlsx"]},
    {"url_list": [
        "https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250709/0DF1D41CAFD54622BDED4375AB79F319_686dc920e4b0d82d7d861453.xlsx"]},
    {"url_list": [
        "https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250709/D6F5303F87C34668B01DCB39049AD556_686dca00e4b0df2808c16196.xlsx"]},
    {"url_list": [
        "https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250709/0DF1D41CAFD54622BDED4375AB79F319_686dc920e4b0d82d7d861453.xlsx"]},
    {"url_list": [
        "https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250709/D6F5303F87C34668B01DCB39049AD556_686dca00e4b0df2808c16196.xlsx"]},
    {"url_list": [
        "https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250709/0DF1D41CAFD54622BDED4375AB79F319_686dc920e4b0d82d7d861453.xlsx"]},
    {"url_list": [
        "https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250709/D6F5303F87C34668B01DCB39049AD556_686dca00e4b0df2808c16196.xlsx"]},
    {"url_list": [
        "https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250709/0DF1D41CAFD54622BDED4375AB79F319_686dc920e4b0d82d7d861453.xlsx"]},
    {"url_list": [
        "https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250709/D6F5303F87C34668B01DCB39049AD556_686dca00e4b0df2808c16196.xlsx"]},


]
print(len(JSON_PAYLOADS))

# 单个 POST 请求逻辑
async def post_request(client: httpx.AsyncClient, json_data: dict):

    start = time.time()
    try:
        response = await client.post(ENDPOINT, json=json_data, timeout=600)
        elapsed = time.time() - start
        print(f"[{response.status_code}] {json_data['url_list']} | {elapsed:.2f}s")
        return {
            "url_list": json_data['url_list'],
            "status": response.status_code,
            "time": elapsed,
            "body": response.text[:200],
            "json": response.json()
        }
    except Exception as e:
        print(f"[ERROR] {json_data['url_list']} -> {e}")
        return {
            "url_list": json_data['url_list'],
            "error": str(e)
        }

# 随机文件名生成
def generate_random_filename(prefix="result_", suffix=".json", length=8):
    rand_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    return f"{prefix}{rand_str}{suffix}"

# 主逻辑
async def main():
    async with httpx.AsyncClient() as client:
        tasks = [post_request(client, payload) for payload in JSON_PAYLOADS]
        results = await asyncio.gather(*tasks)

        print(f"\n✅ 全部请求完成，共 {len(results)} 条")

        for i in results:
            if "json" in i and "parse" in i["json"]:
                json_str = i["json"]["parse"]
                filename = generate_random_filename()
                filepath = os.path.join(RESULT_DIR, filename)
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(json_str, f, ensure_ascii=False, indent=2)
            else:
                print(f"⚠️ 跳过写入：{i.get('error') or '响应中无解析字段'}")

# 执行
if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    end_time = time.time()
    print(f"⏱️ 总耗时：{end_time - start_time:.2f} 秒")