import json
import tictactoe as ttt
import pygame
import sys
import time
from pathlib import Path


class GameState:
    MENU = 'menu'
    PLAYER_SELECTION = 'player_selection'
    GAME = 'game'
    GAME_OVER = 'game_over'
    SCORES = 'scores'

class Colors:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    BLUE = (87, 160, 211)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)
    PURPLE = (128, 0, 128)
    ORANGE = (255, 165, 0)
    GREY = (128, 128, 128)

class TicTacToeGame:

    def __init__(self):
        pygame.init()
        self.size = self.width, self.height = 800, 600
        self.screen = pygame.display.set_mode(self.size)

        self.mediumFont = pygame.font.Font("OpenSans-Regular.ttf", 28)
        self.largeFont = pygame.font.Font("OpenSans-Regular.ttf", 40)
        self.moveFont = pygame.font.Font("OpenSans-Regular.ttf", 60)

        # GameState
        self.game_mode = None  # None, "AI", "2P"
        self.user = None
        self.board = ttt.initial_state()
        self.ai_turn = False
        self.show_leaderboard = False
        self.state = GameState.MENU
        self.stats_updated = False

        # Player data
        self.data_folder = Path("game_data")
        self.data_file = self.data_folder / "player_stats.json"
        self.initialize_storage()
        self.current_players = {"X": None, "O": None}

        # Input box properties
        self.input_boxes = {
            "player1": pygame.Rect(self.width // 4, self.height // 3, 400, 40),
            "player2": pygame.Rect(self.width // 4, self.height // 2, 400, 40)
        }
        self.active_input = None
        self.input_texts = {"player1": "", "player2": ""}
        self.input_labels = {"player1": "Player 1 (X)", "player2": "Player 2 (O)"}

    def initialize_storage(self):
        """Initialize storage for player stats"""
        self.data_folder.mkdir(exist_ok=True)
        if not self.data_file.exists():
            initiated = {}
            with open(self.data_file, 'w') as f:
                json.dump(initiated, f)

    def load_stats(self):
        """Load player statistics"""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                if not data:  # Handle empty file case
                    return {}
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            # If file doesn't exist or is corrupted, create new one
            initial_data = {}
            with open(self.data_file, 'w') as f:
                json.dump(initial_data, f)
            return initial_data

    def save_stats(self, stats):
        """Save player stats to file .json"""
        with open(self.data_file, 'w') as f:
            json.dump(stats, f, indent=4)

    def draw_text(self, text, font, color, center):
        """Utility function to render text at a specific center."""
        rendered_text = font.render(text, True, color)
        rect = rendered_text.get_rect()
        rect.center = center
        self.screen.blit(rendered_text, rect)

    def update_player_stats(self, player_name, won=False, tied=False):
        """Update player statistics"""
        stats = self.load_stats()
        if player_name not in stats:
            stats[player_name] = {"wins": 0, "losses": 0, "ties": 0}

        if tied:
            stats[player_name]["ties"] += 1
            print("tie")
        elif won:
            stats[player_name]["wins"] += 1
            print("win")
        else:
            stats[player_name]["losses"] += 1
            print("loss")

        self.save_stats(stats)



    def handle_events(self):
        """Handle game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self.handle_click(mouse_pos)

                # Handle input box selection
                if self.state == GameState.PLAYER_SELECTION and self.game_mode == "2P":
                    self.active_input = None
                    for box_name, box in self.input_boxes.items():
                        if box.collidepoint(mouse_pos):
                            self.active_input = box_name

            elif event.type == pygame.KEYDOWN and self.active_input:
                if event.key == pygame.K_RETURN:
                    if self.input_texts["player1"] and self.input_texts["player2"]:
                        self.current_players["X"] = self.input_texts["player1"]
                        self.current_players["O"] = self.input_texts["player2"]
                        self.state = GameState.GAME
                elif event.key == pygame.K_BACKSPACE:
                    self.input_texts[self.active_input] = self.input_texts[self.active_input][:-1]
                else:
                    if len(self.input_texts[self.active_input]) < 15:  # Limit name length
                        self.input_texts[self.active_input] += event.unicode

    def handle_click(self, mouse_pos):
        """Handle mouse clicks based on game state"""
        if self.state == GameState.MENU:
            self.handle_menu_click(mouse_pos)
        elif self.state == GameState.PLAYER_SELECTION:
            self.handle_player_selection_click(mouse_pos)
        elif self.state == GameState.GAME:
            self.handle_game_click(mouse_pos)
        elif self.state == GameState.GAME_OVER:
            self.handle_game_over_click(mouse_pos)
        elif self.state == GameState.SCORES:
            self.handle_scores_click(mouse_pos)


    def handle_scores_click(self, mouse_pos):
        """Handle clicks in the scores state"""
        back_button = pygame.Rect(self.width // 2 - 100, self.height * 3 // 4, 200, 50)

        if back_button.collidepoint(mouse_pos):
            self.state = GameState.PLAYER_SELECTION
            self.show_leaderboard = False
            time.sleep(0.2)

    def handle_menu_click(self, mouse_pos):
        """Handle clicks in the menu state"""
        vs_ai_button = pygame.Rect(self.width // 4 - 100, self.height // 2, 200, 50)
        vs_player_button = pygame.Rect(3 * self.width // 4 - 100, self.height // 2, 200, 50)

        if vs_ai_button.collidepoint(mouse_pos):
            self.game_mode = "AI"
            self.state = GameState.PLAYER_SELECTION
            time.sleep(0.2)  # Prevent double clicks
        elif vs_player_button.collidepoint(mouse_pos):
            self.game_mode = "2P"
            self.show_leaderboard = False
            self.input_texts = {"player1": "", "player2": ""}
            self.state = GameState.PLAYER_SELECTION
            time.sleep(0.2)

    def handle_player_selection_click(self, mouse_pos):
        """Handle clicks in the player selection state"""
        play_x_button = pygame.Rect(self.width // 4 - 100, self.height // 2, 200, 50)
        play_o_button = pygame.Rect(3 * self.width // 4 - 100, self.height // 2, 200, 50)

        if self.game_mode == "AI":
            if play_x_button.collidepoint(mouse_pos):
                self.user = ttt.X
                self.current_players["X"] = 'Player'
                self.current_players["O"] = 'Computer'
                self.state = GameState.GAME
                time.sleep(0.2)
            elif play_o_button.collidepoint(mouse_pos):
                self.user = ttt.O
                self.current_players["X"] = "Computer"
                self.current_players["O"] = "Player"
                self.state = GameState.GAME
                time.sleep(0.2)


        elif self.game_mode == "2P":

            # Check if scores button is clicked
            scores_button = pygame.Rect(self.width // 1.5 - 100, self.height * 3 // 4, 200, 50)
            if scores_button.collidepoint(mouse_pos):
                self.state = GameState.SCORES
                time.sleep(0.2)

            # Check if start button is clicked
            start_button = pygame.Rect(self.width // 3 - 100, self.height * 3 // 4, 200, 50)
            if start_button.collidepoint(mouse_pos):
                if self.input_texts["player1"] and self.input_texts["player2"]:
                    self.current_players["X"] = self.input_texts["player1"]
                    self.current_players["O"] = self.input_texts["player2"]
                    self.state = GameState.GAME
                    time.sleep(0.2)

                else:
                    # Draw error message if names are not entered
                    message = "Please enter both player names to start"
                    msg_surface = self.mediumFont.render(message, True, Colors.RED)
                    msg_rect = msg_surface.get_rect(center=(self.width // 2, self.height // 2 + 60 ))
                    self.screen.blit(msg_surface, msg_rect)
                    pygame.display.flip()  # Update the display to show the message
                    time.sleep(1)  # Show the message for 1 second


    def handle_game_click(self, mouse_pos):
        """Handle clicks during gameplay"""
        if ttt.terminal(self.board):
            return

        # Calculate board positions
        tile_size = self.width // 6
        tile_origin = (self.width // 2 - (1.5 * tile_size),
                       self.height // 2 - (1.5 * tile_size))

        # Check if it's the player's turn
        current_player = ttt.player(self.board)
        if (self.game_mode == "AI" and current_player != self.user) or self.ai_turn:
            return

        # Check each tile
        for i in range(3):
            for j in range(3):
                rect = pygame.Rect(
                    tile_origin[0] + j * tile_size,
                    tile_origin[1] + i * tile_size,
                    tile_size, tile_size
                )
                if rect.collidepoint(mouse_pos) and self.board[i][j] == ttt.EMPTY:
                    self.board = ttt.result(self.board, (i, j))
                    # If in AI mode, set ai_turn to True
                    if self.game_mode == "AI":
                        self.ai_turn = True
                    return

    def handle_game_over_click(self, mouse_pos):
        """Handle clicks in the game over state"""
        play_again_button = pygame.Rect(self.width // 3 - 100, self.height - 65, 200, 50)
        main_menu_button = pygame.Rect(2 * self.width // 3 - 100, self.height - 65, 200, 50)

        if play_again_button.collidepoint(mouse_pos):
            # Reset the game but keep the same players and mode
            self.board = ttt.initial_state()
            self.ai_turn = False
            self.stats_updated = False
            self.state = GameState.GAME
            time.sleep(0.2)
        elif main_menu_button.collidepoint(mouse_pos):
            # Reset everything and go back to menu
            self.game_mode = None
            self.user = None
            self.board = ttt.initial_state()
            self.ai_turn = False
            self.show_leaderboard = False
            self.stats_updated = False
            self.current_players = {"X": None, "O": None}
            self.state = GameState.MENU
            time.sleep(0.2)

    def handle_game_result(self):
        """Determine game result and update stats"""
        winner = ttt.winner(self.board)
        if winner is None:
            message = "Game Over: Tie!"

            if self.game_mode == "2P" and not self.stats_updated:
                self.update_player_stats(self.current_players["X"], tied=True)
                self.update_player_stats(self.current_players["O"], tied=True)
                self.stats_updated = True
        else:
            if self.game_mode == "2P" and not self.stats_updated:
                winner_name = self.current_players[winner]
                loser_symbol = "O" if winner == "X" else "X"
                loser_name = self.current_players[loser_symbol]
                self.update_player_stats(winner_name, won=True)
                self.update_player_stats(loser_name, won=False)
                self.stats_updated = True
            message = f"Game Over: {self.current_players[winner]} wins!"
        return message
    #
    # def update(self):
    #     """Update game state"""
    #     if self.state == GameState.GAME:
    #         if self.game_mode == "AI" and not self.user == ttt.player(self.board) and not ttt.terminal(self.board):
    #             if self.ai_turn:
    #                 time.sleep(0.2)
    #                 move = ttt.minimax(self.board)
    #                 self.board = ttt.result(self.board, move)
    #                 self.ai_turn = False
    #             else:
    #                 time.sleep(0.2)
    #                 self.ai_turn = True

    def render(self):
        """Render game screen"""
        self.screen.fill(Colors.BLUE)

        if self.state == GameState.MENU:
            self.render_menu()
        elif self.state == GameState.PLAYER_SELECTION:
                # Check if the name has been entered for AI mode
            if self.game_mode == "AI" and self.input_texts["player1"]:
                self.player1_name = self.input_texts["player1"]
                self.player2_name = "AI"
                self.state = GameState.GAME
            self.render_player_selection()
        elif self.state == GameState.GAME:
            self.render_game()
        elif self.state == GameState.GAME_OVER:
            self.render_game_over()
        elif self.state == GameState.SCORES:
            self.render_scores()

    def render_menu(self):
        """Render main menu"""
        # Draw title
        title = self.largeFont.render("Play Tic-Tac-Toe", True, Colors.WHITE)
        title_rect = title.get_rect()
        title_rect.center = (self.width // 2, 50)
        self.screen.blit(title, title_rect)

        # Draw buttons
        self.draw_button("vs AI", (self.width // 4, self.height // 2))
        self.draw_button("2 Players", (3 * self.width // 4, self.height // 2))

    

    def render_player_selection(self):
        """Render player selection screen"""
        if self.game_mode == "AI":
            title = self.largeFont.render("Choose Your Side", True, Colors.WHITE)
            title_rect = title.get_rect(center=(self.width // 2, 50))
            self.screen.blit(title, title_rect)

            self.draw_button("Play as X", (self.width // 4, self.height // 2))
            self.draw_button("Play as O", (3 * self.width // 4, self.height // 2))
        else: # 2P
            title = self.largeFont.render("Enter Player Names", True, Colors.WHITE)
            title_rect = title.get_rect(center=(self.width // 2, 50))
            self.screen.blit(title, title_rect)

            # Draw input boxes and labels
            for box_name, box in self.input_boxes.items():
                color = Colors.WHITE if box_name == self.active_input else Colors.GREY
                pygame.draw.rect(self.screen, color, box, 2)

                # Draw label
                label = self.mediumFont.render(self.input_labels[box_name], True, Colors.WHITE)
                label_rect = label.get_rect(bottomleft=(box.left, box.top - 5))
                self.screen.blit(label, label_rect)

                # Draw input text
                text_surface = self.mediumFont.render(self.input_texts[box_name], True, Colors.WHITE)
                self.screen.blit(text_surface, (box.x + 5, box.y + 5))

            # Draw start button if both names are entered
            #if self.input_texts["player1"] and self.input_texts["player2"]:
            self.draw_button("Start Game", (self.width // 3, self.height * 3 // 4))

            # Draw scores button to see the top rankings
            self.draw_button("Scores", (self.width // 1.5, self.height * 3 // 4))



    def render_game(self):
        """Render game board"""
        # Draw game board
        tile_size = self.width // 6
        tile_origin = (self.width // 2 - (1.5 * tile_size),
                       self.height // 2 - (1.5 * tile_size))
        tiles = []
        for i in range(3):
            row = []
            for j in range(3):
                rect = pygame.Rect(
                    tile_origin[0] + j * tile_size,
                    tile_origin[1] + i * tile_size,
                    tile_size, tile_size
                )
                pygame.draw.rect(self.screen, Colors.WHITE, rect, 3)

                if self.board[i][j] != ttt.EMPTY:
                    move = self.moveFont.render(self.board[i][j], True, Colors.WHITE)
                    move_rect = move.get_rect()
                    move_rect.center = rect.center
                    self.screen.blit(move, move_rect)
                row.append(rect)
            tiles.append(row)

        # Draw game status
        if ttt.terminal(self.board):
            self.state = GameState.GAME_OVER
        else:
            player = ttt.player(self.board)
            player_name = self.current_players[ttt.player(self.board)]
            if self.game_mode == "2P":
                status = f"Player {player_name}'s Turn"
            else:
                status = "Your Turn" if player == self.user else "Computer Thinking..."

            status_text = self.largeFont.render(status, True, Colors.WHITE)
            status_rect = status_text.get_rect()
            status_rect.center = (self.width // 2, 30)
            self.screen.blit(status_text, status_rect)

        if self.state == GameState.GAME:
            if self.game_mode == "AI" and not self.user == ttt.player(self.board) and not ttt.terminal(self.board):
                if self.ai_turn:
                    time.sleep(0.2)
                    move = ttt.minimax(self.board)
                    self.board = ttt.result(self.board, move)
                    self.ai_turn = False
                else:
                    time.sleep(0.2)
                    self.ai_turn = True

    def render_game_over(self):
        """Render game over screen"""
        print("Rendering game over...")
        self.render_game()  # Show final board state

        print("Print game result message: ")
        message = self.handle_game_result()
        message_text = self.largeFont.render(message, True, Colors.WHITE)
        message_rect = message_text.get_rect()
        message_rect.center = (self.width / 2, 30)
        self.screen.blit(message_text, message_rect)

        # Draw leaderboard
        self.render_leaderboard(self.width // 2, self.height // 2)

        # Draw buttons
        self.draw_button("Play Again", (self.width // 3, self.height - 65))
        self.draw_button("Main Menu", (2 * self.width // 3, self.height - 65))

    def render_leaderboard(self, x, y):
        """Render leaderboard"""
        if not self.show_leaderboard:
            return

        stats = self.load_stats()

        # Sort players by score (wins * 3 + ties)
        players = []
        for name, data in stats.items():
            if not isinstance(data, dict):
                continue  # Skip invalid entries
            wins = int(data.get("wins", 0))  # Default to 0 if key is missing
            #ties = int(data.get("ties", 0))  # Default to 0 if key is missing
            #losses = int(data.get("losses", 0))  # Default to 0 if key is missing
            #score = wins
            players.append((name, wins))
        players.sort(key=lambda x: x[1], reverse=True)

        # Draw top 10 players
        for i, (name, wins) in enumerate(players[:10]):
            ranking_text = f"{i + 1}. {name}: {wins} Wins"
            player_text = self.mediumFont.render(ranking_text, True, Colors.WHITE)
            text_rect = player_text.get_rect(center=(x, y + i * 30))
            self.screen.blit(player_text, text_rect)


    def render_scores(self):
        """Render the scores screen with the leaderboard."""
        # Draw heading
        heading = self.largeFont.render("Top Rankings", True, Colors.WHITE)
        heading_rect = heading.get_rect(center=(self.screen.get_width() // 2, 100))
        self.screen.blit(heading, heading_rect)

        # Render leaderboard
        self.show_leaderboard = True
        self.render_leaderboard(self.width // 2, 150)

        # Draw a back button
        self.draw_button("Back", (self.width // 2, self.height * 3 // 4))


    def draw_button(self, text, pos, size=(200, 50), border_radius=20):
        """Helper method to draw buttons"""
        button = pygame.Rect(pos[0] - size[0] // 2, pos[1], size[0], size[1])
        pygame.draw.rect(self.screen, Colors.WHITE, button, border_radius=border_radius)

        text_surface = self.mediumFont.render(text, True, Colors.BLACK)
        text_rect = text_surface.get_rect(center=button.center)
        self.screen.blit(text_surface, text_rect)

        return button



    def run(self):
        """Main game loop"""
        while True:
            self.handle_events()
            #self.update()
            self.render()
            pygame.display.flip()

if __name__ == "__main__":
    game = TicTacToeGame()
    game.run()