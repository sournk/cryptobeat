from advparser import OrderSide, SimpleOrder


def main() -> None:
    input = """
    🎈 #LINK/USDT - LONG📈

    🟢 Открытие - 6.342-6.153

    ✅ Цели - 1-6.411 2-6.475  3-6.529 4-6.611

    ♾ - Плечо - х20 (Cross)

    🔴 Стоп - 5.965
    """

    input = """
    SOL | USDT = LONG

    Точка входа: 19.180
    Тейк-профит: 19.422 | 19.854
    Кредитное плечо: 50x
    Стоп-лосс: 18.609

        """

    # ap = AdviserPrediction('Test', input)
    # ap.calc(100, 25)
    # print(ap)

    so = SimpleOrder(side=OrderSide.BUY,
                     qty=10,
                     open_price=10,
                     stop_loss=2,
                     take_profit=120)

    print(so)

if __name__ == '__main__':
    main()
