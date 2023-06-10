from enum import Enum
from functools import total_ordering


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


@total_ordering
class MarketPosition():
    '''
    1. Class defines market position at one time with qty, price and value.
    2. It's possible to + or - two class instances.
    3. Class is sortable (by @total_ordering) by price.
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

    def __lt__(self, other) -> bool:
        return self.price < other.price
