'''
Author: your name
Date: 2022-03-02 08:19:47
LastEditTime: 2022-06-07 13:43:05
LastEditors: wondereamer wells7.wong@gmail.com
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /machine-learning/ml/finance/analysis.py
'''
from typing import List
from banana.dstruct.order import Deal, Direction, OrderStatus, TradeSide, Order

def orders_to_deals(orders: List[Order]):
    """ 根据交易明细计算开平仓对。 

    1. support hedge position.
    2. positions sorted by create time
    3. close 
    
    """
    transactions = filter(lambda x: x.status in [OrderStatus.Filled, OrderStatus.PartiallyFilled], orders)
    transactions = sorted(transactions, key=lambda x: x.create_time)

    positions = {}
    deals = []
    for trans in transactions:
        open_orders = positions.setdefault((trans.symbol, trans.exchange, trans.direction), [])
        if trans.side == TradeSide.Open:
            open_orders.append(trans)
            continue

        if len(open_orders) == 0:
            raise Exception("There some error in data as we can't close empty position.")

        amount_to_close = trans.quantity
        num_open_orders_to_remove = 0
        # close latest position first
        for open_order in reversed(open_orders):
            if amount_to_close == 0:
                break
            filled_quantity = 0
            if open_order.quantity <= amount_to_close:
                amount_to_close -= open_order.quantity
                filled_quantity = open_order.quantity
                num_open_orders_to_remove += 1
            else:
                open_order.quantity -= amount_to_close
                filled_quantity = amount_to_close
                amount_to_close = 0
            deals.append(Deal(open_order.direction, open_order.price, trans.price,
                open_order.create_time, trans.create_time, filled_quantity, open_order.volume_multiple))

        for i in range(0, num_open_orders_to_remove):
            open_orders.pop()

    return deals