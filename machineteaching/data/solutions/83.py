def euro_conversion(amount, exchange_rate):
    euro = amount//exchange_rate

    euro50s = int(euro // 50)
    remainingEuros = euro % 50

    euro20s = int(remainingEuros // 20)
    remainingEuros = remainingEuros % 20

    euro10s = int(remainingEuros // 10)
    remainingEuros = remainingEuros % 10

    euro5s = int(remainingEuros // 5)
    remainingEuros = remainingEuros % 5

    return(euro, euro50s, euro20s, euro10s, euro5s, remainingEuros)
