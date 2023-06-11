import copy
import uuid
import datetime
import re
import requests
import logging
from pybit.unified_trading import HTTP

from dataclasses import dataclass, field
from enum import Enum
from advparser.exceptions import ErrorPlaceOrder

logger = logging.getLogger(__name__)


# prediction_properties_patterns = {
#     'open': list(map(str.upper, ['Open', 'Открытие', 'Точка входа'])),
#     'tp': list(map(str.upper, ['Цели', 'TP', 'Тейк-профит'])),
#     'sl': list(map(str.upper, ['Стоп', 'SL', 'Стоп-лосс']))
# }


# @dataclass
# class AdviserPrediction():
#     id: str = field(init=False)
#     dt: datetime.datetime = field(init=False, default_factory=datetime.datetime.now)

#     adviser: str
#     prediction_text: str

#     side: OrderSide = field(init=False)
#     opens: list[float] = field(init=False, default_factory=list)
#     stop_losses: list[float] = field(init=False)
#     take_profits: list[float] = field(init=False)

#     complex_order: ComplexOrder = field(init=None)

#     def __post_init__(self) -> None:
#         def get_side(s: str) -> OrderSide:
#             s = s.upper()
#             if ('SHORT' in s) or ('SELL' in s):
#                 return OrderSide.SELL

#             return OrderSide.BUY

#         def get_numbers(s: str) -> list:
#             pattens_to_clear = [' 1-', ' 2-', ' 3-', ' 4-']
#             for pattern in pattens_to_clear:
#                 s = s.replace(pattern, ' ')

#             return list(map(float, re.findall(r"[-+]?\d*\.?\d+|\d+", s)))

#         def generate_id() -> str:
#             return str(uuid.uuid4())

#         self.id = generate_id()
#         self.dt = datetime.datetime

#         self.side = get_side(self.prediction_text)
#         prediction = {}
#         for s in self.prediction_text.upper().split('\n'):
#             for k, patterns_list in prediction_properties_patterns.items():
#                 if any([s.find(pattern) >= 0 for pattern in patterns_list]):
#                     prediction[k] = sorted(list(map(abs, get_numbers(s))))

#         self.opens = prediction['open']
#         self.stop_losses = prediction['sl']
#         self.take_profits = prediction['tp']

#     def create_complex_order(self, total_qty: float, stop_loss_strategy) -> ComplexOrder:
#         self.complex_order = ComplexOrder()

#         simple_order_cnt = len(self.opens) * len(self.take_profits)
#         simple_order_qty = total_qty / simple_order_cnt if simple_order_cnt > 0 else 0

#         stop_loss = max(self.stop_losses)
#         if self.side == OrderSide.BUY:
#             stop_loss = min(self.stop_losses)

#         for open_price in self.opens:
#             for take_profit in self.take_profits:
#                 order = SimpleOrder(side=self.side,
#                                     qty=simple_order_qty,
#                                     open_price=open_price,
#                                     stop_loss=stop_loss,
#                                     take_profit=take_profit)
#                 self.complex_order.orders.append(order)

#         self.complex_order.calculate()

#         return self.complex_order

#     def print(self) -> str:
#         print(f'Opens: {self.opens}\nTake profits: {self.take_profits}\nStop losses: {self.stop_losses}')

#     def get_qty_by_loss(self, max_loss: float) -> float:
#         price_delta_max = max([abs(o - sl) for o in self.opens for sl in self.stop_losses])
#         return max_loss / price_delta_max


