'''
Author: your name
Date: 2022-03-02 09:26:09
LastEditTime: 2022-03-05 21:15:45
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /machine-learning/ml/finance/datastruct.py
'''

from json.tool import main
from pprint import pformat
from enum import Enum

class PrintMixin(object):
    
    def __str__(self):
        attrs = vars(self)
        return pformat(dict(filter(lambda x: not x[0].startswith('__'), attrs.items())))

    def __repr__(self):
        return self.__str__()


class TradeSide(Enum):
    Open = 1
    Close = 2


class OrderType(Enum):
    """ 下单类型
    """
    Market = 0
    Limit = 1


class Direction(Enum):
    """
    多空方向。
    """
    Long = 0
    Short = 1


class OrderStatus(Enum):
    Submitted = 1
    Canceled = 5
    PartiallyFilled = 2
    Filled = 3
    Invalid = 7


class Deal(PrintMixin):
    """ 每笔交易(一开, 一平)

    :ivar open_datetime: 开仓时间
    :ivar close_datetime: 平仓时间
    :ivar open_price: 开仓价格
    :ivar close_price: 平仓价格
    :ivar direction: 开仓方向
    """
    def __init__(self, direction, open_price, close_price, open_time, close_time, quantity, volume_multiple):
        self.direction = direction
        self.open_price = open_price
        self.close_price = close_price
        self.open_time = open_time
        self.close_time = close_time
        self.quantity = quantity
        self.volume_multiple = volume_multiple

    @property
    def profit(self):
        """ 盈亏额  """
        if self.direction == Direction.Long:
            return (self.close_price - self.open_price) * self.quantity * self.volume_multiple
        return (self.open_price - self.close_price) * self.quantity * self.volume_multiple

    def __eq__(self, r):
        return self.__str__() == str(r)


class Order(PrintMixin):
    """ 订单
    """
    def __init__(self, id, create_time, symbol, exchange, order_type, side, direction,
                 price, quantity, status, volume_multiple):
        self.id = id
        self.create_time = create_time
        self.symbol = symbol
        self.exchange = exchange
        self.type = order_type
        self.side = side
        self.direction = direction
        self.price = price
        self.quantity = quantity
        self.status = status
        self.volume_multiple = volume_multiple

    def __hash__(self):
        try:
            return self._hash
        except AttributeError:
            self._hash = hash(self.id)
            return self._hash

    def __eq__(self, r):
        return self._hash == r._hash



if __name__ == "__main__":
    d = Deal(Direction.Long, 12, 10, "t3", "t4", 1, 1)
    print(d)
