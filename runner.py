import json
import tictactoe as ttt
import pygame
import sys
import time
from pathlib import Path


class GameState:
    """Represents the different states of the game.

    Attributes:
        MENU (str): The state where the game is at the main menu.
        PLAYER_SELECTION (str): The state where players select their mode or enter names.
        GAME (str): The state where the game is actively being played.
        GAME_OVER (str): The state after the game ends, showing results.
        SCORES (str): The state displaying the leaderboard or scores.
        SETTINGS (str): The state for managing game settings, such as themes.
    """

    MENU = 'menu'
    PLAYER_SELECTION = 'player_selection'
    GAME = 'game'
    GAME_OVER = 'game_over'
    SCORES = 'scores'
    SETTINGS = 'settings'


class Colors:
    """Defines a collection of commonly used colors in the game, represented as RGB tuples.

    Attributes:
        BLACK (tuple): The color black, represented as (0, 0, 0).
        WHITE (tuple): The color white, represented as (255, 255, 255).
        BLUE (tuple): A shade of blue, represented as (87, 160, 211).
        GREEN (tuple): The color green, represented as (0, 255, 0).
        RED (tuple): The color red, represented as (255, 0, 0).
        YELLOW (tuple): The color yellow, represented as (255, 255, 0).
        PURPLE (tuple): The color purple, represented as (128, 0, 128).
        ORANGE (tuple): The color orange, represented as (255, 165, 0).
        GREY (tuple): A shade of grey, represented as (128, 128, 128).
    """

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
    """Manages themes for a game, including loading, saving, and applying themes.

    Attributes:
        theme_file (str): The path to the JSON file containing theme data.
        themes (dict): A dictionary containing theme configurations.
        current_theme (str): The currently selected theme.

    Methods:
        load_themes():
            Loads theme data from the specified theme file.
        
        save_theme():
            Saves the currently selected theme to a file.
        
        load_current_theme():
            Loads the current theme from a save file.
        
        load_theme():
            An alternate method to load the current theme.
        
        apply_theme():
            Applies the currently selected theme to the game.
        
        get_theme():
            Returns the active theme's data.
    """


    def __init__(self, theme_file="game_data/theme.json", default_theme="Classic"):
        """Initializes the ThemeManager.

        Args:
            theme_file (str): The path to the JSON file containing theme data. Defaults to "game_data/theme.json".
            default_theme (str): The default theme to use if none is specified. Defaults to "Classic".
        """

        self.theme_file = theme_file
        self.themes = {}
        self.current_theme = default_theme
        self.load_themes()
        self.load_current_theme()
        

    def load_themes(self):
        """Loads theme data from the specified theme file.

        Tries to read the theme configurations from the JSON file at `theme_file`. If the file is not found,
        a default theme is returned.

        Returns:
            dict: A dictionary of themes if successfully loaded, or the default theme dictionary otherwise.
        """

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
        """Saves the currently selected theme to a file.

        Writes the `current_theme` to the `theme.json` file.
        """


        with open("theme.json", "w") as f:
            json.dump({"current_theme": self.current_theme}, f)


    def load_current_theme(self):
        """Loads the current theme from a save file.

        Reads the `current_theme` from the `theme.json` file. If the file is not found, defaults to "Classic".
        """

        try:
            with open("theme.json", "r") as f:
                self.current_theme = json.load(f).get("current_theme", "Classic")
        except FileNotFoundError:
            print("Theme save file not found. Defaulting to 'Classic'.")


    def load_theme(self):
        """Loads the current theme from a save file (alternate method).

        Reads the `current_theme` from the `theme.json` file. Defaults to "Classic" if the file is missing.
        """

        try:
            with open("theme.json", "r") as f:
                self.current_theme = json.load(f).get("current_theme", "Classic")
        except FileNotFoundError:
            self.current_theme = "Classic"  # Default to "Classic" if the file is missing


    def apply_theme(self):
        """Applies the currently selected theme to the game.

        Sets the background color, grid, and other game elements based on the active theme.
        """

        self.screen.fill(self.themes[self.current_theme]["background"])
        self.draw_grid()
        self.update_game_state()

    def get_theme(self):
        """Returns the active theme's data.

        Fetches the data for the currently selected theme. If the theme does not exist, defaults to "Classic".

        Returns:
            dict: The active theme's configuration.
        """

        return self.themes.get(self.current_theme, self.themes.get("Classic", {}))


class StorageManager:
    """Manages the storage of player statistics, including initialization, loading, saving, and updating stats.

    Attributes:
        data_folder (Path): The path to the folder where player statistics are stored.
        data_file (Path): The path to the JSON file containing player statistics.

    Methods:
        initialize_storage():
            Initializes the storage directory and creates the stats file if it does not exist.
        
        load_stats():
            Loads player statistics from the stats file.
        
        save_stats(stats):
            Saves the given player statistics to the stats file.
        
        update_player_stats(player_name, won=False, tied=False):
            Updates the statistics for a specific player based on the game's outcome.
    """

    def __init__(self, data_folder="game_data"):
        """Initializes the StorageManager.

        Args:
            data_folder (str): The path to the folder where game data is stored. Defaults to "game_data".
        """

        self.data_folder = Path(data_folder)
        self.data_file = self.data_folder / "player_stats.json"
        self.initialize_storage()
        

    def initialize_storage(self):
        """Initializes the storage directory and creates the stats file if it does not exist.

        Ensures that the specified folder exists and creates an empty JSON file for player statistics if none exists.
        """

        self.data_folder.mkdir(exist_ok=True)
        if not self.data_file.exists():
            initiated = {}
            with open(self.data_file, 'w') as f:
                json.dump(initiated, f)


    def load_stats(self):
        """Loads player statistics from the stats file.

        Tries to read player statistics from the JSON file. If the file is missing or corrupted, it creates a new empty file.

        Returns:
            dict: A dictionary of player statistics. If the file is empty or missing, returns an empty dictionary.
        """

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
        """Saves the given player statistics to the stats file.

        Args:
            stats (dict): A dictionary containing player statistics to be saved.
        """

        with open(self.data_file, 'w') as f:
            json.dump(stats, f, indent=4)


    def update_player_stats(self, player_name, won=False, tied=False):
        """Updates the statistics for a specific player based on the game's outcome.

        If the player does not exist in the stats, a new entry is created. Updates are made based on whether the player
        won, lost, or tied the game.

        Args:
            player_name (str): The name of the player whose stats are being updated.
            won (bool): Whether the player won the game. Defaults to False.
            tied (bool): Whether the game was tied. Defaults to False.
        """

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
    """Handles rendering of all game screens, elements, and user interfaces.

    Attributes:
        screen (pygame.Surface): The main display surface for rendering.
        theme_manager (ThemeManager): Manages the game's themes and associated colors.
        fonts (Fonts): Manages the fonts used throughout the game.
        game (TicTacToeGame): The main game object, used for accessing game state.
        state (GameState): The current game state.

    Methods:
        render():
            Renders the current game screen based on the game state.

        draw_text(text, font, color, center):
            Renders a single line of text at a specific position.

        draw_button(text, pos, size, border_radius):
            Draws a button with specified text and position.

        render_menu():
            Renders the main menu screen.

        render_settings():
            Renders the settings screen for selecting themes.

        render_player_selection():
            Renders the player selection screen (vs AI or 2P mode).

        render_game():
            Renders the game board and player moves.

        render_game_over():
            Renders the game over screen and final results.

        render_leaderboard(x, y):
            Renders the leaderboard showing top player rankings.

        render_scores():
            Renders the scores screen, including the leaderboard.
    """


    def __init__(self, game, screen, theme_manager, fonts, state=GameState.MENU):
        """Initializes the Renderer with game, screen, theme, and font information."""

        self.screen = screen
        self.theme_manager = theme_manager 
        self.fonts = fonts
        self.game = game
        self.state = self.game.state


    def render(self):
        """Renders the appropriate game screen based on the current game state."""

        theme = self.theme_manager.get_theme()
        self.screen.fill(theme["background"])  # Use theme background color

        if self.game.state == GameState.MENU:
            self.render_menu()
        elif self.game.state == GameState.PLAYER_SELECTION:
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
        """Utility function to render a single line of text at a specific center position.

        Args:
            text (str): The text to render.
            font (pygame.font.Font): The font object for rendering.
            color (tuple): The RGB color of the text.
            center (tuple): The center position of the text.
        """

        rendered_text = font.render(text, True, color)
        rect = rendered_text.get_rect()
        rect.center = center
        self.screen.blit(rendered_text, rect)


    def draw_button(self, text, pos, size=(200, 50), border_radius=20):
        """Helper method to draw buttons on the screen.

        Args:
            text (str): The text to display on the button.
            pos (tuple): The position of the button's center.
            size (tuple): The size (width, height) of the button.
            border_radius (int): The radius for rounding button corners.

        Returns:
            pygame.Rect: The rectangle of the button for collision detection.
        """

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
        """Renders the main menu screen with title and navigation buttons."""

        theme = self.theme_manager.get_theme()
        # Draw title
        title = self.fonts.largeFont.render("Play Tic-Tac-Toe", True, theme["font_color"])
        title_rect = title.get_rect()
        title_rect.center = (self.game.width // 2, 50)
        self.screen.blit(title, title_rect)

        # Draw buttons
        self.draw_button("vs AI", (2*self.game.width // 4, self.game.height // 3))
        self.draw_button("2 Players", (2*self.game.width // 4, self.game.height // 2))
        self.draw_button("Settings", (2*self.game.width // 4, self.game.height // 1.5))


    def render_settings(self):
        """Renders the settings screen for selecting themes."""

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
        """Renders the player selection screen for choosing sides or entering names."""

        theme = self.theme_manager.get_theme()

        if self.game.game_mode == "AI":
            #print("DEBUG: Rendering AI player selection screen")
            #print(f"DEBUG: Game state: {self.game.state}")
            title = self.fonts.largeFont.render("Choose Your Side", True, theme["font_color"])
            title_rect = title.get_rect(center=(self.game.width // 2, 50))
            self.screen.blit(title, title_rect)

            self.draw_button("Play as X", (2* self.game.width // 4, self.game.height // 3))
            self.draw_button("Play as O", (2* self.game.width // 4, self.game.height // 2))
            self.draw_button("Back", (2* self.game.width // 4, self.game.height // 1.5))

        else: # 2P
            print("Render_player_selection 2P - Enter Player Names")
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

            self.draw_button("Start Game", (self.game.width // 5.2, self.game.height * 3 // 4))
            # Draw scores button to see the top rankings
            self.draw_button("Scores", (self.game.width // 2, self.game.height * 3 // 4))

            self.draw_button("Back", (self.game.width // 1.25, self.game.height * 3 // 4))


    def render_game(self):
        """Renders the game board, player moves, and status messages."""

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
                if self.game.ai_turn:
                    print("DEBUG: AI Turn")
                    status = f"Computer Thinking..."
                else:
                    status = f"Your Turn"

            status_text = self.fonts.largeFont.render(status, True, theme["font_color"])
            status_rect = status_text.get_rect()
            status_rect.center = (self.game.width // 2, 30)
            self.screen.blit(status_text, status_rect)
            time.sleep(0.2)

        if self.game.state == GameState.GAME:
            if self.game.game_mode == "AI" and not self.game.user == ttt.player(self.game.board):
                if self.game.ai_turn:
                    time.sleep(0.2)
                    move = ttt.minimax(self.game.board)
                    self.game.board = ttt.result(self.game.board, move)
                    self.game.ai_turn = False
                else:
                    time.sleep(0.2)
                    self.game.ai_turn = True


    def render_game_over(self):
        """Renders the game over screen with results and leaderboard."""

        theme = self.theme_manager.get_theme()
        self.render_game()  # Show final board state
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
        """Renders the leaderboard showing the top player rankings."""

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
        """Renders the scores screen, including the leaderboard."""

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
    """Handles events and user interactions within the game, such as mouse clicks, keyboard input, and state changes.

    Attributes:
        game (Game): The main game object containing game state and logic.
        fonts (Fonts): The font manager for rendering text.
        state (GameState): The current game state.

    Methods:
        handle_events():
            Processes all user events, including mouse and keyboard input.

        handle_click(mouse_pos):
            Handles mouse click events based on the current game state.

        handle_settings_click(mouse_pos):
            Handles clicks in the settings state.

        handle_scores_click(mouse_pos):
            Handles clicks in the scores state.

        handle_menu_click(mouse_pos):
            Handles clicks in the menu state.

        handle_player_selection_click(mouse_pos):
            Handles clicks in the player selection state.

        handle_game_click(mouse_pos):
            Handles mouse clicks during gameplay.

        handle_game_over_click(mouse_pos):
            Handles clicks in the game over state.

        handle_game_result():
            Determines the result of the game and updates player stats if necessary.
    """

    def __init__(self, game, fonts, state):
        """Initializes the EventHandler.

        Args:
            game (Game): The main game object containing game state and logic.
            fonts (Fonts): The font manager for rendering text.
            state (GameState): The current game state.
        """

        self.game = game
        self.fonts = fonts
        self.state = self.game.state
        

    def handle_events(self):
        """Processes all user events, including mouse and keyboard input.

        Handles quitting the game, mouse clicks, and keyboard input for player name entry during player selection.
        """

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
        """Handles mouse click events based on the current game state.

        Args:
            mouse_pos (tuple): The position of the mouse click.
        """

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
        """Handles clicks in the settings state.

        Args:
            mouse_pos (tuple): The position of the mouse click. Checks if buttons (e.g., Apply, Back) are clicked.
        """

        back_button = pygame.Rect(self.game.width // 2 - 100, self.game.height * 3 // 4, 200, 50)
        apply_button = pygame.Rect(self.game.width // 2 - 100, self.game.height * 6 // 4, 200, 50)

        if apply_button.collidepoint(mouse_pos):
            self.game.state = GameState.MENU
            time.sleep(0.2)
        elif back_button.collidepoint(mouse_pos):
            self.game.state = GameState.MENU
            time.sleep(0.2)


    def handle_scores_click(self, mouse_pos):
        """Handles clicks in the scores state.

        Args:
            mouse_pos (tuple): The position of the mouse click. Checks if the back button is clicked.
        """

        back_button = pygame.Rect(self.game.width // 2 - 100, self.game.height * 3 // 4, 200, 50)

        if back_button.collidepoint(mouse_pos):
            self.game.state = GameState.PLAYER_SELECTION
            self.game.show_leaderboard = False
            time.sleep(0.2)


    def handle_menu_click(self, mouse_pos):
        """Handles clicks in the menu state.

        Args:
            mouse_pos (tuple): The position of the mouse click. Determines if the player wants to play vs AI,
            play vs another player, or enter the settings menu.
        """

        vs_ai_button = pygame.Rect(2*self.game.width // 4 - 100, self.game.height // 3, 200, 50)
        vs_player_button = pygame.Rect(2 * self.game.width // 4 - 100, self.game.height // 2, 200, 50)
        settings_button = pygame.Rect(2*self.game.width // 4 - 100, self.game.height // 1.5, 200, 50)

        if vs_ai_button.collidepoint(mouse_pos):
            self.game.board = ttt.initial_state()
            self.game.game_mode = "AI"
            self.show_leaderboard = False
            self.game.user = None
            self.game.ai_turn = False
            self.game.current_players = {"X": None, "O": None}
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
        """Handles clicks in the player selection state.

        Args:
            mouse_pos (tuple): The position of the mouse click. Checks for clicks on start buttons, name entry
            boxes, or scores display.
        """

        if ttt.terminal(self.game.board):
            return
        current_player = ttt.player(self.game.board)

        play_x_button = pygame.Rect(2* self.game.width // 4 - 100, self.game.height // 3, 200, 50)
        play_o_button = pygame.Rect(2 * self.game.width // 4 - 100, self.game.height // 2, 200, 50)
        back_button = pygame.Rect(2* self.game.width // 4 - 100, self.game.height // 1.5, 200, 50)
        if back_button.collidepoint(mouse_pos):
            self.game.state = GameState.MENU
            time.sleep(0.2)

        if self.game.game_mode == "AI" and current_player != self.game.user:
            if play_x_button.collidepoint(mouse_pos):
                self.game.user = ttt.X
                self.game.current_players["X"] = 'Player'
                self.game.current_players["O"] = 'Computer'
                self.game.state = GameState.GAME
                self.game.ai_turn = False
                time.sleep(0.2)
            elif play_o_button.collidepoint(mouse_pos):
                self.game.user = ttt.O
                self.game.current_players["X"] = "Computer"
                self.game.current_players["O"] = "Player"
                self.game.state = GameState.GAME
                self.game.ai_turn = False
                time.sleep(0.2)


        elif self.game.game_mode == "2P":

            back_button = pygame.Rect(self.game.width // 1.25 - 100, self.game.height * 3 // 4, 200, 50)
            if back_button.collidepoint(mouse_pos):
                self.game.state = GameState.MENU
                time.sleep(0.2)

            # Check if scores button is clicked
            scores_button = pygame.Rect(self.game.width // 2 - 100, self.game.height * 3 // 4, 200, 50)
            if scores_button.collidepoint(mouse_pos):
                self.game.state = GameState.SCORES
                time.sleep(0.2)

            # Check if start button is clicked
            start_button = pygame.Rect(self.game.width // 5.2 - 100, self.game.height * 3 // 4, 200, 50)
            if start_button.collidepoint(mouse_pos):
                if self.game.input_texts["player1"] and self.game.input_texts["player2"]:

                    player1 = self.game.input_texts["player1"]
                    player2 = self.game.input_texts["player2"]
                    if player1 == player2:
                        message = "Player's names are duplicated!!"
                        msg_surface = self.fonts.mediumFont.render(message, True, Colors.RED)
                        msg_rect = msg_surface.get_rect(center=(self.game.width // 2, self.game.height // 2 + 60 ))
                        self.game.screen.blit(msg_surface, msg_rect)
                        pygame.display.flip()  # Update the display to show the message
                        time.sleep(1.5)  # Show the message for 1 second
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
        """Handles mouse clicks during gameplay.

        Args:
            mouse_pos (tuple): The position of the mouse click. Determines which tile on the board is clicked
            and makes a move if it's valid.
        """

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
        """Handles clicks in the game over state.

        Args:
            mouse_pos (tuple): The position of the mouse click. Checks if the player wants to play again or
            return to the main menu.
        """

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
        """Determines the result of the game and updates player stats if necessary.

        Determines if the game ended in a win or a tie and updates the player statistics accordingly.
        Returns:
            str: A message summarizing the game result, such as "Game Over: Tie!" or "Game Over: [Player] wins!".
        """

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
    """Manages font resources for the game, providing different sizes for various UI elements.

    Attributes:
        mediumFont (pygame.font.Font): A medium-sized font, typically used for buttons and smaller text.
        largeFont (pygame.font.Font): A large-sized font, typically used for titles and headings.
        moveFont (pygame.font.Font): A large-sized font used for displaying moves (X and O) on the game board.
    """

    def __init__(self):
        """Initializes the Fonts object, loading font resources with specific sizes."""

        # Fonts
        self.mediumFont = pygame.font.Font("OpenSans-Regular.ttf", 28)
        self.largeFont = pygame.font.Font("OpenSans-Regular.ttf", 40)
        self.moveFont = pygame.font.Font("OpenSans-Regular.ttf", 60)


class TicTacToeGame:
    """Represents the main Tic-Tac-Toe game, including initialization, game state management, and the main loop.

    Attributes:
        size (tuple): The dimensions of the game window.
        width (int): The width of the game window.
        height (int): The height of the game window.
        screen (pygame.Surface): The main game display surface.
        fonts (Fonts): The font manager for rendering text.
        game_mode (str): The current game mode, either None, "AI", or "2P".
        user (str): The user/player's symbol, either "X" or "O".
        board (list): The current game board state.
        ai_turn (bool): Whether it's the AI's turn.
        show_leaderboard (bool): Whether the leaderboard is being displayed.
        state (GameState): The current game state.
        stats_updated (bool): Whether player statistics have been updated after a game.
        current_theme (str): The current theme of the game.
        theme_manager (ThemeManager): Manages themes and visual elements.
        storage_manager (StorageManager): Handles saving and loading of player statistics.
        renderer (Renderer): Handles rendering of the game visuals.
        event_handler (EventHandler): Handles user events such as mouse clicks and key presses.
        input_boxes (dict): Rectangles for player name input fields.
        input_texts (dict): Text entered for player names.
        active_input (str): The currently active input box.
        input_labels (dict): Labels for the input boxes.
        current_players (dict): Maps "X" and "O" to player names.

    Methods:
        run():
            The main game loop, continuously handling events and rendering the game.
    """

    def __init__(self):
        """Initializes the Tic-Tac-Toe game."""

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
        """The main game loop.

        Continuously handles user input, updates the game state, and renders the screen.
        """

        while True:
            self.event_handler.handle_events()
            self.renderer.render()
            pygame.display.flip()


if __name__ == "__main__":
    game = TicTacToeGame()
    game.run()