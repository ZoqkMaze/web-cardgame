import random
from enum import Enum

# todo: add error codes for each class


class LobbyState(Enum):
    JOIN = "join"
    SETUP = "setup"
    GAME = "game"
    IDLE = "idle"
    CANCEL = "cancel"


class Color(Enum):
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    YELLOW = "yellow"
    BLANCK = "blanck"


class Flag(Enum):
    RED_FLAG = "double normal points"
    BLUE_FLAG = "clear all points"
    YELLOW_FLAG = "minus 5 points"
    LOW_FLAG = "plus 5 points"
    HIGH_FLAG = "plus 5 points"
    NONE_FLAG = "no effect"


class Spell(Enum):
    NO_SPELL = 0
    LOW_SPELL = 20
    MEDIUM_SPELL = 25
    HIGH_SPELL = 30


class Card:

    MIN_RANK = 0  # inclusive
    MAX_RANK = 15  # exclusiv

    WITCH_RANK = 11
    QUEEN_RANK = 12

    def __init__(self, color, rank):
        self.__changeable = True
        self.__color = None
        self.__rank = None

        if self.set_color(color) or self.set_rank(rank):
            raise KeyError()

        self.__changeable = False
    
    def __gt__(self, other):
        if isinstance(other, Card):
            return self.__rank > other.rank
        raise ValueError()
    
    def __repr__(self):
        return f"Card<{self.__color}-{self.__rank}>"
    
    @property
    def witch(self):
        return self.__rank == Card.WITCH_RANK
    
    @property
    def queen(self):
        return self.__rank == Card.QUEEN_RANK
    
    @property
    def color(self):
        return self.__color
    
    @property
    def rank(self):
        return self.__rank
    
    @property
    def points(self):
        return 1 if self.__color is Color.RED and not self.witch else 0
    
    @property
    def flag(self):
        if self.__color is Color.GREEN and self.queen: return Flag.HIGH_FLAG
        if self.witch:
            match self.__color:
                case Color.RED:    return Flag.RED_FLAG
                case Color.BLUE:   return Flag.BLUE_FLAG
                case Color.GREEN:  return Flag.LOW_FLAG
                case Color.YELLOW: return Flag.YELLOW_FLAG
                case _: return Flag.NONE_FLAG
        return Flag.NONE_FLAG
    
    def set_color(self, color: Color):
        if self.__changeable:
            if color in Color:
                self.__color = color
                return 0
        return 1
    
    def set_rank(self, rank):
        if self.__changeable:
            if Card.MIN_RANK <= rank < Card.MAX_RANK:
                self.__rank = rank
                return 0
        return 1


class Stitch:

    FULL_ERROR = 1
    NO_CARD_ERROR = 2

    def __init__(self, player_count):
        self.__player_count = player_count
        self.__next_index = 0
        self.__cards: list[Card] = []
        self.__color = Color.BLANCK
        self.__points = 0
        self.__flags = []
        self.__red_cards = 0
        self.__winner = -1

    @property
    def red_cards(self):
        return self.__red_cards
    
    @property
    def color(self):
        return self.__color
    
    @property
    def points(self):
        return self.__points
    
    @property
    def flags(self):
        return self.__flags
    
    @property
    def full(self):
        return len(self.__cards) == self.__player_count
    
    @property
    def winner(self):
        return self.__winner
    
    def play_card(self, card):
        if self.full:
            return Stitch.FULL_ERROR
        if not isinstance(card, Card):
            return Stitch.NO_CARD_ERROR
        
        if self.__color == Color.BLANCK: self.__color = card.color
        if self.__winner == -1: self.__winner = 0
        if card.color is self.__color and card > self.__cards[self.__winner]: self.__winner = self.__next_index
        self.__next_index += 1
        self.__cards.append(card)
        self.__points += card.points
        flag = card.flag
        if flag != Flag.NONE_FLAG: self.__flags.append(flag)
        if card.__color is Color.RED: self.__red_cards += 1
        return
    

class Player:

    MIN_POINTS = 0  # inklusive
    MAX_DOUBLE_POINTS = 15
    HIGH_POINTS = 10
    LOW_POINTS = 5

    def __init__(self, id):
        self.__id = id
        self.__cards: dict[str, Card] = {}
        self.__stitches: list[Stitch] = []
        self.__points = 0  # Punkte über alle Stiche einer Spielrunde
        self.__flags = []
        self.__red_cards = 0
        self.__game_score = 0  # Punkte über alle Spielrunden
        self.__next_card_id = 0
    
    @property
    def id(self):
        return self.__id
    
    @property
    def cards(self):
        return self.__cards
    
    @property
    def flags(self):
        return self.__flags

    @property
    def number_of_cards(self):
        return len(self.__cards)

    @property
    def game_score(self):
        return self.__game_score

    @property
    def spell(self):
        if self.__red_cards == Card.MAX_RANK - Card.MIN_RANK - 2:
            if Flag.LOW_FLAG in self.__flags:
                if Flag.HIGH_FLAG in self.__flags:
                    return Spell.HIGH_SPELL
                else:
                    return Spell.LOW_SPELL
            if Flag.HIGH_FLAG in self.__flags:
                return Spell.MEDIUM_SPELL
        return Spell.NO_SPELL

    @property
    def score(self):
        score = min(Player.MAX_DOUBLE_POINTS, 2*self.__points) if Flag.RED_FLAG in self.__flags else self.__points
        if Flag.LOW_FLAG in self.__flags: score += Player.LOW_POINTS
        if Flag.HIGH_FLAG in self.__flags: score += Player.HIGH_POINTS
        if Flag.YELLOW_FLAG in self.__flags: score -= Player.LOW_POINTS
        if Flag.BLUE_FLAG in self.__flags: score = 0
        return max(Player.MIN_POINTS, score)

    def add_game_score(self, points):
        self.__game_score += points

    def has_card(self, card):
        return card in self.__cards.values()
    
    def has_card_id(self, card_id):
        return card_id in self.__cards
    
    def has_color(self, color):
        for c in self.__cards.values():
            if c.color is color: return True
        return False

    def get_stitch(self, stitch: Stitch):
        self.__stitches.append(stitch)
        self.__points += stitch.points
        self.__flags += stitch.flags
        self.__red_cards += stitch.red_cards

    def play_card(self, card_id):
        return self.__cards.pop(card_id)
    
    def get_card(self, card_id):
        return self.__cards[card_id]
    
    def add_cards(self, cards):
        for c in cards:
            self.__cards[f"c{self.__next_card_id}"] = c
            self.__next_card_id += 1
    
    def add_card(self, card):
        self.__cards[f"c{self.__next_card_id}"] = card
        self.__next_card_id += 1
    
    def remove_card_id(self, card_id):
        del self.__cards[card_id]
    
    def clear_cards(self):
        self.__cards = {}
        self.__stitches = []
        self.__points = 0
        self.__flags = []
        self.__red_cards = 0
        self.__next_card_id = 0


class GameManager:

    MIN_PLAYER = 3  # inclusiv
    MAX_PLAYER = 6  # inclusiv
        
    ALL_CARDS = [
        Card(c, r)
        for c in Color
        for r in range(Card.MIN_RANK+1, Card.MAX_RANK)
        if c is not Color.BLANCK
    ] + [Card(Color.BLANCK, Card.MIN_RANK) for _ in range(len(Color))]

    def __init__(self):
        self.__players: list[Player] = []
        self.__current_player = 0
        self.__state = LobbyState.JOIN

        self.__current_stitch: Stitch = None
        self.__round = 0
    
    @property
    def player_ids(self):
        return [p.id for p in self.__players]
    
    @property
    def player_count(self):
        return len(self.__players)
    
    @property
    def total_stitches(self):
        return len(GameManager.ALL_CARDS) // self.player_count

    @property
    def round(self):
        return self.__round
    
    @property
    def current_color(self):
        return self.__current_stitch.color
    
    @property
    def stitch_full(self):
        return self.__current_stitch.full
    
    def join(self, player: Player):
        if self.__state is LobbyState.JOIN:
            self.__players.append(player)
            return 0
        return 1
    
    def leave(self, player_id):
        if self.__state is LobbyState.JOIN:
            self.__players.remove(player_id)
            return
        self.__state = LobbyState.CANCEL
        # todo: handle break
    
    def start(self):
        if self.__state not in [LobbyState.JOIN, LobbyState.IDLE]:
            return 1
        if GameManager.MIN_PLAYER <= self.player_count <= GameManager.MAX_PLAYER:
            self.__state = LobbyState.SETUP
            self._game_deal_cards()  # todo: change
            return
        return 1
    
    def _skip_card_switch(self):  # todo: implement card switching
        self.__state = LobbyState.GAME
        return
    
    def play_card(self, player_id, card_id):

        if self.__state is not LobbyState.GAME:
            return 1
        
        if player_id not in self.player_ids:
            return 1
        
        if not self.__current_player == self.player_ids.index(player_id):
            return 1
        
        player = self.__players[self.__current_player]
        
        if not player.has_card_id(card_id):
            return 1
        
        card = player.get_card(card_id)
        color = self.current_color

        if color is not Color.BLANCK and card.color is not Color.BLANCK:
            # apply zugzwang
            if player.has_color(color) and card.color is not color:
                return 1
        
        if self.__game.play_card(card):
            raise ValueError()
        
        player.remove_card_id(card_id)
        self.__current_player = (self.__current_player + 1) % self.player_count

        if self.stitch_full:
            self.evaluate_stitch()

        return 0

    def evaluate_stitch(self):
        pass

    def evaluate_round(self):
        if self.__state is not LobbyState.GAME:
            return 1
        
        if self.round != self.total_stitches:
            return 1
        
        spell = max([p.spell for p in self.__players])
        if spell:
            for p in self.__players:
                if not p.spell: p.add_game_score(spell)
        else:
            for p in self.__players:
                p.add_game_score(p.score)
        
        self.__state = LobbyState.IDLE
        self.__current_player = 0
    
    
    def _game_play_card(self, card):
        # caller-todo: remove card from player | check card | check player

        if self.__state is not GameState.PLAYING:
            return 1
        
        # the game does not check for validity -> the player class has to verify!
        if self.__current_stitch.play_card(card):  # stitch is full (or wrong card)
            return 1

        # if stitch is full -> nothing happens -> call new_stitch
        return 0
    
    def _game_new_stitch(self):
        if not self.__current_stitch.full:
            return 1
        old_stitch = self.__current_stitch
        self.__current_stitch = Stitch(self.__player_count)
        self.__round += 1
        if self.__round > self.total_stitches:
            self.__round = 0
            self.__state = GameState.IDLE
        """determine winner, next player, give stitch to player"""
        return old_stitch  # kann ausgewertet und dem gewinner gegeben werden

    def get_card_stacks(self):
        # no check for correctness! only call after check (on start)
        if len(GameManager.ALL_CARDS) % self.player_count: raise ValueError("wrong number of players")
        stacks = [[] for _ in range(self.player_count)]
        card_per_player = len(GameManager.ALL_CARDS) / self.player_count
        open_p = [x for x in range(self.player_count)]
        for c in GameManager.ALL_CARDS:
            p = random.randint(0, len(open_p)-1)
            stacks[open_p[p]].append(c)
            if len(stacks[open_p[p]]) >= card_per_player:
                open_p.pop(p)
        return stacks
    
    def deal_cards(self):
        # no check for correctness! only call after check (on start)
    
