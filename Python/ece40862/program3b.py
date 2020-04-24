from random import randint

num = randint(1, 10)
for tries in range(1, 4):
    guess = int(input('Enter your guess:'))
    if guess == num:
        print("You win!")
        break
    elif tries == 3:
        print("You lose!")