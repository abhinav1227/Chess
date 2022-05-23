'''
This class is responsible for storing all the info about the current state of a chess
game. It will also be responsible for determining the valid moves at the current
state. It will also keep a move log
'''

class GameState:
    def __init__(self):
        # board is an 8*8 2-D list and each element has two char.
        # The first char is color of piece and second is type.

        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']]

        self.move_functions = {'P': self.get_pawn_moves, 'R': self.get_rook_moves,
                               'B': self.get_bishop_moves, 'Q': self.get_queen_moves,
                               'K': self.get_king_moves, 'N': self.get_knight_moves}
        self.white_to_move = True
        self.move_log = []
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.enpassant_possible = ()  # coordinates of the square where en-passant capture is possible
        self.enpassant_possible_logs = [self.enpassant_possible]
        self.current_castling_right = CastlingRights(True, True, True, True)
        self.castle_rights_log = [CastlingRights(self.current_castling_right.wks, self.current_castling_right.bks, self.current_castling_right.wqs,  self.current_castling_right.bqs)]

    def make_move(self, move):
        self.board[move.start_row][move.start_col] = '--'
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move

        # updating king move
        if move.piece_moved == 'wK':
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == 'bK':
            self.black_king_location = (move.end_row, move.end_col)

        # pawn promotion
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + 'Q'

        # en passant move update the board to capture the pawn
        if move.is_enpassant_move:
            self.board[move.start_row][move.end_col] = '--'  # capturing the pawn


        # update enpassant_possible variable
        if move.piece_moved[1] == 'P' and abs(move.start_row - move.end_row) == 2:  # only on 2-square pawn advances
            self.enpassant_possible = ((move.start_row + move.end_row)//2, move.start_col)
        else:
            self.enpassant_possible = ()

        self.enpassant_possible_logs.append(self.enpassant_possible)

        # castle move
        if move.is_castle_move:
            if move.end_col - move.start_col == 2:  # kingside castle
                self.board[move.end_row][move.end_col-1] = self.board[move.end_row][move.end_col+1]
                self.board[move.end_row][move.end_col+1] = '--'  # erase the old rook
            else:  # queenside castle
                self.board[move.end_row][move.end_col+1] = self.board[move.end_row][move.end_col-2]
                self.board[move.end_row][move.end_col-2] = '--'  # erase the old rook

        # update castling rights (whenever it is a king or rook move)
        self.update_castle_rights(move)
        self.castle_rights_log.append(CastlingRights(self.current_castling_right.wks, self.current_castling_right.bks, self.current_castling_right.wqs, self.current_castling_right.bqs))


    def undo_move(self):
        if len(self.move_log) !=0:  # make sure there is a move to undo
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move  # switch turns back

            # updating king move if needed
            if move.piece_moved == 'wK':
                self.white_king_location = (move.start_row, move.start_col)
            elif move.piece_moved == 'bK':
                self.black_king_location = (move.start_row, move.start_col)

            # undo an en-passant
            if move.is_enpassant_move:
                self.board[move.end_row][move.end_col] = '--'   # leave landing square blank
                self.board[move.start_row][move.end_col] = move.piece_captured

            self.enpassant_possible_logs.pop()
            self.enpassant_possible = self.enpassant_possible_logs[-1]

            # undo castling rights
            self.castle_rights_log.pop()  # getting rid of new castle rights
            new_rights = self.castle_rights_log[-1]
            self.current_castling_right = CastlingRights(new_rights.wks, new_rights.bks, new_rights.wqs, new_rights.bqs)

            # undo castle move
            if move.is_castle_move:
                if move.end_col - move.start_col == 2:  # kingside
                    self.board[move.end_row][move.end_col+1] = self.board[move.end_row][move.end_col-1]
                    self.board[move.end_row][move.end_col-1] = '--'
                else:  # queenside
                    self.board[move.end_row][move.end_col-2] = self.board[move.end_row][move.end_col+1]
                    self.board[move.end_row][move.end_col+1] = '--'

            # also
            self.checkmate = False
            self.stalemate = False

    def update_castle_rights(self, move):
        if move.piece_moved == 'wK':
            self.current_castling_right.wks = False
            self.current_castling_right.wqs = False
        elif move.piece_moved == 'bK':
            self.current_castling_right.bks = False
            self.current_castling_right.bqs = False
        elif move.piece_moved == 'wR':
            if move.start_row == 7:
                if move.start_col == 0:  # left rook
                    self.current_castling_right.wqs = False
                elif move.start_col == 7:  # right rook
                    self.current_castling_right.wks = False
        elif move.piece_moved == 'bR':
            if move.start_row == 0:
                if move.start_col == 0:  # left rook
                    self.current_castling_right.bqs = False
                elif move.start_col == 7:  # right rook
                    self.current_castling_right.bks = False

        # if a rook is captured
        if move.piece_captured == 'wR':
            if move.end_row == 7:
                if move.end_col == 0:
                    self.current_castling_right.wqs = False
                elif move.end_col == 7:
                    self.current_castling_right.wks = False
        elif move.piece_captured == 'bR':
            if move.end_row == 0:
                if move.end_col == 0:
                    self.current_castling_right.bqs = False
                elif move.end_col == 7:
                    self.current_castling_right.bks = False



    '''
    We will make a distinction between for all possible moves and all valid moves.
    So the basic algo for our get_valid_moves() will be:
    -->get all possible moves
    --> for each possible move, check to see if it is a valid move by:
        * make the move
        * generate all possible moves for the opposing player
        * see if any of the moves attack the king.
        * if your king is safe it is a valid move, add it to the list
        * return the list of valid moves only'''

    # all moves considering checks
    def get_valid_moves(self):
        #  for debugging
        '''for log in self.castle_rights_log:
            print(log.wks, log.wqs, log.bks, log.bqs, end=', ')
        print()'''

        temp_enpassant_possible = self.enpassant_possible
        temp_castle_rights = CastlingRights(self.current_castling_right.wks, self.current_castling_right.bks, self.current_castling_right.wqs, self.current_castling_right.bqs)  # copying the curent castling rights
        # Generate all possible move
        moves = self.get_all_possible_moves()  # it will generate king moves which will effect the castling rights
        if self.white_to_move:  # seperating castling moves from king moves to avoid recursion
            self.get_castle_moves(self.white_king_location[0], self.white_king_location[1], moves)
        else:
            self.get_castle_moves(self.black_king_location[0], self.black_king_location[1], moves)

        # for each move, make the move
        for i in range(len(moves)-1, -1, -1):  # when removing , go backwards to avoid missing something
            self.make_move(moves[i])

            # generate all opponent's move
            # for each opponent move see if they attack your king
            self.white_to_move = not self.white_to_move  # so that we are checking for our original player
            if self.in_check():
                moves.remove(moves[i])   # if king is under attack, not a valid move
            self.white_to_move = not self.white_to_move
            self.undo_move()

        if len(moves) == 0:  # either checkmate or stalemate
            if self.in_check():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        self.enpassant_possible = temp_enpassant_possible
        self.current_castling_right = temp_castle_rights
        return moves

    # determine if the current player is under check
    def in_check(self):
        if self.white_to_move:
            return self.square_under_attack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.square_under_attack(self.black_king_location[0], self.black_king_location[1])

    # if the enemy can attack square (r, c)
    def square_under_attack(self, r, c):
        self.white_to_move = not self.white_to_move #switch to opponent's
        oppo_moves = self.get_all_possible_moves()
        self.white_to_move = not self.white_to_move # to get to original player
        for move in oppo_moves:
            if move.end_row == r and move.end_col == c: #square is under attack
                return True
        return False

    #generating all possible moves
    def get_all_possible_moves(self):
        moves = []
        for r in range(len(self.board)): #number of rows
            for c in range(len(self.board[r])): #number of col in the given row
                turn = self.board[r][c][0]
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    piece = self.board[r][c][1]
                    self.move_functions[piece](r, c, moves)  # call the app move func
        return moves

    # get all the pawn moves and add these moves to the list
    def get_pawn_moves(self, r, c, moves):
        if self.white_to_move:  # white pawn moves
            if self.board[r-1][c] == '--':  # 1 square pawn advance
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == '--':  # 2 square pawn advance
                    moves.append(Move((r, c), (r-2, c), self.board))

            if c-1 >= 0:  # captures to the left
                if self.board[r-1][c-1][0] == 'b':  # enemy piece to capture
                    moves.append(Move((r, c), (r-1, c-1), self.board))
                elif (r-1, c-1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r-1, c-1), self.board, is_enpassant_move=True))

            if c+1 <= 7:  # capture to the right
                if self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c+1), self.board))
                elif (r-1, c+1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r-1, c+1), self.board, is_enpassant_move=True))

        else:  # black pawn moves
            if self.board[r+1][c] == '--':  # 1 square pawn move
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == '--':  # 2 square pawn move
                    moves.append(Move((r, c), (r+2, c), self.board))

            if c-1 >= 0:  # captures to the right
                if self.board[r+1][c-1][0] == 'w':  # enemy piece to capture
                    moves.append(Move((r, c), (r+1, c-1), self.board))
                elif (r+1, c-1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r+1, c-1), self.board, is_enpassant_move=True))

            if c+1 <= 7:  # capture to the left
                if self.board[r+1][c+1][0] == 'w':
                    moves.append(Move((r, c), (r+1, c+1), self.board))
                elif (r+1, c+1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r+1, c+1), self.board, is_enpassant_move=True))


    # get all the rook moves and add these moves to the list
    def get_rook_moves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up left down right
        enemy_color = 'b' if self.white_to_move else 'w'

        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i

                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]

                    if end_piece == '--':
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:  # for friendly piece
                        break
                else:  # off board
                    break

    # get all the knight moves and add these moves to the list
    def get_knight_moves(self, r, c, moves):
        knight_moves = ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1))
        ally_color = 'w' if self.white_to_move else 'b'
        for m in knight_moves:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:  # i.e empty or enemy
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    # get all the bishop moves and add these moves to the list
    def get_bishop_moves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemy_color = 'b' if self.white_to_move else 'w'

        for d in directions:
            for i in range(1, 8):  # can move max 7 squares
                end_row = r + d[0] * i
                end_col = c + d[1] * i

                if 0 <= end_row < 8 and 0 <= end_col < 8:  # its on the board
                    end_piece = self.board[end_row][end_col]

                    if end_piece == '--':
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:  # for friendly piece
                        break
                else:  # off board
                    break

    # get all the queen moves and add these moves to the list
    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

    # get all the king moves and add these moves to the list
    def get_king_moves(self, r, c, moves):
        king_moves = ((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1))
        allycolor = 'w' if self.white_to_move else 'b'
        for i in range(8):
            end_row = r + king_moves[i][0]
            end_col = c + king_moves[i][1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != allycolor:
                    moves.append(Move((r, c), (end_row, end_col), self.board))
                elif end_piece == '--':
                    moves.append(Move((r, c), (end_row, end_col), self.board))


    # generate all valid castle moves for king and add them to the list of moves
    def get_castle_moves(self, r, c, moves):
        if self.square_under_attack(r, c):
            return  # we can't castle while in check
        if (self.white_to_move and self.current_castling_right.wks) or (not self.white_to_move and self.current_castling_right.bks):
            self.get_kingside_castle_moves(r, c, moves)
        if (self.white_to_move and self.current_castling_right.wqs) or (not self.white_to_move and self.current_castling_right.bqs):
            self.get_queenside_castle_moves(r, c, moves)


    def get_kingside_castle_moves(self, r, c, moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.square_under_attack(r, c+1) and not self.square_under_attack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, is_castle_move=True))

    def get_queenside_castle_moves(self, r, c, moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.square_under_attack(r, c-1) and not self.square_under_attack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, is_castle_move=True))


class CastlingRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move:
    # map keys to values to make chess notation work in computer
    ranks_to_rows = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
    rows_to_ranks = {k: v for v, k in ranks_to_rows.items()}

    files_to_cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    cols_to_files = {k: v for v, k in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board, is_enpassant_move=False, is_castle_move=False):  # optional parameters
        self.start_sq = start_sq
        self.end_sq = end_sq
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]

        # en-passant
        self.is_enpassant_move = is_enpassant_move
        if self.is_enpassant_move:
            self.piece_captured = 'wP' if self.piece_moved == 'bP' else 'bP'

        # pawn promotion
        self.is_pawn_promotion = False
        if (self.piece_moved == 'wP' and self.end_row == 0) or (self.piece_moved == 'bP' and self.end_row == 7):
            self.is_pawn_promotion = True

        # castle move
        self.is_castle_move = is_castle_move

        self.move_ID = 1000*self.start_row + 100*self.start_col + 10*self.end_row + self.end_col

    # overriding the equals method
    # although the column is same it considers it as two diff objects
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_ID == other.move_ID
        return False

    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]

    # overridng the str() function
    def __str__(self):
        # castle move
        if self.is_castle_move:
            # 'O-O' king side castle
            # 'O-O-O' queen side castle
            return 'O-O' if self.end_col == 6 else 'O-O-O'

        #end_square = self.get_rank_file(self.end_row, self.end_col)
