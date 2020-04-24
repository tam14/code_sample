num_list = [10, 20, 10, 40, 50, 60, 70]
target = int(input("What is your target number? "))

found = False
for x in range(6):
    for y in range(x + 1, 7):
        val = num_list[x] + num_list[y]
        if val == target:
            print('index1={}, index2={}'.format(x, y))
            break
    else:
        continue
    break
