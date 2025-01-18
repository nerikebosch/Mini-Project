import pygame
import sys
import time
import tictactoe as ttt  # Assuming ttt contains the game logic.

class TicTacToeGame:
    def __init__(self):
        pygame.init()
        self.size = self.width, self.height = 600, 400
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)
        self.screen = pygame.display.set_mode(self.size)
        self.mediumFont = pygame.font.Font("OpenSans-Regular.ttf", 28)
        self.largeFont = pygame.font.Font("OpenSans-Regular.ttf", 40)
        self.moveFont = pygame.font.Font("OpenSans-Regular.ttf", 60)

        self.game_mode = None  # None, "AI", "2P"
        self.user = None
        self.board = ttt.initial_state()
        self.ai_turn = False
        self.running = True

    def draw_text(self, text, font, color, center):
        """Utility function to render text at a specific center."""
        rendered_text = font.render(text, True, color)
        rect = rendered_text.get_rect()
        rect.center = center
        self.screen.blit(rendered_text, rect)

    def draw_button(self, text, rect, color, text_color):
        """Utility function to draw a button."""
        pygame.draw.rect(self.screen, color, rect)
        self.draw_text(text, self.mediumFont, text_color, rect.center)
        return rect

    def handle_menu(self):
        """Handle the main menu for game mode selection."""
        self.draw_text("Play Tic-Tac-Toe", self.largeFont, self.white, (self.width // 2, 50))

        vsAIButton = pygame.Rect(1.5 * (self.width / 8), self.height / 2, self.width / 4, 50)
        play2Button = pygame.Rect(4.5 * (self.width / 8), self.height / 2, self.width / 4, 50)

        self.draw_button("vs AI", vsAIButton, self.white, self.black)
        self.draw_button("2 Players", play2Button, self.white, self.black)

        click, _, _ = pygame.mouse.get_pressed()
        if click == 1:
            mouse = pygame.mouse.get_pos()
            if vsAIButton.collidepoint(mouse):
                time.sleep(0.2)
                self.game_mode = "AI"
            elif play2Button.collidepoint(mouse):
                time.sleep(0.2)
                self.game_mode = "2P"
                self.user = ttt.X

    def handle_ai_selection(self):
        """Handle the selection of X or O for AI mode."""
        self.draw_text("Play Tic-Tac-Toe vs AI", self.largeFont, self.white, (self.width // 2, 50))

        playXButton = pygame.Rect(self.width / 8, self.height / 2, self.width / 4, 50)
        playOButton = pygame.Rect(5 * (self.width / 8), self.height / 2, self.width / 4, 50)

        self.draw_button("Play as X", playXButton, self.white, self.black)
        self.draw_button("Play as O", playOButton, self.white, self.black)

        click, _, _ = pygame.mouse.get_pressed()
        if click == 1:
            mouse = pygame.mouse.get_pos()
            if playXButton.collidepoint(mouse):
                time.sleep(0.2)
                self.user = ttt.X
            elif playOButton.collidepoint(mouse):
                time.sleep(0.2)
                self.user = ttt.O

    def draw_board(self):
        """Draw the game board and handle moves."""
        tile_size = 80
        tile_origin = (self.width / 2 - (1.5 * tile_size), self.height / 2 - (1.5 * tile_size))
        tiles = []

        for i in range(3):
            row = []
            for j in range(3):
                rect = pygame.Rect(
                    tile_origin[0] + j * tile_size,
                    tile_origin[1] + i * tile_size,
                    tile_size, tile_size
                )
                pygame.draw.rect(self.screen, self.white, rect, 3)

                if self.board[i][j] != ttt.EMPTY:
                    self.draw_text(self.board[i][j], self.moveFont, self.white, rect.center)
                row.append(rect)
            tiles.append(row)

        return tiles

    def handle_game(self):
        """Handle the main game logic."""
        tiles = self.draw_board()
        game_over = ttt.terminal(self.board)
        player = ttt.player(self.board)

        # Display game status
        if game_over:
            winner = ttt.winner(self.board)
            status = "Game Over: Tie." if winner is None else f"Game Over: {winner} wins."
        else:
            status = f"Player {player}'s turn" if self.game_mode == "2P" else \
                f"Computer thinking..." if self.user != player else f"Play as {self.user}"
        self.draw_text(status, self.largeFont, self.white, (self.width // 2, 30))

        # AI move
        if self.game_mode == "AI" and self.user != player and not game_over:
            if self.ai_turn:
                time.sleep(0.5)
                move = ttt.minimax(self.board)
                self.board = ttt.result(self.board, move)
                self.ai_turn = False
            else:
                self.ai_turn = True

        # User move
        click, _, _ = pygame.mouse.get_pressed()
        if click == 1 and not game_over:
            mouse = pygame.mouse.get_pos()
            for i in range(3):
                for j in range(3):
                    if self.board[i][j] == ttt.EMPTY and tiles[i][j].collidepoint(mouse):
                        self.board = ttt.result(self.board, (i, j))

        # Restart button
        if game_over:
            againButton = pygame.Rect(self.width / 3, self.height - 65, self.width / 3, 50)
            self.draw_button("Play Again", againButton, self.white, self.black)
            if click == 1:
                mouse = pygame.mouse.get_pos()
                if againButton.collidepoint(mouse):
                    time.sleep(0.2)
                    self.reset_game()

    def reset_game(self):
        """Reset the game state."""
        self.game_mode = None
        self.user = None
        self.board = ttt.initial_state()
        self.ai_turn = False

    def run(self):
        """Main game loop."""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.screen.fill(self.black)

            if self.game_mode is None:
                self.handle_menu()
            elif self.user is None and self.game_mode == "AI":
                self.handle_ai_selection()
            else:
                self.handle_game()

            pygame.display.flip()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = TicTacToeGame()
    game.run()
