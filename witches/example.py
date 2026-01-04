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
        inp = input(f"card id: ")
        if inp not in cards and inp in player.card_ids:
            cards.append(inp)
    return cards

def stitch_feedback(winner_id):
    print(f"player {winner_id} won the stitch!")


if __name__ == "__main__":
    
    # INITIALISING
    manager = GameManager()
    manager.register_stitch_feedback(stitch_feedback)
    players = {f"p{i+1}": Player(f"p{i+1}") for i in range(4)}

    # JOINING
    for p in players.values(): manager.join(p)
    
    new_round = True
    while new_round:
            
        # SETUP
        manager.start()
        while manager.state is LobbyState.SETUP:
            for player_id in manager.missing_switch_player_ids:
                manager.switch_cards(player_id, choose_switch_cards(manager.switch_card_number, players[player_id]))
        
        # GAME
        while manager.state is LobbyState.GAME:
            p_id = manager.current_player_id
            print(f"Player {p_id}, choose a card to play!")
            manager.play_card(p_id, select_card(players[p_id]))

        print("results:")
        for i in players:
            print(f"   ({i}) {players[i].total_game_score}")
        
        new_round = True if input("next round (y/n): ").lower() == "y" else False
    
    print(f"overall winners: {manager.winner_ids}")
    

