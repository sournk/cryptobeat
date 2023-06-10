import unittest

from simpleorder.order_details import MarketPosition
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

    def test_initial_values(self):
        self.assertEqual(self.position1.qty, 10)
        self.assertEqual(self.position1.price, 100)
        self.assertEqual(self.position1.value, 1000)

    def test_addition(self):
        result = self.position1 + self.position2
        self.assertEqual(result.qty, 15)
        self.assertLess(abs(result.price-116.67), 0.01)
        self.assertEqual(result.value, 1750)

    def test_subtraction(self):
        result = self.position1 - self.position2
        self.assertEqual(result.qty, 5)
        self.assertEqual(result.price, 50)
        self.assertEqual(result.value, 250)

    def test_comparison(self):
        self.assertTrue(self.position1 < self.position2)

    def test_qty_setter(self):
        self.position1.qty = 15
        self.assertEqual(self.position1.qty, 15)
        self.assertEqual(self.position1.value, 1500)

    def test_price_setter(self):
        self.position1.price = 200
        self.assertEqual(self.position1.price, 200)
        self.assertEqual(self.position1.value, 2000)

    def test_compare_positions_by_price_using_lt(self):
        self.assertLess(self.position1, self.position2)

    def test_fit_decimal_price(self):
        mp = MarketPosition(price=12.7,
                            qty=100)
        self.instrument_info_people.priceFilter.tickSize = 0.33
        mp.fit_price(instrument_info=self.instrument_info_people)
        self.assertEqual(mp.price, 12.54)

    def test_fit_int_tick(self):
        mp = MarketPosition(price=12.7,
                            qty=100)
        self.instrument_info_people.priceFilter.tickSize = 1
        mp.fit_price(instrument_info=self.instrument_info_people)
        self.assertEqual(mp.price, 13)

    def test_fit_decimal_qtyStep(self):
        mp = MarketPosition(price=12.7,
                            qty=100.3)
        self.instrument_info_people.lotSizeFilter.qtyStep = 0.2
        mp.fit_qty(instrument_info=self.instrument_info_people)
        self.assertEqual(mp.qty, 100.2)

    def test_fit_int_qtyStep(self):
        mp = MarketPosition(price=12.7,
                            qty=101.3)
        self.instrument_info_people.lotSizeFilter.qtyStep = 2
        mp.fit_qty(instrument_info=self.instrument_info_people)
        self.assertEqual(mp.qty, 102)


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
            0.01)
        self.assertEqual(
            self.instrument_info.priceFilter.tickSize,
            0.00005)
        self.assertEqual(
            self.instrument_info.lotSizeFilter.maxOrderQty,
            460000)

if __name__ == '__main__':
    unittest.main()
