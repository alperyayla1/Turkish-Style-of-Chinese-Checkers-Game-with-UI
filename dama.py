import tkinter as tk
from typing import List, Tuple, Optional

class TurkishChineseCheckers:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Turkish Chinese Checkers - 2 Players")
        self.HIGHLIGHT_COLOR = "green"
        self.STAY_COLOR = "yellow"
        self.BOARD_SIZE = 600
        self.SQUARE_SIZE = 60
        self.PIECE_RADIUS = 25
        self.COLORS = {1: "#FF0000", 2: "#0000FF"}  # Red (Player 1), Blue (Player 2)
        self.all_pieces_moved = {1: False, 2: False}

        self.selected_piece = None
        self.current_player = 1
        self.board = self.initialize_board()
        self.jump_in_progress = False
        self.jumped_positions = set()
        self.pieces_moved = {1: set(), 2: set()}  # Track pieces that have left starting area

        self.canvas = tk.Canvas(self.root, width=self.BOARD_SIZE, height=self.BOARD_SIZE, bg="white")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.handle_click)

        self.turn_label = tk.Label(self.root, text="Player 1's Turn (Red)", font=("Arial", 14))
        self.turn_label.pack()

        self.draw_board()

    def initialize_board(self) -> dict:
        board = {(row, col): None for row in range(8) for col in range(8)}
        for row in range(3):
            for col in range(5, 8):
                board[(row, col)] = 1
        for row in range(5, 8):
            for col in range(3):
                board[(row, col)] = 2
        return board

    def get_valid_moves(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        if pos not in self.board or self.board[pos] is None:
            return []

        valid_moves = []
        player = self.board[pos]
        directions = self.get_allowed_directions(pos, player)

        # Single step moves (only if not in a jump sequence)
        if not self.jump_in_progress:
            for dx, dy in directions:
                new_pos = (pos[0] + dx, pos[1] + dy)
                if self.is_valid_position(new_pos) and self.board[new_pos] is None:
                    if self.is_valid_move(pos, new_pos, player):
                        valid_moves.append(new_pos)

        # Jump moves
        for dx, dy in directions:
            jump_over = (pos[0] + dx, pos[1] + dy)
            jump_to = (pos[0] + 2 * dx, pos[1] + 2 * dy)
            if (self.is_valid_position(jump_over) and self.is_valid_position(jump_to) and
                    self.board[jump_over] is not None and self.board[jump_to] is None and
                    jump_over not in self.jumped_positions):
                if self.is_valid_move(pos, jump_to, player):
                    valid_moves.append(jump_to)

        return valid_moves

    def get_allowed_directions(self, pos: Tuple[int, int], player: int) -> List[Tuple[int, int]]:
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # Allow all directions
        return directions

    def is_valid_position(self, pos: Tuple[int, int]) -> bool:
        return 0 <= pos[0] < 8 and 0 <= pos[1] < 8

    def is_in_opponent_area(self, pos: Tuple[int, int], player: int) -> bool:
        row, col = pos
        return (row >= 5 and col <= 2) if player == 1 else (row <= 2 and col >= 5)

    def is_in_starting_area(self, pos: Tuple[int, int], player: int) -> bool:
        row, col = pos
        return (row <= 2 and col >= 5) if player == 1 else (row >= 5 and col <= 2)

    def all_pieces_left_starting_area(self, player: int) -> bool:
        for row in range(8):
            for col in range(8):
                if self.board[(row, col)] == player and self.is_in_starting_area((row, col), player):
                    return False
        return True

    def is_in_opponent_starting_area(self, pos: Tuple[int, int], player: int) -> bool:
        row, col = pos
        return (row >= 5 and col <= 2) if player == 1 else (row <= 2 and col >= 5)

    def is_valid_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], player: int) -> bool:
        dx, dy = to_pos[0] - from_pos[0], to_pos[1] - from_pos[1]

        # Check if the move is backwards
        is_backwards = (player == 1 and (dx < 0 or dy > 0)) or (player == 2 and (dx > 0 or dy < 0))

        if is_backwards:
            # Allow backwards move only if all pieces have left starting area and the piece is in opponent's starting area
            if self.all_pieces_moved[player] and self.is_in_opponent_starting_area(from_pos, player):
                return True
            else:
                return False

        return True

    def perform_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]):
        player = self.board[from_pos]
        self.board[to_pos] = self.board[from_pos]
        self.board[from_pos] = None

        # Check if all pieces have left the starting area
        if not self.all_pieces_moved[player] and self.all_pieces_left_starting_area(player):
            self.all_pieces_moved[player] = True

        # Check if it's a jump move
        if abs(from_pos[0] - to_pos[0]) == 2 or abs(from_pos[1] - to_pos[1]) == 2:
            jumped_pos = ((from_pos[0] + to_pos[0]) // 2, (from_pos[1] + to_pos[1]) // 2)
            self.jumped_positions.add(jumped_pos)
            self.jump_in_progress = True
            self.selected_piece = to_pos
            if not self.get_valid_moves(to_pos):
                self.end_turn()
        else:
            self.end_turn()

        self.draw_board()

    def handle_click(self, event):
        if self.check_winner():
            return

        col = (event.x - 50) // self.SQUARE_SIZE
        row = (event.y - 50) // self.SQUARE_SIZE
        pos = (row, col)

        if not self.is_valid_position(pos):
            return

        if self.selected_piece is None:
            if pos in self.board and self.board[pos] == self.current_player:
                self.selected_piece = pos
                self.draw_board()
        else:
            valid_moves = self.get_valid_moves(self.selected_piece)
            if pos in valid_moves:
                self.perform_move(self.selected_piece, pos)
            elif pos == self.selected_piece and self.jump_in_progress:
                self.end_turn()  # Allow staying after a jump
            else:
                self.selected_piece = None
                self.draw_board()

    def end_turn(self):
        self.current_player = 3 - self.current_player
        self.selected_piece = None
        self.jump_in_progress = False
        self.jumped_positions.clear()
        self.turn_label.config(
            text=f"Player {self.current_player}'s Turn ({'Red' if self.current_player == 1 else 'Blue'})")
        self.draw_board()

    def check_winner(self) -> Optional[int]:
        red_win = all(self.board.get((row, col)) == 1 for row in range(5, 8) for col in range(3))
        blue_win = all(self.board.get((row, col)) == 2 for row in range(3) for col in range(5, 8))
        if red_win:
            self.turn_label.config(text="Game Over! Player 1 (Red) wins!")
            return 1
        elif blue_win:
            self.turn_label.config(text="Game Over! Player 2 (Blue) wins!")
            return 2
        return None

    def draw_board(self):
        self.canvas.delete("all")
        for row in range(8):
            for col in range(8):
                x1 = col * self.SQUARE_SIZE + 50
                y1 = row * self.SQUARE_SIZE + 50
                x2 = x1 + self.SQUARE_SIZE
                y2 = y1 + self.SQUARE_SIZE
                color = "#FFFFFF" if (row + col) % 2 == 0 else "#808080"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

                piece = self.board.get((row, col))
                if piece is not None:
                    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                    self.canvas.create_oval(cx - self.PIECE_RADIUS, cy - self.PIECE_RADIUS,
                                            cx + self.PIECE_RADIUS, cy + self.PIECE_RADIUS,
                                            fill=self.COLORS[piece], outline="black")

        if self.selected_piece:
            valid_moves = self.get_valid_moves(self.selected_piece)
            for move in valid_moves:
                col, row = move[1], move[0]
                cx = col * self.SQUARE_SIZE + 50 + self.SQUARE_SIZE // 2
                cy = row * self.SQUARE_SIZE + 50 + self.SQUARE_SIZE // 2
                self.canvas.create_oval(cx - self.PIECE_RADIUS, cy - self.PIECE_RADIUS,
                                        cx + self.PIECE_RADIUS, cy + self.PIECE_RADIUS,
                                        outline=self.HIGHLIGHT_COLOR, width=2)

        self.root.update()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = TurkishChineseCheckers()
    game.run()