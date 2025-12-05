
from lab5 import Restaurant  

restaurant = Restaurant()
print("=== Рестораны систем ===")

while True:
    restaurant.show_menu()
    choice = input("Хоол сонгох (гарах бол 'q' дарна уу): ")
    
    if choice.lower() == 'q':
        break
    
    try:
        quantity = int(input("Хэд ширхэг авах вэ? "))
        if quantity <= 0:
            print("❌ Ширхэг 0-с их байх ёстой!")
            continue
    except ValueError:
        print("❌ Зөв тоо оруулна уу!")
        continue

    restaurant.add_order(choice, quantity)

restaurant.print_bill()
