
from lab4 import BankAccount  

print("=== BankAccount Програм ===")
user_pin = int(input("Шинэ данс үүсгэх PIN кодоо оруулна уу: "))
account = BankAccount(user_pin)

while True:
    print("\nОдоогийн үйлдэл сонгоно уу:")
    print("1: Мөнгө хийх")
    print("2: Мөнгө хасах")
    print("3: Үлдэгдэл харах")
    print("0: Программаас гарах")
    
    choice = input("Сонголт: ")
    
    if choice == "1":
        pin = int(input("PIN кодоо оруулна уу: "))
        amount = int(input("Мөнгөн дүн оруулна уу: "))
        print(account.deposit(pin, amount))

    elif choice == "2":
        pin = int(input("PIN кодоо оруулна уу: "))
        amount = int(input("Мөнгөн дүн оруулна уу: "))
        print(account.withdraw(pin, amount))

    elif choice == "3":
        pin = int(input("PIN кодоо оруулна уу: "))
        print(account.get_balance(pin))

    elif choice == "0":
        print("Программаас гарлаа. Баяртай!")
        break

    else:
        print("❌ Зөв сонголт хийж оруулна уу!")
