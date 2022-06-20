'''
Author: your name
Date: 2022-02-19 17:15:25
LastEditTime: 2022-06-06 09:26:23
LastEditors: wondereamer wells7.wong@gmail.com
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE

FilePath: /machine-learning/ml/widgets/formater.py
'''
from matplotlib.ticker import Formatter


class TimeFormatter(Formatter):
    # 分类 －－format
    def __init__(self, dates, delta=None, fmt='%Y-%m-%d %H:%M'):
        self.dates = dates
        self.fmt = self._strtime_format(delta) if delta else fmt

    def __call__(self, x, pos=0):
        'Return the label for time x at position pos'
        ind = int(round(x))
        if ind>=len(self.dates) or ind<0: return ''
        return self.dates[ind].strftime(self.fmt)

    def _strtime_format(self, delta):
        if delta.days >= 1:
            return '%Y-%m'
        elif delta.seconds == 60:
            return '%m-%d %H:%M'
        else:
            # 日内其它分钟
            return '%m-%d'

