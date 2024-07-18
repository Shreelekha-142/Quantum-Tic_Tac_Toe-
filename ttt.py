import qiskit
from qiskit import QuantumCircuit
import json
from qiskit_aer import Aer
from tkinter import Tk, messagebox, simpledialog, Label
import numpy as np

# Use QASM simulator backend
backend = Aer.get_backend('qasm_simulator')

def run_on_simulator(circuit):
    job = backend.run(circuit, shots=1)
    result = job.result()
    counts = result.get_counts(circuit)
    return counts

global theBoard

def resetBoard():
    return {'1': [' ', 0], '2': [' ', 0], '3': [' ', 0],
            '4': [' ', 0], '5': [' ', 0], '6': [' ', 0],
            '7': [' ', 0], '8': [' ', 0], '9': [' ', 0]}  # space contains empty cell and 0 contains state of cell

def get_board_display(board):
    display = ""
    for i in range(1, 10):
        cell = board[str(i)][0]
        if board[str(i)][1] == 1:  # quantum move
            cell += '*'
        display += cell
        if i % 3 == 0:
            display += '\n'
            if i != 9:
                display += '-+-+-\n'
        else:
            display += '|'
    return display

def update_board_display(label_board, board):
    display = get_board_display(board)
    label_board.config(text=display)

def make_classic_move(theBoard, turn, count, circuit, label_board):
    valid_move = False
    valid_moves = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
    
    while not valid_move:
        location = simpledialog.askstring("Input", "Which location? (1-9)")

        if location in valid_moves:
            if theBoard[location][0] == ' ':
                valid_move = True
                theBoard[location][0] = turn
                count += 1
                theBoard[location][1] = 0  # classical
                circuit.x(int(location) - 1)
                update_board_display(label_board, theBoard)
            else:
                messagebox.showinfo("Invalid Move", "That place is already filled.")
        else:
            messagebox.showinfo("Invalid Input", "Please select a square from 1-9")

    return theBoard, turn, count, circuit

def make_quantum_move(theBoard, count, circuit, turn, label_board):
    valid_move = False
    valid_moves = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]

    while not valid_move:
        location1 = simpledialog.askstring("Input", "Which location? (1-9)")
        location2 = simpledialog.askstring("Input", "Which location? (1-9)")

        if (theBoard[location1][0] == ' ' and theBoard[location2][0] == ' ' and location1 != location2):
            theBoard[location1][0] = turn
            theBoard[location2][0] = turn
            count += 2
            theBoard[location1][1] = 1  # quantum
            theBoard[location2][1] = 1  # quantum
            circuit.h(int(location1) - 1)
            circuit.x(int(location2) - 1)
            circuit.cx(int(location1) - 1, int(location2) - 1)
            update_board_display(label_board, theBoard)
            valid_move = True
        else:
            messagebox.showinfo("Invalid Move", "You have selected an invalid position/s")
    
    return theBoard, count, circuit, turn

def measure(circuit, theBoard, count, label_board):
    messagebox.showinfo("Collapse", "Trigger collapse.")

    for i in range(9):
        circuit.measure(i, i)

    counts = run_on_simulator(circuit)
    out = json.dumps(counts)
    string = out[2:11]

    for i in range(9):
        if string[i] == '1':
            theBoard[str(9 - i)][1] = 0
        else:
            theBoard[str(9 - i)][1] = 0
            theBoard[str(9 - i)][0] = ' '

    count = sum(1 for val in theBoard.values() if val[0] != ' ')
    circuit.reset(range(9))

    for i in range(9):
        if string[8 - i] == '1':
            circuit.x(i)

    update_board_display(label_board, theBoard)

    return circuit, string, theBoard, count

def check_win(theBoard, turn):
    if (theBoard['7'][0] == theBoard['8'][0] == theBoard['9'][0] != ' ' and
        theBoard['7'][1] == theBoard['8'][1] == theBoard['9'][1] == 0):
        messagebox.showinfo("Game Over", f" ** {theBoard['8'][0]} won **")
        return True

    elif (theBoard['4'][0] == theBoard['5'][0] == theBoard['6'][0] != ' ' and
          theBoard['4'][1] == theBoard['5'][1] == theBoard['6'][1] == 0):
        messagebox.showinfo("Game Over", f" ** {theBoard['5'][0]} won **")
        return True

    elif (theBoard['1'][0] == theBoard['2'][0] == theBoard['3'][0] != ' ' and
          theBoard['1'][1] == theBoard['2'][1] == theBoard['3'][1] == 0):
        messagebox.showinfo("Game Over", f" ** {theBoard['2'][0]} won **")
        return True

    elif (theBoard['1'][0] == theBoard['4'][0] == theBoard['7'][0] != ' ' and
          theBoard['1'][1] == theBoard['4'][1] == theBoard['7'][1] == 0):
        messagebox.showinfo("Game Over", f" ** {theBoard['4'][0]} won **")
        return True

    elif (theBoard['2'][0] == theBoard['5'][0] == theBoard['8'][0] != ' ' and
          theBoard['2'][1] == theBoard['5'][1] == theBoard['8'][1] == 0):
        messagebox.showinfo("Game Over", f" ** {theBoard['5'][0]} won **")
        return True

    elif (theBoard['3'][0] == theBoard['6'][0] == theBoard['9'][0] != ' ' and
          theBoard['3'][1] == theBoard['6'][1] == theBoard['9'][1] == 0):
        messagebox.showinfo("Game Over", f" ** {theBoard['6'][0]} won **")
        return True

    elif (theBoard['7'][0] == theBoard['5'][0] == theBoard['3'][0] != ' ' and
          theBoard['7'][1] == theBoard['5'][1] == theBoard['3'][1] == 0):
        messagebox.showinfo("Game Over", f" ** {theBoard['5'][0]} won **")
        return True

    elif (theBoard['1'][0] == theBoard['5'][0] == theBoard['9'][0] != ' ' and
          theBoard['1'][1] == theBoard['5'][1] == theBoard['9'][1] == 0):
        messagebox.showinfo("Game Over", f" ** {theBoard['5'][0]} won **")
        return True

    return False

def game():
    global theBoard
    turn = 'X'
    count = 0
    win = False
    madeMove = False
    circuit = QuantumCircuit(9, 9)

    root = Tk()
    root.title("Quantum Tic-Tac-Toe")

    label_board = Label(root, text="", font=("Arial", 16))
    label_board.pack()

    while not win:
        update_board_display(label_board, theBoard)
        move = simpledialog.askstring("Input", f"It's your turn {turn}. Do you want to make a (1) classical move, (2) quantum move, (3) collapse?, or (4) quit?")

        if move == '1':
            theBoard, turn, count, circuit = make_classic_move(theBoard, turn, count, circuit, label_board)
            madeMove = True
        elif move == '2' and count > 8:
            messagebox.showinfo("Invalid Move", "There aren't enough empty spaces for that!")
        elif move == '2' and count < 8:
            theBoard, count, circuit, turn = make_quantum_move(theBoard, count, circuit, turn, label_board)
            madeMove = True
        elif move == '3':
            circuit, string, theBoard, count = measure(circuit, theBoard, count, label_board)
        elif move == '4':
            break
        
        if count >= 5:
            win = check_win(theBoard, turn)
            if win:
                break

        if count == 9:
            circuit, string, theBoard, count = measure(circuit, theBoard, count, label_board)
            win = check_win(theBoard, turn)
            if count == 9:
                messagebox.showinfo("Game Over", "It's a Tie!")
                win = True

        if madeMove:
            madeMove = False
            turn = 'O' if turn == 'X' else 'X'

    if messagebox.askyesno("Play Again?", "Play Again?"):
        theBoard = resetBoard()
        game()

def start_menu():
    start_menu = """
    Start Menu:

    1. Start Game
    2. How to Play
    3. Quit
    """ 
    
    messagebox.showinfo("Welcome", "###########################\n### Quantum Tic-Tac-Toe ###\n###########################")
    
    choice = '0'
    while choice != '1':
        choice = simpledialog.askstring("Menu", start_menu + "\nWhat would you like to do?")

        if choice == '2':
            How_To = """ 
            In Quantum Tic-Tac-Toe, each square starts empty and your goal is to create a line of three of your naughts/crosses. 
            Playing a classical move will result in setting a square permanently as your piece.
            Playing a quantum move will create a superposition between two squares of your choosing. You may only complete a quantum move in two empty squares.
            The board will collapse when the board is full. At collapse, each superposition is viewed and only 1 piece of the superposition will remain. 
            Powerup Each player can decide to collapse the board prematurely, they may do this once per round each.
            """
            messagebox.showinfo("How to Play", How_To)

        if choice == '3':
            messagebox.showinfo("Goodbye", "Goodbye")
            return '3'
    
    return choice

if __name__ == "__main__":
    root = Tk()
    root.withdraw()  # Hide the root Tkinter window
    theBoard = resetBoard()
    if start_menu() == '1':
        game()
