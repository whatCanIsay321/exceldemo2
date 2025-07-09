import asyncio
import httpx
import time
import os
import random
import string
import json
# ✅ 替换为你的一批测试请求体（多个 URL）
JSON_PAYLOADS = [
    {"url": "https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250418/A3A35DAAA6D14BE09426E833F6C9655E_6801fba3e4b07fedbab4d20a.xlsx"},
    {"url": "https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250304/254E7A6C359A451E8E4F90A7A38F9532_67c6ac87e4b0e5530b926592.xlsx"},
    {"url": "https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250415/67FA9A7EF43C4C448C5DCCE65D4C6F91_67fe1621e4b07c9d995bc5dc.xlsx"},
    {"url": "https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"},
    {"url": "https://csde-file.trinablue.com/test/rsbu-mdm-contract-ps-api/20250221/4AEE2E04146D4F5885025C41E513E681_67b81706e4b07d3d4d6b4ee0.xls"},
    {"url": "https://csde-file.trinablue.com/test/rsbu-mdm-contract-ps-api/20250305/965F681394FA4A41B5580E4583F01239_67c7b1dbe4b086e7ed9014ec.xlsx"},
    {"url": "https://csde-file.trinablue.com/test/rsbu-mdm-contract-ps-api/20250319/938F4173E5204F218AA375CFFD704E41_67da348ae4b099c0e5123f9e.xlsx"},
    {"url": "https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250418/A3A35DAAA6D14BE09426E833F6C9655E_6801fba3e4b07fedbab4d20a.xlsx"},
    {"url": "https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250304/254E7A6C359A451E8E4F90A7A38F9532_67c6ac87e4b0e5530b926592.xlsx"},
    {"url": "https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250415/67FA9A7EF43C4C448C5DCCE65D4C6F91_67fe1621e4b07c9d995bc5dc.xlsx"},
    {"url": "https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"},
    {"url": "https://csde-file.trinablue.com/test/rsbu-mdm-contract-ps-api/20250221/4AEE2E04146D4F5885025C41E513E681_67b81706e4b07d3d4d6b4ee0.xls"},
    {"url": "https://csde-file.trinablue.com/test/rsbu-mdm-contract-ps-api/20250305/965F681394FA4A41B5580E4583F01239_67c7b1dbe4b086e7ed9014ec.xlsx"},
    {"url": "https://csde-file.trinablue.com/test/rsbu-mdm-contract-ps-api/20250319/938F4173E5204F218AA375CFFD704E41_67da348ae4b099c0e5123f9e.xlsx"},
    {"url": "https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250418/A3A35DAAA6D14BE09426E833F6C9655E_6801fba3e4b07fedbab4d20a.xlsx"},
    {"url": "https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250304/254E7A6C359A451E8E4F90A7A38F9532_67c6ac87e4b0e5530b926592.xlsx"},
    {"url": "https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250415/67FA9A7EF43C4C448C5DCCE65D4C6F91_67fe1621e4b07c9d995bc5dc.xlsx"},
    {"url": "https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250318/F053943EE77A499FA4D4D84E8FC0CF9C_67d906c0e4b054f2346cd051.xlsx"},
    {"url": "https://csde-file.trinablue.com/test/rsbu-mdm-contract-ps-api/20250221/4AEE2E04146D4F5885025C41E513E681_67b81706e4b07d3d4d6b4ee0.xls"},
    {"url": "https://csde-file.trinablue.com/test/rsbu-mdm-contract-ps-api/20250305/965F681394FA4A41B5580E4583F01239_67c7b1dbe4b086e7ed9014ec.xlsx"},
    {"url": "https://csde-file.trinablue.com/test/rsbu-mdm-contract-ps-api/20250319/938F4173E5204F218AA375CFFD704E41_67da348ae4b099c0e5123f9e.xlsx"},

    # ...添加更多
]

ENDPOINT = "http://127.0.0.1:8000/items/"
CONCURRENT_LIMIT = 20
RESULT_DIR = "results"

os.makedirs(RESULT_DIR, exist_ok=True)

semaphore = asyncio.Semaphore(CONCURRENT_LIMIT)


async def post_request(client: httpx.AsyncClient, json_data: dict):
    async with semaphore:
        start = time.time()
        try:
            response = await client.post(ENDPOINT, json=json_data,timeout=600)
            elapsed = time.time() - start
            print(f"[{response.status_code}] {json_data['url']} | {elapsed:.2f}s")
            return {"url": json_data['url'], "status": response.status_code, "time": elapsed,
                    "body": response.text[:200],"json":response.json()}
        except Exception as e:
            print(f"[ERROR] {json_data['url']} -> {e}")
            return {"url": json_data['url'], "error": str(e)}
def generate_random_filename(prefix="result_", suffix=".json", length=8):
    rand_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    return f"{prefix}{rand_str}{suffix}"

async def main():
    async with httpx.AsyncClient() as client:
        tasks = [post_request(client, payload) for payload in JSON_PAYLOADS]
        results = await asyncio.gather(*tasks)
        print("\n✅ 全部请求完成，共 %d 条" % len(results))
        for i in results:
            json_str = i["json"]["parse"]

            filename = generate_random_filename()
            filepath = os.path.join(RESULT_DIR, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(json_str, f, ensure_ascii=False, indent=2)






if __name__ == "__main__":
    asyncio.run(main())
    # asyncio.run(send())



