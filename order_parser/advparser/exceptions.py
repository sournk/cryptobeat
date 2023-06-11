class WrongMarketPosition(Exception):
    pass


class WrongSimpleOrder(Exception):
    pass


class WrongQty(WrongSimpleOrder):
    pass


class WrongOpenPrice(WrongSimpleOrder):
    pass


class WrongTakeProfitPrice(WrongSimpleOrder):
    pass


class WrongStopLossPrice(WrongSimpleOrder):
    pass


class ErrorPlaceOrder(Exception):
    pass


class ErrorSetTradingStop(Exception):
    pass


class ErrorGetInstrumentInfo(Exception):
    pass


class ErrorUpdateCurrentPrice(Exception):
    pass
