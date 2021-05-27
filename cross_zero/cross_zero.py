#переменные
game = 0
player1 = 0
player2 = 0
player1_move = 0
player2_move = 0
field = 0
lenght = 0
###

#функция для создания нового игрового поля
def new_field():
    M = [["-" for j in range(4)] for i in range(4)]
    M[0][0] = "\\"

    for i in range(3):
        M[0][i+1] = str(i)
        M[i+1][0] = str(i)
    return M
###

#функция для сканирования массива поля и выявления незаполненых ячеек
def scan_field(Mas):
    global lenght
    full_field = 0
    for i in range(lenght):
        for j in range(lenght):
            if Mas[i][j] == "-":
                full_field = 0
                return True
            else:
                full_field = 1
                continue
    if full_field == 1:
        return False
###

#функция для проверки выйгрышной комбинации
def check_wins(Mas):
    if (Mas[1][1] == Mas[1][2] == Mas[1][3]
        and "-" not in Mas[1]):
        return True
    elif (Mas[2][1] == Mas[2][2] == Mas[2][3]
        and "-" not in Mas[2]):
        return True
    elif (Mas[3][1] == Mas[3][2] == Mas[3][3]
        and "-" not in Mas[3]):
        return True
    elif (Mas[1][1] == Mas[2][1] == Mas[3][1]
        and ("-" not in Mas[1][1] and "-" not in Mas[2][1] and "-" not in Mas[3][1])):
        return True
    elif (Mas[1][2] == Mas[2][2] == Mas[3][2]
        and ("-" not in Mas[1][2] and "-" not in Mas[2][2] and "-" not in Mas[3][2])):
        return True
    elif (Mas[1][3] == Mas[2][3] == Mas[3][3]
        and ("-" not in Mas[1][3] and "-" not in Mas[2][3] and "-" not in Mas[3][3])):
        return True
    elif (Mas[1][1] == Mas[2][2] == Mas[3][3]
        and ("-" not in Mas[1][1] and "-" not in Mas[2][2] and "-" not in Mas[3][3])):
        return True
    elif (Mas[3][1] == Mas[2][2] == Mas[1][3]
        and ("-" not in Mas[3][1] and "-" not in Mas[2][2] and "-" not in Mas[1][3])):
        return True
    else:
        return False
###
    
#функция для печати отображения поля
def print_field(Mas, Lenght):
    for i in range(Lenght):
        print(" ".join(Mas[i]) + "\n")
###

#функция обработки ходов игроков на поле
def move(m, Mas):
    global game, player1, player2
    if m is player1_move:
        if Mas[m[1]+1][m[0]+1] != "x" and Mas[m[1]+1][m[0]+1] != "o":
            Mas[m[1]+1][m[0]+1] = "x"
            print(f"{player1} has maken the move\n")
            if check_wins(Mas):
                print(f"{player1} wins!\n")
                game = 0
            return True
        else:
            if scan_field(Mas):
                print("This cell is busy, try again.\n")
                move_player1()               
            else:
                game = 0
                print("The field is full. No wins. The game is over.\n")
                return False
                               
    elif m is player2_move:
        if Mas[m[1]+1][m[0]+1] != "x" and Mas[m[1]+1][m[0]+1] != "o":
            Mas[m[1]+1][m[0]+1] = "o"
            print(f"{player2} has maken the move\n")
            if check_wins(Mas):
                print(f"{player2} wins!\n")
                game = 0
            return True
        else:
            if scan_field(Mas):
                print("This cell is busy, try again.\n")
                move_player2()               
            else:
                game = 0
                print("The field is full. No wins. The game is over.\n")
                return False
        
    else:
        return False
###

#функция обработки ходов первого игрока
def move_player1():
    global player1_move, field, lenght
    player1_move = str(input(f"Move of {player1} (x): "))
    player1_move = player1_move.split("-")
    player1_move = [int(item) for item in player1_move]
    if (((int(player1_move[0]) == 0 or int(player1_move[0]) == 1 or int(player1_move[0]) == 2)
        and (int(player1_move[1]) == 0 or int(player1_move[1]) == 1 or int(player1_move[1]) == 2))):
        if move(player1_move, field):
            print_field(field, lenght)
        else:
            print("You entered wrong value, please, try again.\n")
            move_player1()
    else:
        print("You entered wrong value, please, try again.\n")
        move_player1()
###

#функция обработки ходов второго игрока
def move_player2():
    global player2_move, field, lenght
    player2_move = str(input(f"Move of {player2} (o): "))
    player2_move = player2_move.split("-")
    player2_move = [int(item) for item in player2_move]
    if (((int(player2_move[0]) == 0 or int(player2_move[0]) == 1 or int(player2_move[0]) == 2)
        and (int(player2_move[1]) == 0 or int(player2_move[1]) == 1 or int(player2_move[1]) == 2))):
        if move(player2_move, field):
            print_field(field, lenght)
        else:
            print("You entered wrong value, please, try again.\n")
            move_player2()
    else:
        print("You entered wrong value, please, try again.\n")
        move_player2()
###

#функция инициализации игровой сессии
def start_game():
    print()
    print("For starting game Enter 'Yes'")
    print("For closing game Enter 'No'")
    choice = str(input("\nEnter your choice: ")).lower()

    if choice == "yes":
        global player1, player2, game, field, lenght
        player1 = input("Enter the name of the first player (x): ")
        player2 = input("Enter the name of the second player (o): ")
        print("The game started!\n")
        field = new_field()
        lenght = len(field)
        game = 1
        return True
    elif choice == "no":
        print("Okay, close the game.\n")
        return False
    else:
        print("You entered wrong choice, please, enter again.")
        start_game()
###

#игровая сессия
print("Welcome to the game Crosses and Zeros!")

if start_game():
    print_field(field, lenght)
else:
    print_field(field, lenght)

while game == 1:
    print("Enter coordinates of move in row-column format, for example, 0-0, 0-2, 1-2")
    move_player1()
    if game == 0:
        break
    print("Enter coordinates of move in row-column format, for example, 0-0, 0-2, 1-2")
    move_player2()
    
print("Thank you for the game!")
input("Press close to exit...")
###

