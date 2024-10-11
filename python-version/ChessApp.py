import tkinter as tk
from PIL import Image, ImageTk
from cairosvg import svg2png
import os

class ChessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Game")
        
        self.window_size = 640
        self.board_size = 8  # 8x8 grid
        self.square_size = self.window_size // self.board_size

        self.canvas = tk.Canvas(self.root, width=self.window_size, height=self.window_size)
        self.canvas.pack()

        self.selected_piece = None  # Store the currently selected piece
        self.piece_positions = {}  # Store positions of pieces
        self.valid_moves = []  # Store valid moves for highlighting
        self.turn = 'w'  # White starts the game
        self.move_history = []  # Store piece move history

        self.load_piece_images()
        self.draw_board()
        self.place_pieces()

        self.canvas.bind("<Button-1>", self.on_square_click)

    def draw_board(self):
        """Draw the chessboard with alternating colors."""
        for row in range(self.board_size):
            for col in range(self.board_size):
                color = "#DDB88C" if (row + col) % 2 == 0 else "#A66D4F"  # Light and dark squares
                x1 = col * self.square_size
                y1 = row * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)

        # Highlight valid moves
        for col, row in self.valid_moves:
            x1 = col * self.square_size
            y1 = row * self.square_size
            x2 = x1 + self.square_size
            y2 = y1 + self.square_size
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="blue", width=3)

    def load_piece_images(self):
        """Load SVG chess pieces and convert to PNG for display."""
        self.piece_images = {}
        pieces = ['pawn', 'knight', 'bishop', 'rook', 'queen', 'king']
        colors = ['w', 'b']

        for piece in pieces:
            for color in colors:
                filename = f"pieces/{piece}-{color}.svg"
                png_image = f"pieces/{piece}-{color}.png"
                
                if not os.path.exists(png_image):
                    with open(filename, 'rb') as svg_file:
                        svg_data = svg_file.read()
                    png_data = svg2png(bytestring=svg_data, output_width=80, output_height=80)
                    with open(png_image, 'wb') as png_file:
                        png_file.write(png_data)
                
                image = Image.open(png_image)
                self.piece_images[f"{piece}-{color}"] = ImageTk.PhotoImage(image.resize((80, 80)))

    def place_pieces(self):
        """Place the initial chess pieces on the board."""
        initial_positions = {
            "rook": [("rook-w", 0, 7), ("rook-w", 7, 7), ("rook-b", 0, 0), ("rook-b", 7, 0)],
            "knight": [("knight-w", 1, 7), ("knight-w", 6, 7), ("knight-b", 1, 0), ("knight-b", 6, 0)],
            "bishop": [("bishop-w", 2, 7), ("bishop-w", 5, 7), ("bishop-b", 2, 0), ("bishop-b", 5, 0)],
            "queen": [("queen-w", 3, 7), ("queen-b", 3, 0)],
            "king": [("king-w", 4, 7), ("king-b", 4, 0)],
            "pawn": [("pawn-w", i, 6) for i in range(8)] + [("pawn-b", i, 1) for i in range(8)],
        }

        for piece, positions in initial_positions.items():
            for p, col, row in positions:
                self.piece_positions[(col, row)] = p
                self.draw_piece(p, col, row)

    def draw_piece(self, piece, col, row):
        """Draw a piece at the specified board position."""
        piece_size = 80
        offset = (self.square_size - piece_size) // 2
        x = col * self.square_size + offset
        y = row * self.square_size + offset
        self.canvas.create_image(x, y, image=self.piece_images[piece], anchor=tk.NW)

    def on_square_click(self, event):
        """Handle clicking on a square to select and move a piece."""
        col = event.x // self.square_size
        row = event.y // self.square_size

        if self.selected_piece:
            if (col, row) in self.valid_moves:
                self.move_piece(self.selected_piece, col, row)
                self.turn = 'b' if self.turn == 'w' else 'w'
            self.selected_piece = None
            self.valid_moves = []
        else:
            if (col, row) in self.piece_positions:
                piece_color = self.piece_positions[(col, row)].split('-')[1]
                if piece_color == self.turn:
                    self.selected_piece = (col, row)
                    self.valid_moves = self.get_valid_moves(col, row)

        self.canvas.delete("all")
        self.draw_board()
        for (c, r), p in self.piece_positions.items():
            self.draw_piece(p, c, r)

    def move_piece(self, from_pos, to_col, to_row):
        """Move a piece from one square to another."""
        piece = self.piece_positions.get(from_pos)

        if piece:
            del self.piece_positions[from_pos]
            self.piece_positions[(to_col, to_row)] = piece
            self.move_history.append((from_pos, (to_col, to_row)))

    def get_valid_moves(self, col, row):
        """Determine the valid moves for the piece at the given position."""
        piece = self.piece_positions.get((col, row))
        if not piece:
            return []

        valid_moves = []
        piece_type, color = piece.split('-')
        
        if piece_type == "pawn":
            valid_moves = self.get_pawn_moves(col, row, color)
        elif piece_type == "rook":
            valid_moves = self.get_rook_moves(col, row, color)
        elif piece_type == "knight":
            valid_moves = self.get_knight_moves(col, row)
        elif piece_type == "bishop":
            valid_moves = self.get_bishop_moves(col, row, color)
        elif piece_type == "queen":
            valid_moves = self.get_queen_moves(col, row, color)
        elif piece_type == "king":
            valid_moves = self.get_king_moves(col, row, color)

        valid_moves = self.remove_blocked_moves(col, row, valid_moves, color)
        return valid_moves

    def remove_blocked_moves(self, col, row, moves, color):
        """Remove moves blocked by own pieces and stop at opponent pieces."""
        valid_moves = []

        # Sort moves into 8 directions for handling long-range pieces (bishop, rook, queen)
        directions = {
        'up': [], 'down': [], 'left': [], 'right': [], 
        'up-right': [], 'up-left': [], 'down-right': [], 'down-left': []
        }

        for c, r in moves:
            if c > col and r == row:
                directions['right'].append((c, r))
            elif c < col and r == row:
                directions['left'].append((c, r))
            elif c == col and r > row:
                directions['down'].append((c, r))
            elif c == col and r < row:
                directions['up'].append((c, r))
            elif c > col and r > row:
                directions['down-right'].append((c, r))
            elif c < col and r > row:
                directions['down-left'].append((c, r))
            elif c > col and r < row:
                directions['up-right'].append((c, r))
            elif c < col and r < row:
                directions['up-left'].append((c, r))
        # Check each direction for obstructions
        for dir_moves in directions.values():
            for c, r in dir_moves:
                if (c, r) in self.piece_positions:
                    piece_at_target = self.piece_positions[(c, r)]
                    piece_color = piece_at_target.split('-')[1]
                    if piece_color != color:
                        valid_moves.append((c, r))  # Capture opponent's piece
                    break  # Stop if any piece blocks further movement
                valid_moves.append((c, r))
            
        return valid_moves

    def get_pawn_moves(self, col, row, color):
        """Get pawn's valid moves including the initial two-square move."""
        direction = -1 if color == 'w' else 1
        start_row = 6 if color == 'w' else 1
        moves = []

        if (col, row + direction) not in self.piece_positions:
            moves.append((col, row + direction))  # Single move forward

            if row == start_row and (col, row + 2 * direction) not in self.piece_positions:
                moves.append((col, row + 2 * direction))  # Double move forward

        # Capture diagonally
        for offset in [-1, 1]:
            if (col + offset, row + direction) in self.piece_positions:
                target_piece = self.piece_positions[(col + offset, row + direction)]
                if target_piece.split('-')[1] != color:
                    moves.append((col + offset, row + direction))

        return moves

    def get_rook_moves(self, col, row, color):
        """Get rook's valid moves."""
        moves = []

        # Horizontal and vertical moves
        for i in range(1, self.board_size):
            moves.append((col + i, row))  # Right
            moves.append((col - i, row))  # Left
            moves.append((col, row + i))  # Up
            moves.append((col, row - i))  # Down

        return moves

    def get_knight_moves(self, col, row):
        """Get knight's valid moves."""
        moves = [
            (col + 2, row + 1), (col + 2, row - 1),
            (col - 2, row + 1), (col - 2, row - 1),
            (col + 1, row + 2), (col + 1, row - 2),
            (col - 1, row + 2), (col - 1, row - 2)
        ]
        return moves

    def get_bishop_moves(self, col, row, color):
        """Get bishop's valid moves."""
        moves = []
        for i in range(1, self.board_size):
            moves.append((col + i, row + i))  # Down-right
            moves.append((col - i, row + i))  # Down-left
            moves.append((col + i, row - i))  # Up-right
            moves.append((col - i, row - i))  # Up-left
        return moves

    def get_queen_moves(self, col, row, color):
        """Get queen's valid moves (combination of rook and bishop)."""
        return self.get_rook_moves(col, row, color) + self.get_bishop_moves(col, row, color)

    def get_king_moves(self, col, row, color):
        """Get king's valid moves."""
        moves = [
            (col + 1, row), (col - 1, row), (col, row + 1), (col, row - 1),
            (col + 1, row + 1), (col + 1, row - 1), (col - 1, row + 1), (col - 1, row - 1)
        ]
        return moves


if __name__ == "__main__":
    root = tk.Tk()
    app = ChessApp(root)
    root.mainloop()
