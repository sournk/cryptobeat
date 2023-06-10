import pprint
import sys
import logging
from logging import StreamHandler, Formatter

import config
from simpleorder import OrderSide, OrderCategory, OrderType, SimpleOrder, MarketPosition, logger
# , ComplexOrder, AdviserPrediction

from pybit.unified_trading import HTTP


def main() -> None:
    input = """
    🎈 #LINK/USDT - LONG📈

    🟢 Открытие - 6.342-6.153

    ✅ Цели - 1-6.411 2-6.475  3-6.529 4-6.611

    ♾ - Плечо - х20 (Cross)

    🔴 Стоп - 5.965
    """

    # input = """
    # SOL | USDT = LONG

    # Точка входа: 19.180
    # Тейк-профит: 19.422 | 19.854
    # Кредитное плечо: 50x
    # Стоп-лосс: 18.609

    #     """

    # co = ComplexOrder()
    # co.orders = [SimpleOrder(side=OrderSide.BUY, qty=1, open_price=10, stop_loss=0, take_profit=15), 
    #              SimpleOrder(side=OrderSide.BUY, qty=2, open_price=11, stop_loss=0, take_profit=18)]

    # co.orders.append(SimpleOrder(side=OrderSide.BUY, qty=3,
    #                             open_price=12, stop_loss=0, take_profit=22))
    
    # co.calculate()
    # print(co)

    # ap = AdviserPrediction('Me', input)
    # co = ap.create_complex_order(ap.get_qty_by_loss(10), 'DynamicSL')

    # for so in co.orders:
    #     so.current_price = so.open_price * 1.05

    # pprint.pprint(co.orders)

    logger.setLevel(logging.DEBUG)
    handler = StreamHandler(stream=sys.stdout)
    handler.setFormatter(
        Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s'))
    logger.addHandler(handler)

    # try:
    #     so = SimpleOrder(caterory='linear',
    #                  symbol='BTCUSDT',
    #                  side='BUY',
    #                  qty=1.0,
    #                  open_price=27000.0,
    #                  stop_loss=26500.0,
    #                  take_profit=27500.0)
        
    #     so.qty = 2
    #     so.update()
    #     print(so)
    #     so.update_current_price_from_exchange()
    #     print(so)
    # except:
    #     pass

    so = SimpleOrder(category=OrderCategory.LINEAR,
                     type=OrderType.MARKET,
                    #  symbol='PEOPLEUSDT',
                     symbol='BTCUSDT',
                     side=OrderSide.BUY,
                     open=MarketPosition(3, 0.01),
                     stop_losses=[MarketPosition(1, 0.005), MarketPosition(1, 0.002)],
                     take_profits=[MarketPosition(3, 0.055555555555555), 
                                   MarketPosition(1, 0.03),
                                   MarketPosition(1, 0.04)])

    # so.update_current_price_from_exchange()


    session = HTTP(
        testnet=False,
        api_key=config.API_KEY,
        api_secret=config.SECRET_KEY,
    )

    so.update_instrument_info_from_exchange(session)
    print(so.instrument_info)
    # print(so)

    # try:
    #     so.place_order(session)
    # except:
    #     pass

    # try:
    #     so.set_trading_stop(session)
    # except:
    #     pass

    # try:
    #     so.set_trailing_stop(session, 
    #                         trailing_stop_price_distance=so.take_profits[0].price-so.open.price,
    #                         activation_price=so.take_profits[0].price)
    # except:
    #     pass

    # print(so)
    # print(f'{so.open_losses[so.stop_losses[0]].roi=}')
    # print(f'{so.open_losses[so.stop_losses[0]].value=}')
    # print(f'{so.open_profits[so.take_profits[0]].roi=}')
    # print(f'{so.open_profits[so.take_profits[0]].value=}')
    # print(f'{so.risk_rate}')

    # print('Done')

    # print(session.get_orderbook(category="linear", symbol="PEOPLEUSDT"))

    # print(session.place_order(
    #     category="linear",
    #     symbol="PEOPLEUSDT",
    #     side="Buy",
    #     orderType="Market",
    #     qty=1,
    #     price=0.01,
    # ))

    print('Done')





if __name__ == '__main__':
    main()
