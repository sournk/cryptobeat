import copy
import pprint
import sys
import logging
from logging import StreamHandler, Formatter


from pybit.unified_trading import HTTP

import config
from market_utils import OrderSide, OrderCategory, OrderType, \
    MarketPosition
from advparser import AdviserPrediction

# from advparser import AdviserPrediction


def place_full_order() -> None:
    session = HTTP(
        testnet=False,
        api_key=config.API_KEY,
        api_secret=config.SECRET_KEY,
    )

    so = SimpleOrder(category=OrderCategory.LINEAR,
                     type=OrderType.MARKET,
                     symbol='PEOPLEUSDT',
                     side=OrderSide.BUY,
                     open=MarketPosition(3, 0.02),
                     stop_losses=[MarketPosition(1, 0.005), MarketPosition(1, 0.002)],
                     take_profits=[MarketPosition(3, 0.055555555555555),
                                   MarketPosition(1, 0.03),
                                   MarketPosition(1, 0.04)])

    print(so.api_update_current_price(session))
    so.api_update_instrument_info(session)
    so.fit_market_positions()    
    so.api_place_order(session)
    so.api_set_trading_stop(session)

    dist = MarketPosition(0, so.take_profits[0].price - so.current.price)
    trailing_stop = TrailingStop(active=True,
                                 distance=dist,
                                 activation_price=so.take_profits[0])
    so.api_set_trailing_stop(session=session,
                             trailing_stop=trailing_stop)
    print('Done')


def parse_advise() -> None:
    advise1 = """
    🎈 #LINK/USDT - LONG📈

    🟢 Открытие - 6.342-6.153

    ✅ Цели - 1-6.411 2-6.475  3-6.529 4-6.611

    ♾ - Плечо - х20 (Cross)

    🔴 Стоп - 5.965
    """

    advise2 = """
    SOL | USDT = LONG

    Точка входа: 19.180
    Тейк-профит: 19.422 | 19.854
    Кредитное плечо: 50x
    Стоп-лосс: 18.609

        """


    ap = AdviserPrediction(adviser='Test Adviser',
                           prediction_text=advise1)
    print(ap)


if __name__ == '__main__':
    logger = logging.getLogger('simpleorder')
    logger.setLevel(logging.DEBUG)
    handler = StreamHandler(stream=sys.stdout)
    handler.setFormatter(
        Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s'))
    logger.addHandler(handler)

    parse_advise()
