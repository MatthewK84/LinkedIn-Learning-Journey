#Start By Defining Valid Move
def is_valid_move(x, y, board):
    return 0 <= x < 8 and 0 <= y < 8 and board[x][y] == -1

#Get All Possible Moves
def get_possible_moves(x, y, board):
    moves = [
        (x+2, y+1), (x+2, y-1), (x-2, y+1), (x-2, y-1),
        (x+1, y+2), (x+1, y-2), (x-1, y+2), (x-1, y-2)
    ]
    return [(x, y) for x, y in moves if is_valid_move(x, y, board)]

def get_degree(x, y, board):
    return len(get_possible_moves(x, y, board))

#Start the Sequence of Solving Knights Tour
def solve_knights_tour(start_x=0, start_y=0):
    # Initialize Board with -1 
    board = [[-1 for _ in range(8)] for _ in range(8)]
    moves = [(start_x, start_y)]
    board[start_x][start_y] = 0
    
    # Current Position
    pos = 1
    curr_x, curr_y = start_x, start_y
    
    # Start Tour Completion
    while pos < 64:
        # All Possible Moves from Current Position
        possible_moves = get_possible_moves(curr_x, curr_y, board)
        
        if not possible_moves:
            return None  # No solution found
        
        # Warnsdorff's Heuristic: Choose Move with the Minimum Number of Onward Moves
        next_moves = [(x, y, get_degree(x, y, board)) for x, y in possible_moves]
        next_x, next_y, _ = min(next_moves, key=lambda x: x[2])
        
        # Next Move
        board[next_x][next_y] = pos
        moves.append((next_x, next_y))
        curr_x, curr_y = next_x, next_y
        pos += 1
    
    return moves

#Print Output in Readable and Verifiable Format
def print_tour(moves):
    board = [[-1 for _ in range(8)] for _ in range(8)]
    for i, (x, y) in enumerate(moves):
        board[x][y] = i
    
    print("\nKnight's Tour Sequence:")
    for row in board:
        print(" ".join(f"{x:2d}" if x != -1 else "##" for x in row))

# Function Implementation
if __name__ == "__main__":
    # Find Tour Starting from Position (0,0)
    solution = solve_knights_tour(0, 0)
    
    if solution:
        print("Solution Found!")
        print("\nMove Sequence:")
        for i, (x, y) in enumerate(solution):
            print(f"Move {i}: ({x}, {y})")
        print_tour(solution)
    else:
        print("No Solution Found!")
