def days_in_month(month):
    if month == 2:
        return 28
    elif month in (4,6,9,11):
        return 30
    elif month in (1,3,5,7,8,10, 12):
        return 31
