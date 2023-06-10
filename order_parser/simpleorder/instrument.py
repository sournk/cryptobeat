from pydantic import BaseModel


class LeverageFilter(BaseModel):
    minLeverage: float
    maxLeverage: float
    leverageStep: float


class PriceFilter(BaseModel):
    minPrice: float
    maxPrice: float
    tickSize: float


class LotSizeFilter(BaseModel):
    maxOrderQty: float
    minOrderQty: float
    qtyStep: float
    postOnlyMaxOrderQty: float


class InstrumentInfo(BaseModel):
    symbol: str

    launchTime: str
    deliveryTime: str
    deliveryFeeRate: str
    priceScale: float
    leverageFilter: LeverageFilter
    priceFilter: PriceFilter
    lotSizeFilter: LotSizeFilter
    fundingInterval: int
