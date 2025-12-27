from classes import *

class CLIPlayer(Player):
    def __init__(self, name):
        super().__init__()
        self.name = name
    
    def choose_card(self):
        print(f"player {self.name} - choose a card:")
        for i, c in enumerate(self.cards):
            print(f"   {i}: {c}")
        choise = -1
        while not 0 <= choise < len(self.cards):
            try:
                choise = int(input("card index: "))
            except ValueError:
                choise = -1
        return self.cards[choise]


if __name__ == "__main__":
    players = [CLIPlayer(str(i+1)) for i in range(3)]
    game = Game(players)
    game.gameloop()
    for p in players:
        print(f"player {p.name}: {p.get_game_score()}")
