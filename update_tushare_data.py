'''
Author: your name
Date: 2022-05-03 11:05:33
LastEditTime: 2022-05-15 21:41:44
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /machine-learning/qc_widget_demo copy.py
'''
'''
Author: wondereamer
Date: 2022-03-05 21:18:04
LastEditTime: 2022-03-13 12:29:28
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /machine-learning/qc_widget_demo.py
'''
from ml.data.tushare import update_tushare_data
from ml.log import wlog as log


token = "b82e69b2dcd8b91f9624de77d3a5b194db95065bc1b3a4ef5f876d95"
data_path = '/Users/wdj/Work/Lean/Data'
update_tushare_data(token, data_path, ['sz', 'sh', 'bj'])

