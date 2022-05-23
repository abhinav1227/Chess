import random

piece_score = {'K': 0, 'Q': 10, 'R': 5, 'B': 3, 'N': 3, 'P': 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 4

# picks and return a random move
def find_random_move(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves)-1)]

# find the best move based on material alone
def find_best_move(gs, valid_moves):
    '''# greedy algorithm
    turn_multiplier = 1 if gs.white_to_move else -1
    max_score = -CHECKMATE
    best_move = None
    for player_move in valid_moves:
        gs.make_move(player_move)
        if gs.checkmate:
            score = CHECKMATE
        elif gs.stalemate:
            score = STALEMATE
        else:
            score = turn_multiplier * score_material(gs.board)
        if score > max_score:
            max_score = score
            best_move = player_move
        gs.undo_move()
    return best_move'''

    # or(two move ahead)
    turn_multiplier = 1 if gs.white_to_move else -1
    opponent_min_max_score = CHECKMATE
    best_player_move = None
    random.shuffle(valid_moves)
    for player_move in valid_moves:
        gs.make_move(player_move)

        # looking at opponent moves and finding the max
        opponent_moves = gs.get_valid_moves()
        if gs.stalemate:
            opponent_max_score = STALEMATE
        elif gs.checkmate:
            opponent_max_score = -CHECKMATE
        else:
            opponent_max_score = -CHECKMATE
            for opponent_move in opponent_moves:
                gs.make_move(opponent_move)
                gs.get_valid_moves()
                if gs.checkmate:
                    score = CHECKMATE
                elif gs.stalemate:
                    score = STALEMATE
                else:
                    score = -turn_multiplier * score_material(gs.board)
                if score > opponent_max_score:
                    opponent_max_score = score
                gs.undo_move()

        if opponent_max_score < opponent_min_max_score:
            opponent_min_max_score = opponent_max_score
            best_player_move = player_move
        gs.undo_move()
    return best_player_move

# helper method to make first recursive call
def find_best_move_(gs, valid_moves):
    global next_move, counter
    next_move = None
    counter = 0
    random.shuffle(valid_moves)
    #find_move_min_max(gs, valid_moves, DEPTH, gs.white_to_move)
    #find_move_nega_max(gs, valid_moves, DEPTH, 1 if gs.white_to_move else -1)
    find_move_nega_max_alpha_beta(gs, valid_moves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.white_to_move else -1)
    print(counter)
    return next_move

def find_move_min_max(gs, valid_moves, depth, white_to_move):
    global next_move, counter

    counter += 1
    if depth == 0:
        return score_material(gs.board)

    if white_to_move:
        max_score = -CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            next_move = gs.get_valid_moves()
            score = find_move_min_max(gs, next_move, depth-1, False)
            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undo_move()
        return max_score
    else:
        min_score = CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            next_move = gs.get_valid_moves()
            score = find_move_min_max(gs, next_move, depth-1, True)
            if score < min_score:
                min_score = score
                if depth == DEPTH:
                    next_move = move
                gs.undo_move()
            return min_score

def find_move_nega_max(gs, valid_moves, depth, turn_multiplier):
    global next_move, counter

    counter += 1
    if depth == 0:
        return turn_multiplier * score_board(gs)

    max_score = -CHECKMATE
    for move in valid_moves:
        gs.make_move(move)
        next_move = gs.get_valid_moves()
        score = -find_move_nega_max(gs, next_move, depth-1, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        gs.undo_move()
    return max_score

def find_move_nega_max_alpha_beta(gs, valid_moves, depth, alpha, beta, turn_multiplier):
    global next_move, counter

    counter += 1
    if depth == 0:
        return turn_multiplier * score_board(gs)

    # move ordering - evaluate capture or getting checked (implement later)2
    max_score = -CHECKMATE
    for move in valid_moves:
        gs.make_move(move)
        next_move = gs.get_valid_moves()
        score = -find_move_nega_max_alpha_beta(gs, next_move, depth-1, -beta, -alpha, -turn_multiplier) # get reversed for opponent
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        gs.undo_move()
        if max_score > alpha:  # pruning happens
            alpha = max_score
        if alpha >= beta:
            break
    return max_score

'''Positive score is good for white, negative score is good for black'''
def score_board(gs):
    if gs.checkmate:
        if gs.white_to_move:
            return -CHECKMATE # black wins
        else:
            return CHECKMATE # white wins
    elif gs.stalemate:
        return STALEMATE

    score = 0
    for row in gs.board:
        for square in row:
            if square[0] == 'w':
                score += piece_score[square[1]]
            elif square[0] == 'b':
                score -= piece_score[square[1]]

    return score

# score the board based on material
def score_material(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += piece_score[square[1]]
            elif square[0] == 'b':
                score -= piece_score[square[1]]

    return score

