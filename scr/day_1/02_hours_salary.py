hour_cost = int(input("Укажите стоимость часа >>> "))
day_quantity = int(input("Укажите количество дней >>> "))

total = (hour_cost * 8) * day_quantity
final = total * 0.87

print("Размер оплаты", final)