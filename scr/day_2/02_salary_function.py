def salary(hour_cost: int, day_quantity: int):
    total = (hour_cost * 8) * day_quantity
    final = total * 0.87

    return final


a = salary(100, 1)
b = salary(100, 2)

print(a, b)