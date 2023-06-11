import unittest

from simpleorder.order_details import ED, MarketPosition
from simpleorder.instrument import InstrumentInfo


class MarketPositionTests(unittest.TestCase):

    def setUp(self):
        self.position1 = MarketPosition(10, 100)
        self.position2 = MarketPosition(5, 150)

        instrument_info_people_mock = '''
                    {
                        "symbol": "PEOPLEUSDT",
                        "contractType": "LinearPerpetual",
                        "status": "Trading",
                        "baseCoin": "PEOPLE",
                        "quoteCoin": "USDT",
                        "launchTime": "1640749024000",
                        "deliveryTime": "0",
                        "deliveryFeeRate": "",
                        "priceScale": "5",
                        "leverageFilter": {
                            "minLeverage": "1",
                            "maxLeverage": "12.50",
                            "leverageStep": "0.01"
                        },
                        "priceFilter": {
                            "minPrice": "0.00005",
                            "maxPrice": "99.99990",
                            "tickSize": "0.00005"
                        },
                        "lotSizeFilter": {
                            "maxOrderQty": "460000",
                            "minOrderQty": "1",
                            "qtyStep": "1",
                            "postOnlyMaxOrderQty": "4600000"
                        },
                        "unifiedMarginTrade": "True",
                        "fundingInterval": 480,
                        "settleCoin": "USDT"
                    }
                '''
        self.instrument_info_people = InstrumentInfo.parse_raw(
            instrument_info_people_mock)

        self.instrument_info_people.priceFilter.tickSize = ED(0.1)

    def test_initial_values(self):
        self.assertEqual(self.position1.qty, ED(10))
        self.assertEqual(self.position1.price, ED(100))
        self.assertEqual(self.position1.value, ED(1000))

    def test_addition(self):
        result = self.position1 + self.position2
        self.assertEqual(result.qty, ED(15))
        self.assertLess(abs(result.price-ED(116.67)), ED(0.01))
        self.assertEqual(result.value, ED(1750))

    def test_subtraction(self):
        result = self.position1 - self.position2
        self.assertEqual(result.qty, ED(5))
        self.assertEqual(result.price, ED(50))
        self.assertEqual(result.value, ED(250))

    def test_comparison(self):
        self.assertTrue(self.position1 < self.position2)

    def test_qty_setter(self):
        self.position1.qty = ED(15)
        self.assertEqual(self.position1.qty, ED(15))
        self.assertEqual(self.position1.value, ED(1500))

    def test_price_setter(self):
        self.position1.price = ED(200)
        self.assertEqual(self.position1.price, ED(200))
        self.assertEqual(self.position1.value, ED(2000))

    def test_compare_positions_by_price_using_lt(self):
        self.assertLess(self.position1, self.position2)

    def test_fit_decimal_price(self):
        mp = MarketPosition(price=12.7,
                            qty=100)
        self.assertEqual(mp.value, ED(12.7)*100)
        self.instrument_info_people.priceFilter.tickSize = ED(0.33)
        mp.fit_price(instrument_info=self.instrument_info_people)
        self.assertEqual(mp.price, ED(12.54))
        self.assertEqual(mp.value, ED(12.54*100))

    def test_fit_int_tick(self):
        mp = MarketPosition(price=12.7,
                            qty=100)
        self.assertEqual(mp.value, ED(12.7*100))
        self.instrument_info_people.priceFilter.tickSize = ED(1)
        mp.fit_price(instrument_info=self.instrument_info_people)
        self.assertEqual(mp.price, ED(13))
        self.assertEqual(mp.value, ED(13*100))

    def test_fit_decimal_qtyStep(self):
        mp = MarketPosition(price=12.7,
                            qty=100.3)
        self.assertEqual(mp.value, ED(12.7*100.3))
        self.instrument_info_people.lotSizeFilter.qtyStep = ED(0.2)
        mp.fit_qty(instrument_info=self.instrument_info_people)
        self.assertEqual(mp.qty, ED(100.4))
        self.assertEqual(mp.value, ED(12.7*100.4))

    def test_fit_int_qtyStep(self):
        mp = MarketPosition(price=12.7,
                            qty=101.3)
        self.assertEqual(mp.value, ED(12.7*101.3))
        self.instrument_info_people.lotSizeFilter.qtyStep = ED(2)
        mp.fit_qty(instrument_info=self.instrument_info_people)
        self.assertEqual(mp.qty, ED(102))
        self.assertEqual(mp.value, ED(12.7)*102)


class InstrumentInfoTests(unittest.TestCase):

    def test_mocked_API_update(self):
        res_mock = '''
                    {
                        "symbol": "PEOPLEUSDT",
                        "contractType": "LinearPerpetual",
                        "status": "Trading",
                        "baseCoin": "PEOPLE",
                        "quoteCoin": "USDT",
                        "launchTime": "1640749024000",
                        "deliveryTime": "0",
                        "deliveryFeeRate": "",
                        "priceScale": "5",
                        "leverageFilter": {
                            "minLeverage": "1",
                            "maxLeverage": "12.50",
                            "leverageStep": "0.01"
                        },
                        "priceFilter": {
                            "minPrice": "0.00005",
                            "maxPrice": "99.99990",
                            "tickSize": "0.00005"
                        },
                        "lotSizeFilter": {
                            "maxOrderQty": "460000",
                            "minOrderQty": "1",
                            "qtyStep": "1",
                            "postOnlyMaxOrderQty": "4600000"
                        },
                        "unifiedMarginTrade": "True",
                        "fundingInterval": 480,
                        "settleCoin": "USDT"
                    }
                '''

        self.instrument_info = InstrumentInfo.parse_raw(res_mock)
        self.assertEqual(self.instrument_info.priceScale, 5)
        self.assertEqual(
            self.instrument_info.leverageFilter.leverageStep,
            ED(0.01))
        self.assertEqual(
            self.instrument_info.priceFilter.tickSize,
            ED(0.00005))
        self.assertEqual(
            self.instrument_info.lotSizeFilter.maxOrderQty,
            ED(460000))


if __name__ == '__main__':
    unittest.main()
