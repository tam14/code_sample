a = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
print("a = {}".format(a))
limit = int(input('Enter number: '))
new_list = [val for val in a if val < limit]
print("The new list is {}".format(new_list))
