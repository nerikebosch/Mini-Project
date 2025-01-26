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
    SETTINGS = 'settings'

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

class ThemeManager:
    def __init__(self, theme_file="game_data/theme.json", default_theme="Classic"):
        self.theme_file = theme_file
        self.themes = {}
        self.current_theme = default_theme
        self.load_themes()
        self.load_current_theme()
        
    def load_themes(self):
        themes_path = Path(self.theme_file)  # Path to the JSON file
        try:
            with themes_path.open("r") as f:
                self.themes = json.load(f)
        except FileNotFoundError:
            print(f"{themes_path} file not found. Using default themes.")
            return {
                "Classic": {
                    "background": [30, 30, 30],
                    "grid_color": [255, 255, 255],
                    "x_color": [200, 0, 0],
                    "o_color": [0, 0, 200],
                    "font_color": [255, 255, 255],
                    "button_color": [50, 50, 50],
                    "button_text_color": [255, 255, 255],
                }
            }
        
    def save_theme(self):
        """Save the currently selected theme."""
        with open("theme.json", "w") as f:
            json.dump({"current_theme": self.current_theme}, f)

    def load_current_theme(self):
        """Load the currently selected theme from a save file."""
        try:
            with open("theme.json", "r") as f:
                self.current_theme = json.load(f).get("current_theme", "Classic")
        except FileNotFoundError:
            print("Theme save file not found. Defaulting to 'Classic'.")

    def load_theme(self):
        try:
            with open("theme.json", "r") as f:
                self.current_theme = json.load(f).get("current_theme", "Classic")
        except FileNotFoundError:
            self.current_theme = "Classic"  # Default to "Classic" if the file is missing


    def apply_theme(self):
        self.screen.fill(self.themes[self.current_theme]["background"])
        self.draw_grid()
        self.update_game_state()

    def get_theme(self):
        """Get the active theme data."""
        return self.themes.get(self.current_theme, self.themes.get("Classic", {}))

class StorageManager:
    def __init__(self, data_folder="game_data"):
        self.data_folder = Path(data_folder)
        self.data_file = self.data_folder / "player_stats.json"
        self.initialize_storage()
        
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
    
class Renderer:
    def __init__(self, game, screen, theme_manager, fonts, state=GameState.MENU):
        self.screen = screen
        self.theme_manager = theme_manager 
        self.fonts = fonts
        self.game = game
        self.state = self.game.state

    def render(self):
        """Render game screen"""
        theme = self.theme_manager.get_theme()
        self.screen.fill(theme["background"])  # Use theme background color

        if self.game.state == GameState.MENU:
            
            self.render_menu()
        elif self.game.state == GameState.PLAYER_SELECTION:
                # Check if the name has been entered for AI mode
            if self.game.game_mode == "AI" and self.game.input_texts["player1"]:
                self.player1_name = self.game.input_texts["player1"]
                self.player2_name = "AI"
                self.game.state = GameState.GAME
            self.render_player_selection()
        elif self.game.state == GameState.GAME:
            self.render_game()
        elif self.game.state == GameState.GAME_OVER:
            self.render_game_over()
        elif self.game.state == GameState.SCORES:
            self.render_scores()
        elif self.game.state == GameState.SETTINGS:
            self.render_settings()

    def draw_text(self, text, font, color, center):
        """Utility function to render text at a specific center."""
        rendered_text = font.render(text, True, color)
        rect = rendered_text.get_rect()
        rect.center = center
        self.screen.blit(rendered_text, rect)

    def draw_button(self, text, pos, size=(200, 50), border_radius=20):
        """Helper method to draw buttons"""
        theme = self.theme_manager.get_theme()
        button_color = theme["button_color"]
        text_color = theme["button_text_color"]

        button = pygame.Rect(pos[0] - size[0] // 2, pos[1], size[0], size[1])
        pygame.draw.rect(self.screen, button_color, button, border_radius=border_radius)

        text_surface = self.fonts.mediumFont.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=button.center)
        self.screen.blit(text_surface, text_rect)

        return button
    
    def render_menu(self):
        """Render main menu"""
        theme = self.theme_manager.get_theme()
        # Draw title
        title = self.fonts.largeFont.render("Play Tic-Tac-Toe", True, theme["font_color"])
        title_rect = title.get_rect()
        title_rect.center = (self.game.width // 2, 50)
        self.screen.blit(title, title_rect)

        # Draw buttons
        self.draw_button("vs AI", (self.game.width // 4, self.game.height // 2))
        self.draw_button("2 Players", (3 * self.game.width // 4, self.game.height // 2))
        self.draw_button("Settings", (self.game.width // 4, self.game.height // 6))

    def render_settings(self):
        # Use the theme dictionary loaded from JSON
        theme = self.theme_manager.get_theme()
        self.screen.fill(theme["background"])  # Set background color

        # Heading
        heading = self.fonts.largeFont.render("Settings", True, theme["font_color"])
        heading_rect = heading.get_rect(center=(self.game.width // 2, 50))
        self.screen.blit(heading, heading_rect)

        # Theme buttons
        y_offset = 150
        for theme_name in self.theme_manager.themes.keys():
            # Draw button for each theme
            button = self.draw_button(
                theme_name,
                (self.game.width // 2, y_offset),
                size=(200, 50)
            )

            # Check if the button is clicked
            if button.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                self.theme_manager.current_theme = theme_name  # Update current theme
                self.theme_manager.save_theme()  # Save the selected theme to the JSON file

            y_offset += 70

        # Back button
        self.draw_button("Back", (self.game.width // 2, self.game.height * 3 // 4))

    def render_player_selection(self):
        """Render player selection screen"""
        theme = self.theme_manager.get_theme()

        if self.game.game_mode == "AI":
            title = self.fonts.largeFont.render("Choose Your Side", True, theme["font_color"])
            title_rect = title.get_rect(center=(self.game.width // 2, 50))
            self.screen.blit(title, title_rect)

            self.draw_button("Play as X", (self.game.width // 4, self.game.height // 2))
            self.draw_button("Play as O", (3 * self.game.width // 4, self.game.height // 2))
        else: # 2P
            title = self.fonts.largeFont.render("Enter Player Names", True, theme["font_color"])
            title_rect = title.get_rect(center=(self.game.width // 2, 50))
            self.screen.blit(title, title_rect)

            # Draw input boxes and labels
            for box_name, box in self.game.input_boxes.items():
                color = Colors.WHITE if box_name == self.game.active_input else Colors.GREY
                pygame.draw.rect(self.screen, color, box, 2)

                # Draw label
                label = self.fonts.mediumFont.render(self.game.input_labels[box_name], True, theme["font_color"])
                label_rect = label.get_rect(bottomleft=(box.left, box.top - 5))
                self.screen.blit(label, label_rect)

                # Draw input text
                text_surface = self.fonts.mediumFont.render(self.game.input_texts[box_name], True, theme["font_color"])
                self.screen.blit(text_surface, (box.x + 5, box.y + 5))

            # Draw start button if both names are entered
            #if self.input_texts["player1"] and self.input_texts["player2"]:
            self.draw_button("Start Game", (self.game.width // 3, self.game.height * 3 // 4))

            # Draw scores button to see the top rankings
            self.draw_button("Scores", (self.game.width // 1.5, self.game.height * 3 // 4))

    def render_game(self):
        """Render game board"""

        theme = self.theme_manager.get_theme()  # Load the current theme colors
        grid_color = theme["grid_color"]
        x_color = theme["x_color"]
        o_color = theme["o_color"]

        # Draw game board
        tile_size = self.game.width // 6
        tile_origin = (self.game.width // 2 - (1.5 * tile_size),
                       self.game.height // 2 - (1.5 * tile_size))
        tiles = []
        for i in range(3):
            row = []
            for j in range(3):
                rect = pygame.Rect(
                    tile_origin[0] + j * tile_size,
                    tile_origin[1] + i * tile_size,
                    tile_size, tile_size
                )
                pygame.draw.rect(self.screen, grid_color, rect, 3)

                if self.game.board[i][j] != ttt.EMPTY:
                    move_color = x_color if self.game.board[i][j] == "X" else o_color
                    move = self.fonts.moveFont.render(self.game.board[i][j], True, move_color)  # Use x_color or o_color
                    move_rect = move.get_rect()
                    move_rect.center = rect.center
                    self.screen.blit(move, move_rect)
                row.append(rect)
            tiles.append(row)

        # Draw game status
        if ttt.terminal(self.game.board):
            self.game.state = GameState.GAME_OVER
        else:
            player = ttt.player(self.game.board)
            player_name = self.game.current_players[ttt.player(self.game.board)]
            if self.game.game_mode == "2P":
                status = f"Player {player_name}'s Turn"
            else:
                status = "Your Turn" if player == self.game.user else "Computer Thinking..."

            status_text = self.fonts.largeFont.render(status, True, theme["font_color"])
            status_rect = status_text.get_rect()
            status_rect.center = (self.game.width // 2, 30)
            self.screen.blit(status_text, status_rect)

        if self.game.state == GameState.GAME:
            if self.game.game_mode == "AI" and not self.game.user == ttt.player(self.game.board) and not ttt.terminal(self.game.board):
                if self.game.ai_turn:
                    time.sleep(0.2)
                    move = ttt.minimax(self.game.board)
                    self.game.board = ttt.result(self.game.board, move)
                    self.game.ai_turn = False
                else:
                    time.sleep(0.2)
                    self.game.ai_turn = True

    def render_game_over(self):
        """Render game over screen"""

        theme = self.theme_manager.get_theme()
        print("Rendering game over...")
        self.render_game()  # Show final board state

        print("Print game result message: ")
        message = self.game.event_handler.handle_game_result()
        message_text = self.fonts.largeFont.render(message, True, theme["font_color"])
        message_rect = message_text.get_rect()
        message_rect.center = (self.game.width / 2, 30)
        self.screen.blit(message_text, message_rect)

        # Draw leaderboard
        self.render_leaderboard(self.game.width // 2, self.game.height // 2)

        # Draw buttons
        self.draw_button("Play Again", (self.game.width // 3, self.game.height - 65))
        self.draw_button("Main Menu", (2 * self.game.width // 3, self.game.height - 65))

    def render_leaderboard(self, x, y):
        """Render leaderboard"""

        theme = self.theme_manager.get_theme()
        if not self.game.show_leaderboard:
            return

        stats = self.game.storage_manager.load_stats()

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
            player_text = self.fonts.mediumFont.render(ranking_text, True, theme["font_color"])
            text_rect = player_text.get_rect(center=(x, y + i * 30))
            self.screen.blit(player_text, text_rect)


    def render_scores(self):
        """Render the scores screen with the leaderboard."""

        theme = self.theme_manager.get_theme()
        # Draw heading
        heading = self.fonts.largeFont.render("Top Rankings", True, theme["font_color"])
        heading_rect = heading.get_rect(center=(self.screen.get_width() // 2, 100))
        self.screen.blit(heading, heading_rect)

        # Render leaderboard
        self.game.show_leaderboard = True
        self.render_leaderboard(self.game.width // 2, 150)

        # Draw a back button
        self.draw_button("Back", (self.game.width // 2, self.game.height * 3 // 4))

class EventHandler:
    def __init__(self, game, fonts, state):
        self.game = game
        self.fonts = fonts
        self.state = self.game.state
        
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
                if self.game.state == GameState.PLAYER_SELECTION and self.game.game_mode == "2P":
                    self.game.active_input = None
                    for box_name, box in self.game.input_boxes.items():
                        if box.collidepoint(mouse_pos):
                            self.game.active_input = box_name

            elif event.type == pygame.KEYDOWN and self.game.active_input:
                if event.key == pygame.K_RETURN:
                    if self.game.input_texts["player1"] and self.game.input_texts["player2"]:
                        self.game.current_players["X"] = self.game.input_texts["player1"]
                        self.game.current_players["O"] = self.game.input_texts["player2"]
                        self.game.state = GameState.GAME
                elif event.key == pygame.K_BACKSPACE:
                    self.game.input_texts[self.game.active_input] = self.game.input_texts[self.game.active_input][:-1]
                else:
                    if len(self.game.input_texts[self.game.active_input]) < 15:  # Limit name length
                        self.game.input_texts[self.game.active_input] += event.unicode

    def handle_click(self, mouse_pos):
        """Handle mouse clicks based on game state"""
        if self.game.state == GameState.MENU:
            self.handle_menu_click(mouse_pos)
        elif self.game.state == GameState.PLAYER_SELECTION:
            self.handle_player_selection_click(mouse_pos)
        elif self.game.state == GameState.GAME:
            self.handle_game_click(mouse_pos)
        elif self.game.state == GameState.GAME_OVER:
            self.handle_game_over_click(mouse_pos)
        elif self.game.state == GameState.SCORES:
            self.handle_scores_click(mouse_pos)
        elif self.game.state == GameState.SETTINGS:
            self.handle_settings_click(mouse_pos)


    def handle_settings_click(self, mouse_pos):
        """Handle clicks in the settings state"""
        back_button = pygame.Rect(self.game.width // 2 - 100, self.game.height * 3 // 4, 200, 50)
        apply_button = pygame.Rect(self.game.width // 2 - 100, self.game.height * 6 // 4, 200, 50)

        if apply_button.collidepoint(mouse_pos):
            self.game.state = GameState.MENU
            time.sleep(0.2)
        elif back_button.collidepoint(mouse_pos):
            self.game.state = GameState.MENU
            time.sleep(0.2)


    def handle_scores_click(self, mouse_pos):
        """Handle clicks in the scores state"""
        back_button = pygame.Rect(self.game.width // 2 - 100, self.game.height * 3 // 4, 200, 50)

        if back_button.collidepoint(mouse_pos):
            self.game.state = GameState.PLAYER_SELECTION
            self.game.show_leaderboard = False
            time.sleep(0.2)

    def handle_menu_click(self, mouse_pos):
        """Handle clicks in the menu state"""
        vs_ai_button = pygame.Rect(self.game.width // 4 - 100, self.game.height // 2, 200, 50)
        vs_player_button = pygame.Rect(3 * self.game.width // 4 - 100, self.game.height // 2, 200, 50)
        settings_button = pygame.Rect(self.game.width // 4 - 100, self.game.height // 6, 200, 50)

        if vs_ai_button.collidepoint(mouse_pos):
            self.game.game_mode = "AI"
            self.game.state = GameState.PLAYER_SELECTION
            time.sleep(0.2)  # Prevent double clicks
        elif vs_player_button.collidepoint(mouse_pos):
            self.game.game_mode = "2P"
            self.show_leaderboard = False
            self.game.input_texts = {"player1": "", "player2": ""}
            self.game.state = GameState.PLAYER_SELECTION
            time.sleep(0.2)
        elif settings_button.collidepoint(mouse_pos):
            self.game.state = GameState.SETTINGS
            time.sleep(0.2)

    def handle_player_selection_click(self, mouse_pos):
        """Handle clicks in the player selection state"""
        play_x_button = pygame.Rect(self.game.width // 4 - 100, self.game.height // 2, 200, 50)
        play_o_button = pygame.Rect(3 * self.game.width // 4 - 100, self.game.height // 2, 200, 50)

        if self.game.game_mode == "AI":
            if play_x_button.collidepoint(mouse_pos):
                self.game.user = ttt.X
                self.game.current_players["X"] = 'Player'
                self.game.current_players["O"] = 'Computer'
                self.game.state = GameState.GAME
                time.sleep(0.2)
            elif play_o_button.collidepoint(mouse_pos):
                self.game.user = ttt.O
                self.game.current_players["X"] = "Computer"
                self.game.current_players["O"] = "Player"
                self.game.state = GameState.GAME
                time.sleep(0.2)


        elif self.game.game_mode == "2P":

            # Check if scores button is clicked
            scores_button = pygame.Rect(self.game.width // 1.5 - 100, self.game.height * 3 // 4, 200, 50)
            if scores_button.collidepoint(mouse_pos):
                self.game.state = GameState.SCORES
                time.sleep(0.2)

            # Check if start button is clicked
            start_button = pygame.Rect(self.game.width // 3 - 100, self.game.height * 3 // 4, 200, 50)
            if start_button.collidepoint(mouse_pos):
                if self.game.input_texts["player1"] and self.game.input_texts["player2"]:

                    player1 = self.game.input_texts["player1"]
                    player2 = self.game.input_texts["player2"]
                    if player1 == player2:
                        message = "Player's name are duplicated!!"
                        msg_surface = self.fonts.mediumFont.render(message, True, Colors.RED)
                        msg_rect = msg_surface.get_rect(center=(self.game.width // 2, self.game.height // 2 + 60 ))
                        self.game.screen.blit(msg_surface, msg_rect)
                        pygame.display.flip()  # Update the display to show the message
                        time.sleep(1)  # Show the message for 1 second
                    else: 
                        self.game.current_players["X"] = self.game.input_texts["player1"]
                        self.game.current_players["O"] = self.game.input_texts["player2"]
                        self.game.state = GameState.GAME
                        time.sleep(0.2)

                else:
                    # Draw error message if names are not entered
                    message = "Please enter both player names to start"
                    msg_surface = self.fonts.mediumFont.render(message, True, Colors.RED)
                    msg_rect = msg_surface.get_rect(center=(self.game.width // 2, self.game.height // 2 + 60 ))
                    self.game.screen.blit(msg_surface, msg_rect)
                    pygame.display.flip()  # Update the display to show the message
                    time.sleep(1)  # Show the message for 1 second


    def handle_game_click(self, mouse_pos):
        """Handle clicks during gameplay"""
        if ttt.terminal(self.game.board):
            return

        # Calculate board positions
        tile_size = self.game.width // 6
        tile_origin = (self.game.width // 2 - (1.5 * tile_size),
                       self.game.height // 2 - (1.5 * tile_size))

        # Check if it's the player's turn
        current_player = ttt.player(self.game.board)
        print(f"DEBUG: Current player: {current_player}")
        print(f"DEBUG: Game mode: {self.game.game_mode}, AI turn: {self.game.ai_turn}, User: {self.game.user}")

        if (self.game.game_mode == "AI" and current_player != self.game.user) or self.game.ai_turn:
            print("DEBUG: Not the player's turn or AI is currently playing.")
            return

        # Check each tile
        for i in range(3):
            for j in range(3):
                rect = pygame.Rect(
                    tile_origin[0] + j * tile_size,
                    tile_origin[1] + i * tile_size,
                    tile_size, tile_size
                )
                if rect.collidepoint(mouse_pos) and self.game.board[i][j] == ttt.EMPTY:
                    print("DEBUG: Tile is empty. Making a move.")
                    self.game.board = ttt.result(self.game.board, (i, j))
                    print(f"DEBUG: Updated board:\n{self.game.board}")
                    # If in AI mode, set ai_turn to True
                    if self.game.game_mode == "AI":
                        print("DEBUG: AI's turn set to True.")
                        self.game.ai_turn = True
                    return

    def handle_game_over_click(self, mouse_pos):
        """Handle clicks in the game over state"""
        play_again_button = pygame.Rect(self.game.width // 3 - 100, self.game.height - 65, 200, 50)
        main_menu_button = pygame.Rect(2 * self.game.width // 3 - 100, self.game.height - 65, 200, 50)

        if play_again_button.collidepoint(mouse_pos):
            # Reset the game but keep the same players and mode
            self.game.board = ttt.initial_state()
            self.game.ai_turn = False
            self.game.stats_updated = False
            self.game.state = GameState.GAME
            time.sleep(0.2)
        elif main_menu_button.collidepoint(mouse_pos):
            # Reset everything and go back to menu
            self.game.game_mode = None
            self.game.user = None
            self.game.board = ttt.initial_state()
            self.game.ai_turn = False
            self.game.show_leaderboard = False
            self.game.stats_updated = False
            self.game.current_players = {"X": None, "O": None}
            self.game.state = GameState.MENU
            time.sleep(0.2)

    def handle_game_result(self):
        """Determine game result and update stats"""
        winner = ttt.winner(self.game.board)
        if winner is None:
            message = "Game Over: Tie!"

            if self.game.game_mode == "2P" and not self.game.stats_updated:
                self.game.storage_manager.update_player_stats(self.game.current_players["X"], tied=True)
                self.game.storage_manager.update_player_stats(self.game.current_players["O"], tied=True)
                self.game.stats_updated = True
        else:
            if self.game.game_mode == "2P" and not self.game.stats_updated:
                winner_name = self.game.current_players[winner]
                loser_symbol = "O" if winner == "X" else "X"
                loser_name = self.game.current_players[loser_symbol]
                self.game.storage_manager.update_player_stats(winner_name, won=True)
                self.game.storage_manager.update_player_stats(loser_name, won=False)
                self.game.stats_updated = True
            message = f"Game Over: {self.game.current_players[winner]} wins!"
        return message

class Fonts:
    def __init__(self):
        # Fonts
        self.mediumFont = pygame.font.Font("OpenSans-Regular.ttf", 28)
        self.largeFont = pygame.font.Font("OpenSans-Regular.ttf", 40)
        self.moveFont = pygame.font.Font("OpenSans-Regular.ttf", 60)

class TicTacToeGame:
    def __init__(self):
        pygame.init()
        self.size = self.width, self.height = 800, 600
        self.screen = pygame.display.set_mode(self.size)
        self.fonts = Fonts()

        # GameState
        self.game_mode = None  # None, "AI", "2P"
        self.user = None
        self.board = ttt.initial_state()
        self.ai_turn = False
        self.show_leaderboard = False
        self.state = GameState.MENU
        self.stats_updated = False
        self.current_theme = "Classic"

        # Initialize managers
        self.theme_manager = ThemeManager()
        self.storage_manager = StorageManager()
        self.storage_manager.initialize_storage()
        
        self.renderer = Renderer(self, self.screen, self.theme_manager, self.fonts, self.state)
        self.event_handler = EventHandler(self, self.fonts, self.state)
        
        # Input attributes for player names
        self.input_boxes = {
            "player1": pygame.Rect(300, 200, 200, 40),  # Example positions and sizes
            "player2": pygame.Rect(300, 300, 200, 40)
        }
        self.input_texts = {"player1": "", "player2": ""}
        self.active_input = None
        self.input_labels = {"player1": "Player 1 Name", "player2": "Player 2 Name"}

        self.current_players = {"X": None, "O": None}


    def run(self):
        """Main game loop"""
        while True:
            self.event_handler.handle_events()
            #self.update()
            self.renderer.render()
            pygame.display.flip()

if __name__ == "__main__":
    game = TicTacToeGame()
    game.run()