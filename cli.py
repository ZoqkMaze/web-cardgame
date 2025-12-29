from classes import *


def show_cards(player: Player):
    for id in player.card_dict:
        print(f"{id}: {player.card_dict[id]}")
    return

def select_card(player: Player, show=True):
    if show: show_cards(player)
    inp = ""
    while inp not in player.card_ids:
        inp = input("card id: ")
    return inp

def choose_switch_cards(switch_cards, player: Player):
    print(f"Player {player.id}, choose {switch_cards} different cards to switch:")
    show_cards(player)
    cards = []
    while len(cards) != switch_cards:
        inp = input("card id: ")
        if inp not in cards and inp in player.card_ids:
            cards.append(inp)
    return cards

def stitch_feedback(winner_id):
    print(f"player {winner_id} won the stitch!")


if __name__ == "__main__":
    
    # INITIALISING
    manager = GameManager()
    players = {f"p{i}": Player(f"p{i}") for i in range(4)}

    # JOINING
    for p in players.values(): manager.join(p)
    
    # SETUP
    manager.start()
    while not manager.all_switched:
        for player_id in manager.missing_switch_player_ids:
            manager.switch_cards(player_id, choose_switch_cards(manager.switch_card_number, players[player_id]))
    
    # GAME
    while manager.state is LobbyState.GAME:
        manager.play_card(manager.current_player_id, select_card(players[manager.current_player_id]))

    print("results:")
    for i, p in players:
        print(f"   ({i}) {p.game_score}")
