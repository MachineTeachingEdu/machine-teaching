def days_in_month(month, year):
    if month == 2:
        if (year % 400) == 0:
            return 29
        elif (year % 100) == 0:
            return 28
        elif (year % 4) == 0:
            return 29
        else:
            return 28
    elif month in (4,6,9,11):
        return 30
    elif month in (1,3,5,7,8,10, 12):
        return 31

