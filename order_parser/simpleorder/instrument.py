from pydantic import BaseModel
from .order_details import OrderCategory


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
    category: OrderCategory
    symbol: str

    launchTime: str
    deliveryTime: str
    deliveryFeeRate: str
    priceScale: str
    leverageFilter: LeverageFilter
    priceFilter: PriceFilter
    lotSizeFilter: LotSizeFilter
    fundingInterval: int



