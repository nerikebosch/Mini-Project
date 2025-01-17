"""
Tic Tac Toe Player
 Tic Tac Toe game implementation with an AI opponent using the minimax algorithm.

This module provides a complete implementation of a Tic Tac Toe game, including game state 
management and an AI player that makes optimal moves using the minimax algorithm with 
alpha-beta pruning. The game board is represented as a 3x3 list of lists, where each cell 
contains either 'X', 'O', or None (empty).

Global Constants:
    X (str): Represents the X player
    O (str): Represents the O player
    EMPTY (None): Represents an empty cell
"""

import math
import copy 

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    
    Returns:
        list: A 3x3 nested list representing the game board, with all positions set to EMPTY.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    
    Args:
        board (list): The current game board state.
        
    Returns:
        str: 'X' if X's turn, 'O' if O's turn. X goes first, and turns alternate.
        The return value is determined by counting the number of X's and O's on the board.
    """
    # if board == initial_state():
    #     return X
    x = sum(row.count(X) for row in board)
    o = sum(row.count(O) for row in board)
    
    if x > o:
        return O
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    
    Args:
        board (list): The current game board state.
        
    Returns:
        set: A set of tuples (i, j) representing all empty cells where i is the row 
             index (0-2) and j is the column index (0-2).
             
    """
    act = set()
    for i in range(0,3):
        for j in range(0, 3):
            if board[i][j] == EMPTY:
                act.add((i, j))
    return act


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    
    Args:
        board (list): The current game board state.
        action (tuple): A tuple (i, j) representing the move to make.
        
    Returns:
        list: A new board state with the move applied.
        
    Raises:
        Exception: If the action is not valid for the current board.
        
    """
    if action not in actions(board):
        raise Exception("Invalid action")
     
    newBoard = copy.deepcopy(board)
    (i, j) = action
    newBoard[i][j] = player(board)
    
    return newBoard   
    

def winner(board):
    """
    Returns the winner of the game, if there is one.
    
    Checks all rows, columns (using transpose), and both diagonals for three in a row
    of either X or O.
    
    Args:
        board (list): The current game board state.
        
    Returns:
        str or None: 'X' if X has won, 'O' if O has won, None if no winner.
    """
    # transpose list of lists #  **** 
    def transpose(board): 
        return [list(sub) for sub in zip(*board)]
    # checking
    def checkin(board):
        #check row 
        for row in board:
            if all(cell == X for cell in row):
                return X
            if all(cell == O for cell in row):
                return O
        # check diag
        if (board[0][0] == board[1][1] == board[2][2]) and board[0][0] is not EMPTY:
            return board[0][0] 
        if (board[2][0] == board[1][1] == board[0][2]) and board[2][0] is not EMPTY:
            return board[2][0]
        return None
    return (checkin(board) or checkin(transpose(board)))


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    
    Determine if the game is over.
    
    A game is over if either:
    1. Someone has won the game
    2. All cells are filled (no more valid moves)
    
    Args:
        board (list): The current game board state.
        
    Returns:
        bool: True if game is over, False otherwise.
    """
    if (winner(board) is not None) or (not any(None in row for row in board)):
        return True
    return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    
    Args:
        board (list): The current game board state.
        
    Returns:
        int: 1 if X has won, -1 if O has won, 0 for a draw.
        This utility function is used by the minimax algorithm to evaluate board states.
        
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    
    Args:
        board (list): The current game board state.
        
    Returns:
        tuple or None: A tuple (i, j) representing the optimal move, or None if the game is over.
        For X (maximizing player), chooses the move with the highest minimax value.
        For O (minimizing player), chooses the move with the lowest minimax value.
        
    """
    if terminal(board):
        return None
    
    mx = float('-inf')
    mn = float('inf')
    
    if player(board) == X:
        return max_val(board, mx, mn)[1]
    else:
        return min_val(board, mx, mn)[1]   

def max_val(board, mx, mn):
    """
    Args:
        board (list): The current game board state.
        mx (float): Alpha value for alpha-beta pruning.
        mn (float): Beta value for alpha-beta pruning.
        
    Returns:
        list: A list containing [best_value, best_action], where best_value is the minimax
              value of the optimal move and best_action is the corresponding move.
    """
    if terminal(board):
        return [utility(board), None]
        
    best_val = float('-inf')
    best_act = None
    
    for act in actions(board):
        mini_val = min_val(result(board, act), mx, mn)[0]
        mx = max(mx, mini_val)
            
        if mini_val > best_val:
            best_val = mini_val
            best_act = act
            
        if mx >= mn:
            break
        
    return [best_val, best_act]

def min_val(board, mx, mn):
    """
    Helper function for minimax that handles minimizing player's turns.
    
    Args:
        board (list): The current game board state.
        mx (float): Alpha value for alpha-beta pruning.
        mn (float): Beta value for alpha-beta pruning.
        
    Returns:
        list: A list containing [best_value, best_action], where best_value is the minimax
              value of the optimal move and best_action is the corresponding move.
    """
    if terminal(board):
        return [utility(board), None]
        
    best_val = float('inf')
    best_act = None
    for act in actions(board):
        maxi_val = max_val(result(board, act), mx, mn)[0]
        mn = min(mn, maxi_val)
            
        if maxi_val < best_val:
            best_val = maxi_val
            best_act = act
        if mx >= mn:
            break
    
    return [best_val, best_act]