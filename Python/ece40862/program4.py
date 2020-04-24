birth_dict = {'Albert Einstein': '03/14/1879', 'Benjamin Franklin': '01/17/1706', 'Ada Lovelace': '12/10/1815'}
print("Welcome to the birthday dictionary. We know the birthdays of:")
for name in birth_dict.keys():
    print("{}".format(name))

name_request = input("Who's birthday do you want to look up?\n")
print("{}'s birthday is {}".format(name_request, birth_dict[name_request]))