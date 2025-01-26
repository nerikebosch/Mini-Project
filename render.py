from runner import GameState
from runner import EventHandler
from runner import TicTacToeGame
from runner import Fonts
from runner import Colors
import pygame
import tictactoe as ttt
import time

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
