import uuid
import datetime
import re

from dataclasses import dataclass, field
from enum import Enum
from advparser.exceptions import WrongQty, WrongOpenPrice, WrongStopLossPrice, WrongTakeProfitPrice


class OrderSide(Enum):
    BUY = 'Buy'
    SELL = 'Sell'


@dataclass
class SimpleOrder():
    id: str = field(init=False)
    side: OrderSide
    qty: float
    open_price: float
    value: float = field(init=False)

    stop_loss: float
    loss: float = field(init=False)
    loss_roi: float = field(init=False)

    take_profit: float
    profit: float = field(init=False)
    profit_roi: float = field(init=False)

    risk_profit_rate: float = field(init=False)

    def generate_id(self) -> str:
        return str(uuid.uuid4())

    def __post_init__(self) -> None:
        def check_order_price_bounds():
            if self.open_price <= 0:
                raise WrongOpenPrice(f'{self.open_price=} must be >0')

            if self.stop_loss < 0:
                raise WrongStopLossPrice(
                    f'{self.stop_loss=} must be >0')
            if self.stop_loss != 0:
                if (self.side == OrderSide.BUY) and (self.stop_loss > self.open_price):
                    raise WrongStopLossPrice(
                        f'{self.stop_loss=} must be <= {self.open_price=} for {self.side=}')
                elif (self.side == OrderSide.SELL) and (self.stop_loss < self.open_price):
                    raise WrongStopLossPrice(
                        f'{self.stop_loss=} must be >= {self.open_price=} for {self.side=}')

            if self.take_profit < 0:
                raise WrongTakeProfitPrice(
                    f'{self.take_profit=} must be positive')
            if self.take_profit != 0:
                if (self.side == OrderSide.BUY) and (self.take_profit < self.open_price):
                    raise WrongTakeProfitPrice(
                        f'{self.take_profit=} must be >= {self.open_price=} for {self.side=}')
                elif (self.side == OrderSide.SELL) and (self.take_profit > self.open_price):
                    raise WrongTakeProfitPrice(
                        f'{self.take_profit=} must be <= {self.open_price=} for {self.side=}')
        
        self.id = self.generate_id()

        # Check Qty
        if self.qty <= 0:
            raise WrongQty(f'{self.qty=} must be >0')

        # Check prices
        check_order_price_bounds()

        # Calc Order params
        self.value = self.qty * self.open_price

        self.loss = self.qty * abs(self.open_price - self.stop_loss) \
            if self.stop_loss != 0 else 0
        self.profit = self.qty * abs(self.open_price - self.take_profit) \
            if self.take_profit !=0 else 0

        self.loss_roi, self.profit_roi = 0, 0
        if self.value != 0:
            self.loss_roi = self.loss / self.value
            self.profit_roi = self.profit / self.value

        self.risk_profit_rate = self.profit / self.loss if self.loss != 0 else 0

@dataclass
class ComplexOrder():
    id: str = field(init=False)
    orders: list[SimpleOrder] = field(init=False, default_factory=list)
    side: OrderSide = field(init=False)
    qty: float = field(init=False)
    value: float = field(init=False)

    loss: float = field(init=False)
    profit: float = field(init=False)

    risk_profit_rate: float = field(init=False)

    def generate_id(self) -> str:
        return str(uuid.uuid4())

    def __post_init__(self) -> None:
        self.id = self.generate_id()

    def calculate(self) -> None:
        self.side = self.orders[0].side

        self.qty = sum([o.qty for o in self.orders])
        self.value = sum([o.value for o in self.orders])
        self.loss = sum([o.loss for o in self.orders])
        self.profit = sum([o.profit for o in self.orders])

        self.risk_profit_rate = self.profit / self.loss if self.loss != 0 else 0


prediction_properties_patterns = {
    'open': list(map(str.upper, ['Open', 'Открытие', 'Точка входа'])),
    'tp': list(map(str.upper, ['Цели', 'TP', 'Тейк-профит'])),
    'sl': list(map(str.upper, ['Стоп', 'SL', 'Стоп-лосс']))
}


@dataclass
class AdviserPrediction():
    id: str = field(init=False)
    dt: datetime.datetime = field(init=False, default_factory=datetime.datetime.now)

    adviser: str
    prediction_text: str

    side: OrderSide = field(init=False)
    opens: list[float] = field(init=False, default_factory=list)
    stop_losses: list[float] = field(init=False)
    take_profits: list[float] = field(init=False)

    complex_order: ComplexOrder = field(init=None)

    def __post_init__(self) -> None:
        def get_side(s: str) -> OrderSide:
            s = s.upper()
            if ('SHORT' in s) or ('SELL' in s):
                return OrderSide.SELL

            return OrderSide.BUY

        def get_numbers(s: str) -> list:
            pattens_to_clear = [' 1-', ' 2-', ' 3-', ' 4-']
            for pattern in pattens_to_clear:
                s = s.replace(pattern, ' ')

            return list(map(float, re.findall(r"[-+]?\d*\.?\d+|\d+", s)))

        def generate_id() -> str:
            return str(uuid.uuid4())

        self.id = generate_id()
        self.dt = datetime.datetime

        self.side = get_side(self.prediction_text)
        prediction = {}
        for s in self.prediction_text.upper().split('\n'):
            for k, patterns_list in prediction_properties_patterns.items():
                if any([s.find(pattern) >= 0 for pattern in patterns_list]):
                    prediction[k] = sorted(list(map(abs, get_numbers(s))))

        self.opens = prediction['open']
        self.stop_losses = prediction['sl']
        self.take_profits = prediction['tp']

    def create_complex_order(self, total_qty: float, stop_loss_strategy) -> ComplexOrder:
        self.complex_order = ComplexOrder()

        simple_order_cnt = len(self.opens) * len(self.take_profits)
        simple_order_qty = total_qty / simple_order_cnt if simple_order_cnt > 0 else 0

        stop_loss = max(self.stop_losses)
        if self.side == OrderSide.BUY:
            stop_loss = min(self.stop_losses)

        for o in self.opens:
            for tp in self.take_profits:
                open_price = o
                if stop_loss_strategy == 'Basic':
                    pass
                elif stop_loss_strategy == 'BE':
                    if len(self.complex_order.orders) > 0:
                        open_price = self.complex_order.orders[-1].take_profit
                        stop_loss = self.complex_order.orders[-1].open_price
                elif stop_loss_strategy == "DynamicSL":
                    if len(self.complex_order.orders) > 0:
                        open_price = self.complex_order.orders[-1].take_profit
                        stop_loss = open_price - (self.complex_order.orders[0].open_price - \
                            self.complex_order.orders[0].stop_loss)

                order = SimpleOrder(side=self.side,
                                    qty=simple_order_qty,
                                    open_price=open_price,
                                    stop_loss=stop_loss,
                                    take_profit=tp)
                self.complex_order.orders.append(order)
        self.complex_order.calculate()

        return self.complex_order

    def print(self) -> str:
        print(f'Opens: {self.opens}\nTake profits: {self.take_profits}\nStop losses: {self.stop_losses}')

    def get_qty_by_loss(self, max_loss: float) -> float:
        price_delta_max = max([abs(o - sl) for o in self.opens for sl in self.stop_losses])
        return max_loss / price_delta_max