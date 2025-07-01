import pandas as pd
from io import BytesIO
import os
import aiohttp
from io import BytesIO
import  asyncio
async def get_excel_data(excel_url,timeout=30):
    async with aiohttp.ClientSession() as session:
        async with session.get(excel_url, timeout=timeout, headers={'User-Agent': 'Mozilla/5.0'}) as response:
            try:
                response.raise_for_status()
                content = await response.read()
                excel_data = pd.read_excel(BytesIO(content), header=None,sheet_name=None)
                return True,[df for sheet_name, df in excel_data.items()]
            except Exception as e:
                return False,str(e)
# excel_url3 = r'https://csde-file.trinablue.com/prod/rsbu-mdm-contract-ps-api/20250415/67FA9A7EF43C4C448C5DCCE65D4C6F91_67fe1621e4b07c9d995bc5dc.xlsx'
#
# x = asyncio.run(get_excel_data("excel_url3"))
# print(x)