from enum import Enum
from functools import total_ordering


import crypto_math as crypto_math
from crypto_math import ED
from .instrument import InstrumentInfo


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
    def qty(self) -> ED:
        return self.__qty

    @qty.setter
    def qty(self, val: ED) -> None:
        self.__qty = ED(val)
        self.value = self.__qty * self.__price

    @property
    def price(self) -> ED:
        return self.__price

    @price.setter
    def price(self, val: ED) -> None:
        self.__price = ED(val)
        self.value = self.__qty * self.__price

    @property
    def value(self) -> ED:
        return self.__value

    @value.setter
    def value(self, val: ED) -> None:
        self.__value = ED(val)

    def __init__(self, qty: ED, price: ED) -> None:
        self.__qty, self.__price, self.__value = ED(
            0), ED(0), ED(0)
        self.qty = qty
        self.price = price

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.qty=}, '\
            f'{self.price=}, {self.value=})'

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

    def fit_price(self, instrument_info: InstrumentInfo) -> ED:
        self.price = crypto_math.fit_to_chunk(
                        val=self.price,
                        tick_size=instrument_info.priceFilter.tickSize,
                        min_value=instrument_info.priceFilter.minPrice,
                        max_value=instrument_info.priceFilter.maxPrice)
        return self.price

    def fit_qty(self, instrument_info: InstrumentInfo) -> ED:
        self.qty = crypto_math.fit_to_chunk(
            val=self.qty,
            tick_size=instrument_info.lotSizeFilter.qtyStep,
            min_value=instrument_info.lotSizeFilter.minOrderQty,
            max_value=instrument_info.lotSizeFilter.maxOrderQty)
        return self.qty

    def fit(self, instrument_info: InstrumentInfo) -> None:
        self.fit_price(instrument_info)
        self.fit_qty(instrument_info)
