import copy
import uuid
import requests
import logging
from pybit.unified_trading import HTTP

from dataclasses import dataclass, field
from functools import total_ordering
from enum import Enum


from .order_details import OrderCategory, OrderSide, OrderType
from advparser.exceptions import CantRequestSymbolTicker, ErrorPlaceOrder, ErrorSetTradingStop
from .order_details import MarketPosition

logger = logging.getLogger(__name__)


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

    stop_losses: list[MarketPosition] = field(
        default_factory=list)   # Order stop losses list
    take_profits: list[MarketPosition] = field(
        default_factory=list)  # Order take profits list

    open_losses: dict[MarketPosition, MarketPosition] = field(
        init=False, default_factory=dict)      # List of losses relative to open MarketPosition
    current_losses: dict[MarketPosition, MarketPosition] = field(
        init=False, default_factory=dict)   # List of losses relative to current MarketPosition

    open_profits: dict[MarketPosition, MarketPosition] = field(
        init=False, default_factory=dict)     # List of profits relative to open MarketPosition
    current_profits: dict[MarketPosition, MarketPosition] = field(
        init=False, default_factory=dict)  # List of profits relative to current MarketPosition

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
        # Sort stop_losses from worse to best based on order side
        self.stop_losses = sorted(self.stop_losses,
                                  reverse=self.side == OrderSide.BUY)

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

        # Sort take_profits from worse to best based on order side
        self.take_profits = sorted(self.take_profits,
                                  reverse=self.side == OrderSide.SELL)
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

        max_profit = max(
            [profit.value for profit in self.open_profits.values()]) if self.open_profits else 0
        max_loss = max(
            [loss.value for loss in self.open_losses.values()]) if self.open_losses else 0
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
        logger.info(f'Placing order via session.place_order() {self}')
        try:
            tp = self.take_profits[-1].price if self.take_profits else 0
            sl = self.stop_losses[-1].price if self.stop_losses else 0
            res = session.place_order(
                category=self.category.value,
                symbol=self.symbol,
                side=self.side.value,
                orderType=self.type.value,
                qty=self.open.qty,
                price=self.open.price,
                orderLinkId=self.id,
                takeProfit=tp,
                stopLoss=sl,
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

    def set_partial_take_profits(self, session: HTTP) -> None:
        '''
        Adds partial TP. Partial means all of them except last=best,
        which is set inside place_order()
        '''
        if self.take_profits:
            logger.info(
                f'Start setting {len(self.take_profits)} partial take profits via session.set_trading_stop() for order {self}')
            for num, take_profit in enumerate(self.take_profits[0:-1]):
                logger.info(
                    f'Setting partial take profit {num} {take_profit=}')

                try:
                    res = session.set_trading_stop(
                        category=self.category.value,
                        symbol=self.symbol,
                        takeProfit=str(take_profit.price),
                        tpTriggerBy="MarkPrice",
                        tpslMode="Partial",
                        tpOrderType="Market",
                        tpSize=str(take_profit.qty),
                        # tpLimitPrice="",
                        positionIdx=0
                    )
                    if res['retCode'] != 0:
                        logger.error(f'Set partial take profit error {res}')
                        raise ErrorSetTradingStop(res)
                    else:
                        logger.info(f'Partial take profit successfully set {res}')

                except Exception as e:
                    logger.exception(f'Error setting partial take profit {e}')
                    raise ErrorSetTradingStop

    def set_partial_stop_losses(self, session: HTTP) -> None:
        '''
        Adds partial SL. Partial means all of them except last=best,
        which is set inside place_order()
        '''
        if self.stop_losses:
            logger.info(
                f'Start setting {len(self.stop_losses)} partial stop losses via session.set_trading_stop() for order {self}')
            for num, stop_loss in enumerate(self.stop_losses[0:-1]):
                logger.info(
                    f'Setting partial stop loss {num} {stop_loss=}')

                try:
                    res = session.set_trading_stop(
                        category=self.category.value,
                        symbol=self.symbol,
                        stopLoss=str(stop_loss.price),
                        slTriggerBy="MarkPrice",
                        tpslMode="Partial",
                        slOrderType="Market",
                        slSize=str(stop_loss.qty),
                        # tpLimitPrice="",
                        positionIdx=0
                    )
                    if res['retCode'] != 0:
                        logger.error(f'Set partial stop loss error {res}')
                        raise ErrorSetTradingStop(res)
                    else:
                        logger.info(
                            f'Partial stop loss successfully set {res}')

                except Exception as e:
                    logger.exception(f'Error setting partial stop loss {e}')
                    raise ErrorSetTradingStop

    def set_trading_stop(self, session: HTTP) -> None:
        '''
        Adds partial SL and TP. Partial means all of them except last=best,
        which is set inside place_order()
        '''
        # self.set_partial_stop_losses(session)
        self.set_partial_take_profits(session)

    def set_trailing_stop(self, session: HTTP, 
                          trailing_stop_price_distance: float,
                          activation_price: float) -> None:
        '''
        Add trailing stop to position
        '''
        '''
        Adds partial TP. Partial means all of them except last=best,
        which is set inside place_order()
        '''
        if self.take_profits:
            logger.info(
                f'Start setting trailing stop via session.set_trading_stop() for order {self}')

            try:
                res = session.set_trading_stop(
                    category=self.category.value,
                    symbol=self.symbol,
                    trailingStop=str(trailing_stop_price_distance),
                    activePrice=str(activation_price),
                    positionIdx=0
                )
                if res['retCode'] != 0:
                    logger.error(f'Set trailing stop error {res}')
                    raise ErrorSetTradingStop(res)
                else:
                    logger.info(
                        f'Trailing stop successfully set {res}')

            except Exception as e:
                logger.exception(f'Error setting trailing stop {e}')
                raise ErrorSetTradingStop
