def amount(transaction_list):
    total = 0
    for item in transaction_list:
        op, value = item
        if op == 'D':
            total += value
        elif op == 'W':
            total -= value
    return total
