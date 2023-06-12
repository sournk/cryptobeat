import uuid
import datetime
import re
import logging

from dataclasses import dataclass, field

from .exceptions import AdviserPredictionOrderSideParseError, \
    AdviserPredictionOpenPriceParseError, AdviserPredictionStopLossParseError,\
    AdviserPredictionTakeProfitParseError
from crypto_math import ED
from market_utils import OrderSide

logger = logging.getLogger(__name__)


prediction_properties_patterns = {
    'buy_side': list(map(str.upper, ['Buy', 'Long'])),
    'sell_side': list(map(str.upper, ['Sell', 'Short'])),
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
    opens: list[ED] = field(init=False, default_factory=list)
    stop_losses: list[ED] = field(init=False, default_factory=list)
    take_profits: list[ED] = field(init=False, default_factory=list)

    def generate_id(self) -> str:
        '''Generated ID as uuid64'''
        return str(uuid.uuid4())

    def __post_init__(self) -> None:
        def get_numbers(s: str) -> list:
            pattens_to_clear = [' 1-', ' 2-', ' 3-', ' 4-']
            for pattern in pattens_to_clear:
                s = s.replace(pattern, ' ')

            return list(map(ED, re.findall(r"[-+]?\d*\.?\d+|\d+", s)))

        self.id = self.generate_id()
        self.dt = datetime.datetime

        prediction = {}
        for s in self.prediction_text.upper().split('\n'):
            for k, patterns_list in prediction_properties_patterns.items():
                if any([s.find(pattern) >= 0 for pattern in patterns_list]):
                    prediction[k] = sorted(list(map(abs, get_numbers(s))))

        if 'buy_side' in prediction:
            self.side = OrderSide.BUY
        elif 'sell_side' in prediction:
            self.side = OrderSide.BUY
        else:
            raise AdviserPredictionOrderSideParseError(
                f'No side pattern found in {self.prediction_text=}')

        if 'open' in prediction:
            self.opens = prediction['open']
        else:
            raise AdviserPredictionOpenPriceParseError(
                f'No open price pattern found in {self.prediction_text=}')

        if 'sl' in prediction:
            self.stop_losses = prediction['sl']
        else:
            raise AdviserPredictionStopLossParseError(
                f'No stop loss pattern found in {self.prediction_text=}')

        if 'tp' in prediction:
            self.take_profits = prediction['tp']
        else:
            raise AdviserPredictionTakeProfitParseError(
                f'No take profit pattern found in {self.prediction_text=}')

    # def get_qty_by_loss(self, max_loss: ED) -> ED:
    #     price_delta_max = max([abs(o - sl) for o in self.opens for sl in self.stop_losses])
    #     return max_loss / price_delta_max
