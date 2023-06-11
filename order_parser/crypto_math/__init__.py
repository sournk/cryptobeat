import decimal


class ED(decimal.Decimal):
    def __new__(cls, value="0", context=None):
        value = str(value)
        return super().__new__(cls, value, context)


def roundtick(x: ED, ticksize: ED):
    return ED(x / ticksize).quantize(
        ED('1'), rounding=decimal.ROUND_HALF_UP) * ticksize


def fit_to_chunk(val: ED, tick_size: ED,
                 min_value: ED, max_value: ED) -> ED:
    res = roundtick(val, tick_size)
    res = max(res, min_value)
    res = min(res, max_value)
    return res


def count_decimals(n):
    return ED(str(n)).as_tuple().exponent
