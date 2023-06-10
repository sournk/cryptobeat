import unittest

from simpleorder import MarketPosition


class MarketPositionTests(unittest.TestCase):

    def setUp(self):
        self.position1 = MarketPosition(10, 100)
        self.position2 = MarketPosition(5, 150)

    def test_initial_values(self):
        self.assertEqual(self.position1.qty, 10)
        self.assertEqual(self.position1.price, 100)
        self.assertEqual(self.position1.value, 1000)

    def test_addition(self):
        result = self.position1 + self.position2
        self.assertEqual(result.qty, 15)
        self.assertEqual(result.price, 110)
        self.assertEqual(result.value, 2250)

    def test_subtraction(self):
        result = self.position1 - self.position2
        self.assertEqual(result.qty, 5)
        self.assertEqual(result.price, 90)
        self.assertEqual(result.value, 450)

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

    def test_repr(self):
        expected = "MarketPosition(qty=10, price=100, value=1000)"
        self.assertEqual(repr(self.position1), expected)


if __name__ == '__main__':
    unittest.main()
