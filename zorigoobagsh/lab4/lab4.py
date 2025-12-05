
class BankAccount:
    def __init__(self, pin):
        self.pin = pin
        self.balance = 0

    def deposit(self, pin, amount):
        if pin == self.pin:  
            self.balance += amount
            return f"Таны данс {amount}₮-р цэнэглэгдэж нийт үлдэгдэл {self.balance}₮ боллоо."
        else:
            return " Pin код буруу байна!"

    def withdraw(self, pin, amount):
        if pin == self.pin:  
            if amount <= self.balance:
                self.balance -= amount
                return f"Таны данснаас {amount}₮-р хасагдаж нийт үлдэгдэл {self.balance}₮ боллоо."
            else:
                return " Дансны үлдэгдэл хүрэлцэхгүй байна!"
        else:
            return " Pin код буруу байна!"

    def get_balance(self, pin):
        if pin == self.pin:  
            return f"Таны дансны үлдэгдэл {self.balance}₮ байна."
        else:
            return " Pin код буруу байна!"
