days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

while True:  
    user_input = input("1-7 hurtel too oruul (garah bol 'stop'): ").strip().lower()
    
    if user_input == 'stop':
        print("Program zogsson")
        break
    
    if user_input.isdigit():  
        n = int(user_input)
        if 1 <= n <= 7:
            print(f"odor: {days[n-1]}")  
        else:
            print("Aldaa: 1-7 hurtel too oruulna uu")  
    else:
        print("Aldaa: Too oruulna uu") 
