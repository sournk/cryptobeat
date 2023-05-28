from advparser import OrderSide, SimpleOrder, ComplexOrder


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

    co = ComplexOrder()
    co.orders = [SimpleOrder(side=OrderSide.BUY, qty=1, open_price=10, stop_loss=0, take_profit=15), 
                 SimpleOrder(side=OrderSide.BUY, qty=2, open_price=11, stop_loss=0, take_profit=18)]

    co.orders.append(SimpleOrder(side=OrderSide.BUY, qty=3,
                                open_price=12, stop_loss=0, take_profit=22))
    
    co.calculate()
    print(co)

    # co.orders.pop()    





if __name__ == '__main__':
    main()
