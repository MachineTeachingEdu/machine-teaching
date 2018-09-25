def is_prime(number):
    '''Returns True for prime numbers, False otherwise'''
    #Edge Cases
    if number == 1:
        prime = False
    elif number == 2:
        prime = True
    #All other primes    
    else:
        prime = True
        for check_number in range(2, (number / 2)+1):
            if number % check_number == 0:
                prime = False
                break
    return prime
