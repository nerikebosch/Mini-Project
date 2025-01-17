import pygame
import sys
import time

import tictactoe as ttt

pygame.init()
size = width, height = 600, 400

# Colors
black = (0, 0, 0)
white = (255, 255, 255)

screen = pygame.display.set_mode(size)

mediumFont = pygame.font.Font("OpenSans-Regular.ttf", 28)
largeFont = pygame.font.Font("OpenSans-Regular.ttf", 40)
moveFont = pygame.font.Font("OpenSans-Regular.ttf", 60)

game_mode = None  # None = not selected, AI , 2P
user = None
board = ttt.initial_state()
ai_turn = False

while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    screen.fill(black)

    # Let user choose game mode
    if game_mode is None:
        
        # Draw title
        title = largeFont.render("Play Tic-Tac-Toe", True, white)
        titleRect = title.get_rect() # to create a rectangular object for text surface
        titleRect.center = (width // 2, 50)
        screen.blit(title, titleRect) # to draw an image
        
        # Draw game mode buttons
        vsAIButton = pygame.Rect(1.5*(width / 8), (height / 2), (width / 4), 50) # rectangular object
        vsAI = mediumFont.render("vs AI", True, black) # Text
        vsAIRect = vsAI.get_rect()
        vsAIRect.center = vsAIButton.center
        pygame.draw.rect(screen, white, vsAIButton) # draw a rectangle
        screen.blit(vsAI, vsAIRect)
        
        play2Button = pygame.Rect(4.5 * (width / 8), (height / 2), (width / 4), 50)
        play2 = mediumFont.render("2 Players", True, black) 
        play2Rect = play2.get_rect()
        play2Rect.center = play2Button.center
        pygame.draw.rect(screen, white, play2Button)
        screen.blit(play2, play2Rect)
        
        # Check if button is clicked
        click, _, _ = pygame.mouse.get_pressed() # get the state of the mouse buttons
        if click == 1:
            mouse = pygame.mouse.get_pos() # get the mouse cursor position
            if vsAIButton.collidepoint(mouse):
                time.sleep(0.2)
                game_mode = "AI"
            elif play2Button.collidepoint(mouse):
                time.sleep(0.2)
                game_mode = "2P"
                user = ttt.X
        
    # AI mode: Let user choose a player.
    elif user is None and game_mode == "AI":

        # Draw title
        title = largeFont.render("Play Tic-Tac-Toe vs AI", True, white)
        titleRect = title.get_rect()
        titleRect.center = ((width / 2), 50)
        screen.blit(title, titleRect)

        # Draw buttons
        playXButton = pygame.Rect((width / 8), (height / 2), width / 4, 50)
        playX = mediumFont.render("Play as X", True, black)
        playXRect = playX.get_rect()
        playXRect.center = playXButton.center
        pygame.draw.rect(screen, white, playXButton)
        screen.blit(playX, playXRect)

        playOButton = pygame.Rect(5 * (width / 8), (height / 2), width / 4, 50)
        playO = mediumFont.render("Play as O", True, black)
        playORect = playO.get_rect()
        playORect.center = playOButton.center
        pygame.draw.rect(screen, white, playOButton)
        screen.blit(playO, playORect)

        # Check if button is clicked
        click, _, _ = pygame.mouse.get_pressed()
        if click == 1:
            mouse = pygame.mouse.get_pos()
            if playXButton.collidepoint(mouse):
                time.sleep(0.2)
                user = ttt.X
            elif playOButton.collidepoint(mouse):
                time.sleep(0.2)
                user = ttt.O

    else: # game_mode = 2P

        # Draw game board
        tile_size = 80
        tile_origin = (width / 2 - (1.5 * tile_size),
                       height / 2 - (1.5 * tile_size))
        tiles = []
        for i in range(3):
            row = []
            for j in range(3):
                rect = pygame.Rect(
                    tile_origin[0] + j * tile_size,
                    tile_origin[1] + i * tile_size,
                    tile_size, tile_size
                )
                pygame.draw.rect(screen, white, rect, 3)

                if board[i][j] != ttt.EMPTY:
                    move = moveFont.render(board[i][j], True, white)
                    moveRect = move.get_rect()
                    moveRect.center = rect.center
                    screen.blit(move, moveRect)
                row.append(rect)
            tiles.append(row)

        game_over = ttt.terminal(board)
        player = ttt.player(board)

        # Show title
        if game_over: # end of the game
            winner = ttt.winner(board)
            if winner is None:
                title = f"Game Over: Tie."
            else:
                title = f"Game Over: {winner} wins."
        elif game_mode == "2P": # 2P mode
            title = f"Player {player}'s turn"
        elif user == player: # AI
            title = f"Play as {user}"
        else:
            title = f"Computer thinking..."
        title = largeFont.render(title, True, white)
        titleRect = title.get_rect()
        titleRect.center = ((width / 2), 30)
        screen.blit(title, titleRect)

        # Check for AI move (AI mode)
        if game_mode == "AI" and user != player and not game_over:
            if ai_turn:
                time.sleep(0.5)
                move = ttt.minimax(board) # using algorithm for bot here
                board = ttt.result(board, move)
                ai_turn = False
            else:
                ai_turn = True

        # Check for a user move
        click, _, _ = pygame.mouse.get_pressed()
        # if click == 1 and user == player and not game_over:
        if click == 1 and not game_over:
            mouse = pygame.mouse.get_pos()
            for i in range(3):
                for j in range(3):
                    if (board[i][j] == ttt.EMPTY and tiles[i][j].collidepoint(mouse)):
                        if game_mode == "2P":
                            board = ttt.result(board, (i, j))
                        elif game_mode == "AI" and user == player:
                            board = ttt.result(board, (i, j))

        if game_over:
            againButton = pygame.Rect(width / 3, height - 65, width / 3, 50)
            again = mediumFont.render("Play Again", True, black)
            againRect = again.get_rect()
            againRect.center = againButton.center
            pygame.draw.rect(screen, white, againButton)
            screen.blit(again, againRect)
            click, _, _ = pygame.mouse.get_pressed()
            if click == 1:
                mouse = pygame.mouse.get_pos()
                if againButton.collidepoint(mouse):
                    time.sleep(0.2)
                    game_mode = None 
                    user = None
                    board = ttt.initial_state()
                    ai_turn = False

    pygame.display.flip()
