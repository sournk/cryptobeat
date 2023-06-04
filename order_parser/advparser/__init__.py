import copy
import uuid
import datetime
import re
import requests
import logging
from pybit.unified_trading import HTTP

from dataclasses import dataclass, field
from enum import Enum
from advparser.exceptions import CantRequestSymbolTicker, ErrorPlaceOrder

logger = logging.getLogger(__name__)


class OrderSide(Enum):
    '''
    Sides of Order
    '''
    BUY = 'Buy'
    SELL = 'Sell'


class OrderCategory(Enum):
    '''
    Categories of Order
    '''
    SPOT = 'spot'
    LINEAR = 'linear'
    INVERSE = 'inverse'
    OPTION = 'option'


class OrderType(Enum):
    '''
    Types of Order
    '''
    MARKET = 'Market'
    LIMIT = 'Limit'


class MarketPosition():
    '''
    Class defines market position at one time with qty, price and value.
    It's possible to + or - two class instances.
    '''
    @property
    def qty(self) -> float:
        return self.__qty

    @qty.setter
    def qty(self, val) -> None:
        self.__qty = val
        self.value = self.__qty * self.__price

    @property
    def price(self) -> float:
        return self.__price

    @price.setter
    def price(self, val) -> None:
        self.__price = val
        self.value = self.__qty * self.__price

    @property
    def value(self) -> float:
        return self.__value

    @value.setter
    def value(self, val) -> None:
        self.__value = val

    def __init__(self, qty: float, price: float) -> None:
        self.__qty, self.__price, self.__value = 0, 0, 0 
        self.qty = qty
        self.price = price

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.qty=}, {self.price=}, {self.value=})'

    def __add__(self, other):
        new_price = (self.value + other.value) / (self.qty + other.qty)\
            if self.qty + other.qty != 0 else 0
        res = MarketPosition(self.qty + other.qty, new_price)
        res.value = self.value + other.value
        return res

    def __sub__(self, other):
        new_price = (self.value - other.value) / (self.qty - other.qty)\
            if self.qty - other.qty != 0 else 0
        res = MarketPosition(self.qty - other.qty, new_price)
        res.value = self.value - other.value
        return res

@dataclass
class SimpleOrder():
    '''Class of Market Order'''

    id: str = field(init=False)
    external_id: str = field(init=False, default='')

    category: OrderCategory
    symbol: str
    side: OrderSide
    type: OrderType

    open: MarketPosition = field()               # Open MarketPosition
    current: MarketPosition = field(init=False)  # Current MarketPosition

    stop_losses: list[MarketPosition] = field(default_factory=list)   # Order stop losses list 
    take_profits: list[MarketPosition] = field(default_factory=list)  # Order take profits list

    open_losses: dict[MarketPosition, MarketPosition] = field(init=False, default_factory=dict)      # List of losses relative to open MarketPosition
    current_losses: dict[MarketPosition, MarketPosition] = field(init=False, default_factory=dict)   # List of losses relative to current MarketPosition

    open_profits: dict[MarketPosition, MarketPosition] = field(init=False, default_factory=dict)     # List of profits relative to open MarketPosition
    current_profits: dict[MarketPosition, MarketPosition] = field(init=False, default_factory=dict)  # List of profits relative to current MarketPosition

    risk_rate: float = field(init=False, default=0)  # Risk rate against open

    def __post_init__(self) -> None:
        self.id = self.generate_id()
        self.current = copy.copy(self.open)

    def generate_id(self) -> str:
        '''Generated ID as uuid64'''
        return str(uuid.uuid4())

    def update(self) -> None:
        """
            Updates open and current losses and profits
        """
        self.open_losses.clear()
        self.current_losses.clear()
        for stop_loss in self.stop_losses:
            if self.side == OrderSide.BUY:
                self.open_losses[stop_loss] = self.open - stop_loss
                self.open_losses[stop_loss].roi = self.open_losses[stop_loss].value / \
                    self.open.value if self.open.value != 0 else 0

                self.current_losses[stop_loss] = self.current - stop_loss
                self.current_losses[stop_loss].roi = self.current_losses[stop_loss].value / \
                    self.open.value if self.open.value != 0 else 0
            else:
                self.open_losses[stop_loss] = stop_loss - self.open
                self.open_losses[stop_loss].roi = self.open_losses[stop_loss].value / \
                    self.open.value if self.open.value != 0 else 0

                self.current_losses[stop_loss] = stop_loss - self.current
                self.current_losses[stop_loss].roi = self.current_losses[stop_loss].value / \
                    self.open.value if self.open.value != 0 else 0

        self.open_profits.clear()
        self.current_profits.clear()
        for take_profit in self.take_profits:
            if self.side == OrderSide.BUY:
                self.open_profits[take_profit] = take_profit - self.open
                self.open_profits[take_profit].roi = self.open_profits[take_profit].value / \
                    self.open.value if self.open.value != 0 else 0

                self.current_profits[take_profit] = take_profit - self.current
                self.current_profits[take_profit].roi = self.current_profits[take_profit].value / \
                    self.open.value if self.open.value != 0 else 0
            else:
                self.open_profits[take_profit] = self.open - take_profit
                self.open_profits[take_profit].roi = self.open_profits[take_profit].value / \
                    self.open.value if self.open.value != 0 else 0

                self.current_profits[take_profit] = self.current - take_profit
                self.current_profits[take_profit].roi = self.current_profits[take_profit].value / \
                    self.open.value if self.open.value != 0 else 0

        max_profit = max([profit.value for profit in self.open_profits.values()])
        max_loss = max([loss.value for loss in self.open_losses.values()])
        self.risk_rate = max_profit / max_loss if max_loss != 0 else 0

    def update_current_price_from_exchange(self) -> float:
        '''Updates current price from exchange'''

        url = "https://api-testnet.bybit.com/derivatives/v3/public/tickers"

        payload = {}
        headers = {}

        logger.info(
            f"Requesting exchange tickers requests.request('GET', url={url}) ")
        try:
            response = requests.request(
                "GET", url, headers=headers, data=payload).json()
        except Exception:
            logger.exception(
                f"Error of requests.request('GET', url={url}) exchange tickers")
            raise CantRequestSymbolTicker

        try:
            data = list(filter(lambda d: d['symbol'].find(
                self.symbol) == 0, response['result']['list']))[0]
            self.current.price = float(data['lastPrice'])
            logger.info(f'{self.current=} updated')
        except Exception:
            logger.exception(
                f"Error price update. Not found {self.symbol=} in exchange tickers list")
            raise CantRequestSymbolTicker

        self.update()
        return self.current

    def place_order(self, session: HTTP) -> None:
        '''
        Places order by open price
        '''
        logger.info(f'Placing order {self} via session.place_order')
        try:
            res = session.place_order(
                category=self.category.value,
                symbol=self.symbol,
                side=self.side.value,
                orderType=self.type.value,
                qty=self.open.qty,
                price=self.open.price,
                orderLinkId=self.id,
            )
            if res['retCode'] == 0:
                self.external_id = res['result']['orderId']
                logger.info(f'Order successfully placed {res}')
            else:
                logger.error(f'Place order error {res}')
                raise ErrorPlaceOrder(res)

        except Exception as e:
            logger.exception(f'Error placing order {e}')
            raise ErrorPlaceOrder



# @dataclass
# class ComplexOrder():
#     id: str = field(init=False)
#     orders: list[SimpleOrder] = field(init=False, default_factory=list)
#     side: OrderSide = field(init=False)
#     qty: float = field(init=False)
#     value: float = field(init=False)

#     loss: float = field(init=False)
#     profit: float = field(init=False)

#     risk_profit_rate: float = field(init=False)

#     current_profit_loss: float = field(init=False, default=0)
#     current_roi: float = field(init=False, default=0)

#     def generate_id(self) -> str:
#         return str(uuid.uuid4())

#     def __post_init__(self) -> None:
#         self.id = self.generate_id()

#     def calculate(self) -> None:
#         self.side = self.orders[0].side

#         self.qty = sum([o.qty for o in self.orders])
#         self.value = sum([o.value for o in self.orders])
#         self.loss = sum([o.loss for o in self.orders])
#         self.profit = sum([o.profit for o in self.orders])

#         self.risk_profit_rate = self.profit / self.loss if self.loss != 0 else 0

#         self.current_profit_loss = sum([o.current_profit_loss for o in self.orders])
#         self.current_roi = self.current_profit_loss / self.value if self.value != 0 else 0

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


