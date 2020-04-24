num = int(input("How many Fibonacci numbers would you like to generate? "))
first = 1
second = 1
idx = 0

print("The Fibonacci Sequence is: ", end='')
while idx != num:
    if idx == 0:
        print("1", end='')
    elif idx == 1:
        print(", 1", end='')
    else:
        print(", {}".format(first + second), end='')
        second = first + second
        first = second - first
    idx = idx + 1
