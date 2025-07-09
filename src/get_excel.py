import pandas as pd
import aiohttp
from io import BytesIO
async def get_excel_data(excel_url,timeout=60):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(excel_url, timeout=timeout, headers={'User-Agent': 'Mozilla/5.0'}) as response:
                response.raise_for_status()
                content = await response.read()
                excel_data = pd.read_excel(BytesIO(content), header=None,sheet_name=None)
                return True,[df for sheet_name, df in excel_data.items()]
    except Exception as e:
                return False,str(e)