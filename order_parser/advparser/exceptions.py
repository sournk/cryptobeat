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