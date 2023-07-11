def fatorial(number):
    total = 1

    for i in range(number, 1, -1):
        total = total * i
    
    return total        
