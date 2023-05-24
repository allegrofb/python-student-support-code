x = input_int()
y = input_int()

# print(y + 2 if (x == 0 if x < 1 else x == 2) else y + 10)

if (x < 1 and x == 0) or x == 2:
    print(y+2)
else:
    print(y+10)
