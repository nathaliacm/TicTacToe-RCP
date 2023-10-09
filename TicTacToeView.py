import pygame
import RPC
import time
import threading

class TicTacToeLogic:
    # Verifica vitória em tabuleiros individuais
    @staticmethod
    def check_board_winner(board):
        for row in board:
            first_symbol = row[0]
            if first_symbol != "" and all(cell == first_symbol for cell in row):
                return first_symbol
        
        for col in range(3):
            first_symbol = board[0][col]
            if first_symbol != "" and all(board[row][col] == first_symbol for row in range(3)):
                return first_symbol
        
        if board[0][0] != "" and all(board[i][i] == board[0][0] for i in range(3)):
            return board[0][0]
        
        if board[0][2] != "" and all(board[i][2 - i] == board[0][2] for i in range(3)):
            return board[0][2]
        
        return None

    # Verifica vitória nas camadas diagonais tridimensionais
    @staticmethod
    def check_diagonal_3d_winner(board):
        for layer in range(3):
            # Verifica a diagonal principal da camada diagonal
            diagonal_main = [board[i][i][layer] for i in range(3)]
            if all(cell == diagonal_main[0] and cell != "" for cell in diagonal_main):
                return diagonal_main[0]

            # Verifica a diagonal secundária da camada diagonal
            diagonal_secondary = [board[i][2 - i][layer] for i in range(3)]
            if all(cell == diagonal_secondary[0] and cell != "" for cell in diagonal_secondary):
                return diagonal_secondary[0]

        for layer in range(3):
            # Verifica a diagonal principal ao longo dos planos
            diagonal_plane_main = [board[i][i][i] for i in range(3)]
            if all(cell == diagonal_plane_main[0] and cell != "" for cell in diagonal_plane_main):
                return diagonal_plane_main[0]
            
            # Verifica a diagonal secundária ao longo dos planos
            diagonal_plane_secondary = [board[i][2 - i][i] for i in range(3)]
            if all(cell == diagonal_plane_secondary[0] and cell != "" for cell in diagonal_plane_secondary):
                return diagonal_plane_secondary[0]

        return None

    # Verifica as colunas entre tabuleiros
    @staticmethod
    def check_column_winner(board, col):
        for layer in range(3):
            if all(board[i][col][layer] == board[0][col][layer] and board[i][col][layer] != "" for i in range(3)):
                return board[0][col][layer]
        return None

    @staticmethod
    def check_winner(board):
        for i, tab in enumerate(board):
            board_winner = TicTacToeLogic.check_board_winner(tab)
            if board_winner:
                print(f"Jogador '{board_winner}' venceu no tabuleiro {i + 1}!")
                return board_winner
        
        for col in range(3):
            diagonal_3d_winner = TicTacToeLogic.check_diagonal_3d_winner(board)
            if diagonal_3d_winner:
                print(f"Jogador '{diagonal_3d_winner}' venceu nas camadas diagonais entre tabuleiros!")
                return diagonal_3d_winner

        for col in range(3):
            column_winner = TicTacToeLogic.check_column_winner(board, col)
            if column_winner:
                print(f"Jogador '{column_winner}' venceu nas colunas entre tabuleiros!")
                return column_winner

        return None

class TicTacToeView:
    def __init__(self):
        self.resigned = False
        self.screen_width = 1100
        self.screen_height = 400
        self.board_size = 200
        self.border_color = (70, 70, 70)
        self.line_color = (0, 180, 0)
        self.x_color = (0, 0, 180)
        self.line_thickness = 5

        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))

        self.board_matrix = [[["" for _ in range(3)] for _ in range(3)] for _ in range(3)]
        self.board_positions = [(50, 100), (300, 100), (550, 100)]
        self.board_states = [[["" for _ in range(3)] for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        self.isCurrentPlayer = False
        self.hasWinner = False
        self.winPossibilities = 27
        self.messagePopUp = ""

        self.game_logic = TicTacToeLogic()

        self.chat_messages = [] 
        self.chat_input = ""
        self.chat_input_box = pygame.Rect(self.screen_width - 180, self.screen_height - 40, 130, 30)
        self.chat_active = False
        self.chat_font = pygame.font.Font(None, 24)
        self.chat_color_inactive = pygame.Color('lightskyblue3')
        self.chat_color_active = pygame.Color('dodgerblue2')
        self.color = self.chat_color_inactive

    def draw_board(self, x, y):
        pygame.draw.rect(self.screen, self.border_color, (x, y, self.board_size, self.board_size), 6)
        for row in range(3):
            for col in range(3):
                pygame.draw.rect(self.screen, self.border_color,
                                 (x + col * (self.board_size // 3), y + row * (self.board_size // 3),
                                  self.board_size // 3, self.board_size // 3), 3)
        self.draw_resign_button() 

    def get_cell_index(self, x, y, board_x, board_y):
        relative_x = x - board_x
        relative_y = y - board_y
        cell_row = relative_y // (self.board_size // 3)
        cell_col = relative_x // (self.board_size // 3)
        return cell_row, cell_col
    
    def draw_resign_button(self):
        font = pygame.font.Font(None, 24)
        resign_text = font.render("Desistir", True, (200, 0, 20))
        resign_rect = resign_text.get_rect(center=(self.screen_width // 2, self.screen_height - 30))

        button_width = 100
        button_height = 30
        button_rect = pygame.Rect(
            self.screen_width // 2 - button_width // 2,
            self.screen_height - 45,
            button_width,
            button_height
        )

        pygame.draw.rect(self.screen, (200, 200, 200), button_rect, border_radius=5)
        self.screen.blit(resign_text, resign_rect)

    def handle_mouse_click(self, board_index, cell_row, cell_col):
        if self.board_states[board_index][cell_row][cell_col] == "":
            self.board_states[board_index][cell_row][cell_col] = self.current_player
            
            self.board_matrix[board_index][cell_row][cell_col] = self.current_player

            self.winPossibilities -= 1
            self.serverClient.sendBoard(self.board_states)

            winner = self.game_logic.check_winner(self.board_matrix)

            if self.winPossibilities == 0:
                self.messagePopUp = "Deu velha!"
                self.serverClient.shouldShowPopUp(self.messagePopUp)
                self.show_popup(self.messagePopUp)
            
            elif winner:
                self.winner = winner
                self.messagePopUp = f"Jogador {winner} venceu!"
                self.serverClient.shouldShowPopUp(self.messagePopUp)
                self.show_popup(self.messagePopUp)

    def draw_symbols(self):
        for i, (board_x, board_y) in enumerate(self.board_positions):
            for row in range(3):
                for col in range(3):
                    symbol = self.board_states[i][row][col]
                    cell_x = board_x + col * (self.board_size // 3) 
                    cell_y = board_y + row * (self.board_size // 3)
                    if symbol == "X":
                        line_length = self.board_size // 3 - 20
                        x_start = cell_x + (self.board_size // 6) - (line_length // 2)
                        y_start = cell_y + (self.board_size // 6) - (line_length // 2)
                        x_end = x_start + line_length
                        y_end = y_start + line_length
                        pygame.draw.line(self.screen, self.x_color, (x_start, y_start), (x_end, y_end), 6)
                        pygame.draw.line(self.screen, self.x_color, (x_end, y_start), (x_start, y_end), 6)
                    elif symbol == "O":
                        circle_radius = (self.board_size // 6) - 8
                        pygame.draw.circle(self.screen, self.line_color, (cell_x + self.board_size // 6, cell_y + self.board_size // 6), circle_radius, self.line_thickness)

    def update_screen(self):
        self.screen.fill((255, 255, 255))

        for i, (board_x, board_y) in enumerate(self.board_positions):
            self.draw_board(board_x, board_y)
            self.draw_symbols()

        pygame.display.flip()

    def update_board(self, server_data):
        self.board_states = server_data
        self.update_screen()

    def draw_chat_area(self):
        pygame.draw.rect(self.screen, (220, 220, 220), (self.screen_width - 200, 0, 200, self.screen_height))
        
        y_offset = 10
        for message in (self.chat_messages[-15:]): 
            rendered_message = self.chat_font.render(message, True, (0, 0, 0))
            self.screen.blit(rendered_message, (self.screen_width - 190, y_offset))
            y_offset += 25

        txt_surface = self.chat_font.render(self.chat_input, True, self.color)
        self.screen.blit(txt_surface, (self.chat_input_box.x + 5, self.chat_input_box.y + 5))
        pygame.draw.rect(self.screen, self.color, self.chat_input_box, 2)

        send_button = pygame.Rect(self.screen_width - 45, self.screen_height - 40, 40, 30)
        pygame.draw.rect(self.screen, (0, 180, 0), send_button)
        self.screen.blit(self.chat_font.render("Env", True, (255, 255, 255)), (self.screen_width - 42, self.screen_height - 37))

    def handle_chat_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.chat_input_box.collidepoint(event.pos):
                self.chat_active = True
            else:
                self.chat_active = False
            self.color = self.chat_color_active if self.chat_active else self.chat_color_inactive
            if self.screen_width - 45 <= event.pos[0] < self.screen_width - 5 and self.screen_height - 40 <= event.pos[1] < self.screen_height - 10:
                self.chat_messages.append(self.chat_input)
                self.serverClient.sendMessage(self.chat_input)
                self.chat_input = ""
        if event.type == pygame.KEYDOWN:
            if self.chat_active:
                if event.key == pygame.K_RETURN:
                    self.chat_messages.append(self.chat_input)
                    self.serverClient.sendMessage(self.chat_input)
                    self.chat_input = ""
                elif event.key == pygame.K_BACKSPACE:
                    self.chat_input = self.chat_input[:-1]
                else:
                    self.chat_input += event.unicode

    def handle_board_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouseX, mouseY = event.pos
            for i, (board_x, board_y) in enumerate(self.board_positions):
                if board_x <= mouseX < board_x + self.board_size and board_y <= mouseY < board_y + self.board_size:
                    cell_row, cell_col = self.get_cell_index(mouseX, mouseY, board_x, board_y)
                    if game.serverClient.isCurrentPlayer and not self.hasWinner and not self.resigned:
                        self.handle_mouse_click(i, cell_row, cell_col)
            if self.screen_width // 2 - 50 <= mouseX < self.screen_width // 2 + 50 and self.screen_height - 45 <= mouseY < self.screen_height - 15:
                self.messagePopUp = "Jogador desistiu!"
                self.resigned = True
                self.serverClient.shouldShowPopUp(self.messagePopUp)

    def run(self):
        self.running = True
        while self.running:
            for event in pygame.event.get():
                self.handle_board_event(event)
                self.handle_chat_event(event)
            if self.serverClient.messageReceived != "":
                     self.chat_messages.append("[ADVERSARIO] "+ self.serverClient.messageReceived)
                     self.serverClient.messageReceived = ""

            self.screen.fill((255, 255, 255))
        
            for i, (board_x, board_y) in enumerate(self.board_positions):
                self.draw_board(board_x, board_y)
                self.draw_symbols()
                
            self.draw_chat_area()

            if self.resigned or self.hasWinner:
                self.show_popup(self.messagePopUp)

            pygame.display.flip()
        pygame.event.clear()
        pygame.quit()
    
    def reset_game(self):
        self.board_states = [[["" for _ in range(3)] for _ in range(3)] for _ in range(3)]
        self.board_matrix = [[["" for _ in range(3)] for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        self.resigned = False
        self.hasWinner = False
        self.winPossibilities = 27

    def show_popup(self, message):
        self.hasWinner = True
        font = pygame.font.Font(None, 36)
        text = font.render(message, True, (0, 0, 0))
        text_rect = text.get_rect(center=(self.screen_width // 2, 20))

        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (255, 255, 255, 128), overlay.get_rect())
        self.screen.blit(overlay, (0, 0))

        self.draw_symbols() 
        self.screen.blit(text, text_rect)
        pygame.display.update()

        threading.Thread(target=self.pause).start()

    def pause(self):
        time.sleep(5)
        self.reset_game()


if __name__ == "__main__":
    game = TicTacToeView()
    usuarioNumber = input("Digite 0 para inicializar um chat e 1 para se conectar a um chat existente\n")
    game.serverClient = RPC.initGame(usuarioNumber, game)
    if usuarioNumber == '0':
        game.serverClient.isCurrentPlayer = True
    time.sleep(2)
    game.run()