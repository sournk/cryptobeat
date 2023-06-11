class AdviserPredictionParseError(Exception):
    pass


class AdviserPredictionOrderSideParseError(AdviserPredictionParseError):
    pass


class AdviserPredictionOpenPriceParseError(AdviserPredictionParseError):
    pass


class AdviserPredictionStopLossParseError(AdviserPredictionParseError):
    pass


class AdviserPredictionTakeProfitParseError(AdviserPredictionParseError):
    pass
