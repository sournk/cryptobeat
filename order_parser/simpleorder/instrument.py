from pydantic import BaseModel, validator

from simpleorder.crypto_math import ED


class LeverageFilter(BaseModel):
    minLeverage: ED
    maxLeverage: ED
    leverageStep: ED

    @validator('*')
    def cast_to_ED_type(cls, v):
        return ED(v)

    class Config():
        validate_assignment = True


class PriceFilter(BaseModel):
    minPrice: ED
    maxPrice: ED
    tickSize: ED

    @validator('*')
    def cast_to_ED_type(cls, v):
        print(v)
        return ED(v)

    class Config():
        validate_assignment = True


class LotSizeFilter(BaseModel):
    maxOrderQty: ED
    minOrderQty: ED
    qtyStep: ED
    postOnlyMaxOrderQty: ED

    @validator('*')
    def cast_to_ED_type(cls, v):
        return ED(v)

    class Config():
        validate_assignment = True


class InstrumentInfo(BaseModel):
    symbol: str

    launchTime: str
    deliveryTime: str
    deliveryFeeRate: str
    priceScale: ED
    leverageFilter: LeverageFilter
    priceFilter: PriceFilter
    lotSizeFilter: LotSizeFilter
    fundingInterval: int

    @validator('priceScale')
    def cast_to_ED_type(cls, v):
        return ED(v)
