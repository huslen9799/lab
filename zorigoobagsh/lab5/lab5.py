class Restaurant:
    def __init__(self):
        self.menu = {
            "1": {"name": "Борщ", "price": 12000},
            "2": {"name": "Пицца", "price": 25000},
            "3": {"name": "Бургер", "price": 15000},
            "4": {"name": "Кофе", "price": 8000},
            "5": {"name": "Сок", "price": 5000}
        }
        self.__order = [] 

    def show_menu(self):
        print("\n=== Меню ===")
        for key, item in self.menu.items():
            print(f"{key}: {item['name']} - {item['price']}₮")

    def add_order(self, choice, quantity):
        """Гаднаас order нэмэх зөвхөн энэ method ашиглана"""
        if choice in self.menu:
            self.__order.append({
                "name": self.menu[choice]['name'],
                "unit_price": self.menu[choice]['price'],  
                "qty": quantity,

                "total_price": self.menu[choice]['price'] * quantity  
            })
            print(f"{self.menu[choice]['name']} x {quantity} захиалагдлаа.")
        else:
            print(" Зөв сонголт хийж оруулна уу!")

    def calculate_total(self):

        total = 0
        for item in self.__order:
            total += item['total_price']
        return total

    def print_bill(self):
        if not self.__order:
            print("Та ямар ч хоол захиалаагүй байна.")
            return
        print("\n=== Таны захиалга ===")
        print(f"{'Хоол':<10} {'Ширхэг':<8} {'Нэг ширхэг үнэ':<15} {'Нийт үнэ':<10}")
        for item in self.__order:
            print(f"{item['name']:<10} {item['qty']:<8} {item['unit_price']:<15} {item['total_price']:<10}")
        total = self.calculate_total()  
        print(f"\nНийт төлбөр: {total}₮")
