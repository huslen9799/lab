last_even = None 

for i in range(1, 11):
    if i % 2 != 0:  
        continue
    last_even = i 

print(last_even)
