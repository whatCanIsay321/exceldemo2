from pydantic import BaseModel
class item(BaseModel):
    bill:str = "电费结算单"

    bill_description:str='''#  电费结算单说明
- 描述：电费结算单是供电局向供电公司采购电力后，所开具的财务支付凭证，作为核算、结算与财务管理的重要依据。'''

    bill_items:str='''#  电费结算单各个字段说明（共 12 个）

## 1. `start_time`
- 描述：结算开始时间，是指本张电费结算单所涉及的电费费用，对应供电局从供电公司购入电量的计费起始日期。
- 匹配关键词：`年月`、`电费年月`、`应付年月`、`购电月份`。

## 2. `end_time`
- 描述：结算结束时间，是指本张电费结算单所涉及的电费费用，对应供电局从供电公司购入电量的计费结束日期。
- 匹配关键词：`年月`、`电费年月`、`应付年月`、`购电月份`。

## 3. `total_electricity`
- 描述：总发电量。
- 匹配关键词：`总电量`、`发电量`。
- **值类型**：数字

## 4. `grid_electricity`
- 描述：总发电量中并入电网的部分电量。
- 匹配关键词：`上网电量`、`总上网电量`。
- **值类型**：数字

## 5. `payable_fee`
- 描述：支付的电费金额（包含税费）。
- 匹配关键词：`含税电费`、`应付购电款`。
- **值类型**：数字

## 6. `payable_tax`
- 描述：应支付的税额。
- 匹配关键词：`税金`、`上网电费税额`。
- **值类型**：数字

## 7. `grid_price`
- 描述：上网电价的单价，也就是一度电的价格。
- 匹配关键词：`上网电价`。
- **值类型**：数字

## 8. `power_station`
- 描述：供电单位或供电所，结算单中的购电方单位名称。
- 匹配关键词：`供电单位`、`管理单位`。
- **不能是某某公司，必须是“供电所”或类似结构**

## 9 `power_company`
- 描述：售电单位,结算单中的售电方企业名称。
- 匹配关键词：`户号`、`发电客户名称、`户名`、`项目名称`。
- **值类型**：一般叫某某公司。

## 10. `generation_account`
- 描述：发电客户或项目的编号。
- 匹配关键词：`发电客户编号`、`项目编号`、`客户编号`、`用户编号`。
- **值类型**：数字

## 11. `transaction_id`
- 描述：电网的交易对象编号。
- 匹配关键词：`电厂交易对象编号`、`交易对象编号`、`上网户号`、`并网户号`、`购电户号`、`购电号`。
- **值类型**：数字

## 12. `meter_id`
- 描述：电表资产编号。
- 匹配关键词：`电表号`。
- **值类型**：数字。'''

    common_bill_items:str=f'''# 公用字段说明（共 12 个）
你要识别的是整张表格中可能适用于所有{bill}的**公用字段值**。这些字段值通常在第一行或顶部标题中出现，而不是来自列名。


## 1. `start_time`
- 描述：结算开始时间，是指本张电费结算单所涉及的电费费用，对应供电局从供电公司购入电量的计费起始日期。
- 匹配关键词：`年月`、`电费年月`、`应付年月`、`购电月份`。

## 2. `end_time`
- 描述：结算结束时间，是指本张电费结算单所涉及的电费费用，对应供电局从供电公司购入电量的计费结束日期。
- 匹配关键词：`年月`、`电费年月`、`应付年月`、`购电月份`。

## 3. `total_electricity`
- 描述：总发电量。
- 匹配关键词：`总电量`、`发电量`。
- **值类型**：数字

## 4. `grid_electricity`
- 描述：总发电量中并入电网的部分电量。
- 匹配关键词：`上网电量`、`总上网电量`。
- **值类型**：数字

## 5. `payable_fee`
- 描述：支付的电费金额（包含税费）。
- 匹配关键词：`含税电费`、`应付购电款`。
- **值类型**：数字

## 6. `payable_tax`
- 描述：应支付的税额。
- 匹配关键词：`税金`、`上网电费税额`。
- **值类型**：数字

## 7. `grid_price`
- 描述：上网电价的单价，也就是一度电的价格。
- 匹配关键词：`上网电价`。
- **值类型**：数字

## 8. `power_station`
- 描述：供电单位或供电所，结算单中的购电方单位名称。
- 匹配关键词：`供电单位`、`管理单位`。
- **不能是某某公司，必须是“供电所”或类似结构**

## 9 `power_company`
- 描述：售电单位,结算单中的售电方企业名称。
- 匹配关键词：`户号`、`发电客户名称、`户名`、`项目名称`。
- **值类型**：一般叫某某公司。

## 10. `generation_account`
- 描述：发电客户或项目的编号。
- 匹配关键词：`发电客户编号`、`项目编号`、`客户编号`、`用户编号`。
- **值类型**：数字

## 11. `transaction_id`
- 描述：电网的交易对象编号。
- 匹配关键词：`电厂交易对象编号`、`交易对象编号`、`上网户号`、`并网户号`、`购电户号`、`购电号`。
- **值类型**：数字

## 12. `meter_id`
- 描述：电表资产编号。
- 匹配关键词：`电表号`。
- **值类型**：数字。'''


    output_get_index_system:str='''{
  "start_time": None,
  "end_time": 0,
  "total_electricity": 1,
  "grid_electricity": None,
  "payable_fee": 17,
  "payable_tax": None,
  "grid_price": 9,
  "power_station": None,
  "power_company":None,
  "generation_account": 3,
  "transaction_id": None,
  "meter_id": None
}'''

    output_get_head_common_system:str='''{
  "start_time": 202503,
  "end_time": 202504,
  "total_electricity": None,
  "grid_electricity": None,
  "payable_fee": None,
  "payable_tax": None,
  "grid_price": None,		
  "power_station": "北京供电所",
  "power_company":乙方：合肥市长兵九能源有限公司,		
  "generation_account": 3550002017241,
  "transaction_id": None,
  "meter_id": None
}'''

    output_prompt:str='''[
{
  "start_time": "202412",
  "end_time": "202412",
  "total_electricity": 3602,
  "grid_electricity": 3602,
  "payable_fee": 1416.31,
  "payable_tax": 162.94,
  "grid_price": 0.3932,
  "power_station": "鹤塘镇供电所",
  "power_company":乙方：合肥市长兵九能源有限公司,		
  "generation_account": 3550002017241,
  "transaction_id": null,
  "meter_id": null
},
{
  "start_time": "202412",
  "end_time": "202412",
  "total_electricity": 4208,
  "grid_electricity": 4208,
  "payable_fee": 1654.59,
  "payable_tax": 190.35,
  "grid_price": 0.3932,
  "power_station": "鹤塘镇供电所",
  "power_company":乙方：合肥市长兵九能源有限公司,		
  "generation_account": 3550002193797,
  "transaction_id": null,
  "meter_id": null
}
]
    
    
'''
    output_count_items_system:str='''
{
  "count":3
}
    '''

    primary_item:list=["generation_account","transaction_id"]

    render_parameters:dict={
        'get_index_system':
        {
            'bill':bill,
            'bill_description':bill_description,
            'bill_items':bill_items,
            'output': output_get_index_system
        },

        'get_head_common_system':
        {
            'bill': bill,
            'bill_description': bill_description,
            'bill_items': common_bill_items,
            'output': output_get_head_common_system

        },
        'prompt':{
            'bill': bill,
            'bill_description': bill_description,
            'bill_items': bill_items,
            'output': output_prompt
        },
        'count_items_system':{
            'bill': bill,
            'bill_description': bill_description,
            'bill_items': bill_items,
            'output': output_count_items_system
        }
    }
