num = int(input("Тоог оруулна уу: "))
if num < 0:
    num = -num
digit_sum = 0
while num > 0:
    digit_sum = digit_sum + (num % 10)  
    num = num // 10                  
print("ornii niilber", digit_sum)
