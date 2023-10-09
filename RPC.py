import Pyro4
import threading

@Pyro4.expose
class Client:

    def __init__(self, game):
        self.messageReceived = ""
        self.game = game
        self.isCurrentPlayer = False

    def registerClient(self):
        daemon = Pyro4.Daemon()
        ns = Pyro4.locateNS()
        uri = daemon.register(self)
        ns.register("my_client", uri)

        threading.Thread(target=daemon.requestLoop).start()

    def conectWithServer(self):
        self.server = Pyro4.Proxy("PYRONAME:my_server")
        self.server.receiveConection("PYRONAME:my_client")

    def sendMessage(self, message):
        self.server.receiveMessage(message)
    
    def receiveMessage(self, message):
        self.messageReceived = message

    def sendBoard(self, board):
        self.isCurrentPlayer = False
        self.server.receiveBoard(board)
        self.game.current_player = "X" if self.game.current_player == "O" else "O"

    def receiveBoard(self, board):
        self.game.update_board(board)
        self.isCurrentPlayer = True
        self.game.current_player = "X" if self.game.current_player == "O" else "O"

    def shouldShowPopUp(self, message):
        self.server.showPopUp(message)

    def showPopUp(self, message):
        self.game.messagePopUp = message
        self.game.show_popup(message)

@Pyro4.expose
class Server:

    def __init__(self, game):
        self.messageReceived = ""
        self.game = game
        self.isCurrentPlayer = False

    def registerServer(self):
        daemon = Pyro4.Daemon()
        ns = Pyro4.locateNS()
        uri = daemon.register(self)
        ns.register("my_server", uri)

        threading.Thread(target=daemon.requestLoop).start()
    
    def receiveConection(self, name):
        self.client = Pyro4.Proxy(name)

    def sendMessage(self, message):
        self.client.receiveMessage(message)

    def receiveMessage(self, message):
        self.messageReceived = message

    def sendBoard(self, board):
        self.isCurrentPlayer = False
        self.client.receiveBoard(board)
        self.game.current_player = "X" if self.game.current_player == "O" else "O"

    def receiveBoard(self, board):
        self.game.update_board(board)
        self.isCurrentPlayer = True
        self.game.current_player = "X" if self.game.current_player == "O" else "O"

    def shouldShowPopUp(self, message):
        self.client.showPopUp(message)

    def showPopUp(self, message):
        self.game.messagePopUp = message
        self.game.show_popup(message)

def initGame(userNumer, game):
    if userNumer == '0':
        server = Server(game)
        server.registerServer()

        return server
    else:
        client = Client(game)
        client.registerClient()
        client.conectWithServer()

        return client