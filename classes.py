
from abc import ABC, abstractmethod
import random
from enum import Enum


class GameState(Enum):
    DEALING = "dealing"
    SWAPING = "swaping"
    PLAYING = "playing"
    EVALUATING = "evaluating"
    def next(self):
        transition = {
            GameState.DEALING: GameState.SWAPING,
            GameState.SWAPING: GameState.PLAYING,
            GameState.PLAYING: GameState.EVALUATING,
            GameState.EVALUATING: GameState.DEALING,
        }
        return transition[self]


class Color(Enum):
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    YELLOW = "yellow"
    BLANCK = "blanck"

    def true_colors():
        return [Color.RED, Color.BLUE, Color.GREEN, Color.YELLOW]


class Game:
    # Zahlen 1 bis 13 in den Farben rot, blau, grün und gelb
    # zusätzlich 4 Narren
    # statt ABC einer logger klasse übergeben, die aufgerufen wird, wenn infos übermittelt werden

    # todo: change constants to enum
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    YELLOW = "yellow"
    BLANCK = "blanck"

    COLORS = [RED, BLUE, GREEN, YELLOW, BLANCK]
    TRUE_COLORS = [RED, BLUE, GREEN, YELLOW]

    RED_FLAG = "double normal points"
    BLUE_FLAG = "clear all points"
    YELLOW_FLAG = "minus 5"
    LOW_FLAG = "plus 5"
    HIGH_FLAG = "plus 10"
    NONE_FLAG = "no effect"

    MIN_RANK = 0  # inklusive
    MAX_RANK = 15  # exklusive

    MIN_POINTS = 0  # inklusive
    MAX_DOUBLE_POINTS = 15
    HIGH_POINTS = 10
    LOW_POINTS = 5

    NO_SPELL = 0
    LOW_SPELL = 20
    MEDIUM_SPELL = 25
    HIGH_SPELL = 30

    MIN_PLAYER = 3  # inclusiv
    MAX_PLAYER = 6  # inclusiv


    def __init__(self, player_count):
        self.__player_count = player_count
        if not Game.MIN_PLAYER <= player_count <= Game.MAX_PLAYER: raise ValueError("wrong player number")
        self.__cards = list(Card(c, r) for c in Game.TRUE_COLORS for r in range(Game.MIN_RANK+1, Game.MAX_RANK)) + list(Card(Game.BLANCK, Game.MIN_RANK) for _ in range(len(Game.TRUE_COLORS)))
        self.__current_stitch: Stitch = Stitch(self.__player_count)
        self.__round = 0
        # self.__total_stitches = len(self.__cards) // self.__player_count  # todo: remove as well
        self.__state = GameState.DEALING
    
    def next_state(self):
        self.__state = self.__state.next()

    def game_status(self):
        return {
            "typ": "game",
            "player_count": self.__player_count,
            "status": self.__state,
            "round": self.__round,
        }

    @property
    def cards(self):
        return self.__cards

    def get_player_count(self):
        return self.__player_count
    
    def play_card(self, card):
        # caller-todo: remove card from player | check card | check player
        """
        stitch_color = self.__current_stitch.get_color()
        zugzwang = stitch_color in Game.TRUE_COLORS and player.has_color(stitch_color)
        while zugzwang and not card.get_color() in [stitch_color, Game.BLANCK]:
        """

        if self.__state is not GameState.PLAYING:
            return 1
        
        # the game does not check for validity -> the player class has to verify!
        if self.__current_stitch.play_card(card):  # stitch is full (or wrong card)
            return 1

        # if stitch is full -> nothing happens -> call new_stitch
        return 0
    
    def new_stitch(self):
        if not self.__current_stitch.is_full():  # includes Game.PLAYING
            return 1
        old_stitch = self.__current_stitch
        self.__current_stitch = Stitch(self.__player_count)
        self.__round += 1
        """determine winner, next player, give stitch to player"""
        return old_stitch  # kann ausgewertet und dem gewinner gegeben werden

    def deal_cards(self):
        if self.__state is not GameState.DEALING:
            return 1
        if len(self.__cards)%self.__player_count: raise ValueError("wrong number of players")
        stacks = [[] for _ in range(self.__player_count)]
        card_per_player = len(self.__cards) / self.__player_count
        open_p = [x for x in range(self.__player_count)]
        for c in self.__cards:
            p = random.randint(0, len(open_p)-1)
            stacks[open_p[p]].append(c)
            if len(stacks[open_p[p]]) >= card_per_player:
                open_p.pop(p)
        self.next_state()
        return stacks
    
    def swap_cards(self):
        if self.__state is not Game.SWAPING:
            return 1
        
        # todo
        self.next_state()
        return 0
    
    def evaluate(self):
        if self.__state is not Game.EVALUATING:
            return 1
        
        # todo
        spell = max([p.has_spell() for p in self.__players])
        if spell:
            for p in self.__players:
                if not p.has_spell(): p.add_game_score(spell)
        else:
            for p in self.__players:
                p.add_game_score(p.get_score())

        self.next_state


class Card:

    def __init__(self, color, rank):
        # todo: finish  initialiser
        self.__changeable = True
        self.__color = None  # Farbe der Karte (einschließlich Narr)
        self.__rank = None  # Zahl der Kare 0..13 (einschließlich Narr)

        if self.set_color(color) or self.set_rank(rank):
            raise KeyError()

        self.__changeable = False
    
    def __gt__(self, other):
        if isinstance(other, Card):
            return self.__rank > other.get_rank()
        return False
    
    def __repr__(self):
        return f"Card<{self.__color}-{self.__rank}>"
    
    def get_color(self):
        return self.__color
    
    def is_color(self, color):
        return self.__color == color
    
    def set_color(self, color):
        if self.__changeable:
            if color in Game.COLORS:
                self.__color = color
                return
        return 1  # Fehler

    def get_rank(self):
        return self.__rank
    
    def set_rank(self, rank):
        if self.__changeable:
            if Game.MIN_RANK <= rank < Game.MAX_RANK:
                self.__rank = rank
                return
        return 1  # Fehler
    
    def points(self):
        return 1 if self.is_color(Game.RED) and self.__rank != 11 else 0
    
    def flag(self):
        if self.is_color(Game.GREEN) and self.__rank == 12: return Game.HIGH_FLAG
        if self.__rank == 11:
            match self.__color:
                case Game.RED: return Game.RED_FLAG
                case Game.BLUE: return Game.BLUE_FLAG
                case Game.GREEN: return Game.LOW_FLAG
                case Game.YELLOW: return Game.YELLOW_FLAG
                case _: return Game.NONE_FLAG
        return Game.NONE_FLAG
    

class Stitch:

    FULL_ERROR = 1
    NO_CARD_ERROR = 2

    def __init__(self, player_count):
        self.__player_count = player_count
        self.__cards: list[Card] = []
        self.__color = Game.BLANCK
        self.__points = 0
        self.__flags = []
        self.__red_cards = 0

    def get_red_cards(self):
        return self.__red_cards
    
    def get_color(self):
        return self.__color
    
    def get_points(self):
        return self.__points
    
    def get_flags(self):
        return self.__flags
    
    def is_full(self):
        return len(self.__cards) == self.__player_count
    
    def play_card(self, card):
        if self.is_full():
            return Stitch.FULL_ERROR
        if isinstance(card, Card):
            if self.__color == Game.BLANCK: self.__color = card.get_color()
            self.__cards.append(card)
            self.__points += card.points()
            flag = card.flag()
            if flag != Game.NONE_FLAG: self.__flags.append(flag)
            if card.is_color(Game.RED): self.__red_cards += 1
            return
        return Stitch.NO_CARD_ERROR
    
    def evaluate(self):
        if self.__player_count == len(self.__cards):
            win_index = 0
            for i, c in enumerate(self.__cards):
                if c.is_color(self.__color) and c > self.__cards[win_index]:
                    win_index = i
            return win_index
        return -1
    

class Player(ABC):
    def __init__(self):
        self.__cards: list[Card] = []
        self.__stitches: list[Stitch] = []
        self.__points = 0  # Punkte über alle Stiche einer Spielrunde
        self.__flags = []
        self.__red_cards = 0
        self.__game_score = 0  # Punkte über alle Spielrunden
    
    @property
    def cards(self):
        return self.__cards
    
    @property
    def flags(self):
        return self.__flags

    @abstractmethod
    def choose_card(self) -> Card:
        # return card to play
        pass

    def get_game_score(self):
        return self.__game_score
    
    def add_game_score(self, points):
        self.__game_score += points

    def has_spell(self):
        if self.__red_cards == Game.MAX_RANK - Game.MIN_RANK - 2:
            if Game.LOW_FLAG in self.__flags:
                if Game.HIGH_FLAG in self.__flags:
                    return Game.HIGH_SPELL
                else:
                    return Game.LOW_SPELL
            if Game.HIGH_FLAG in self.__flags:
                return Game.MEDIUM_SPELL
        return Game.NO_SPELL

    def get_score(self):
        score = min(Game.MAX_DOUBLE_POINTS, 2*self.__points) if Game.RED_FLAG in self.__flags else self.__points
        if Game.LOW_FLAG in self.__flags: score += Game.LOW_POINTS
        if Game.HIGH_FLAG in self.__flags: score += Game.HIGH_POINTS
        if Game.YELLOW_FLAG in self.__flags: score = max(0, score-Game.LOW_POINTS)
        if Game.BLUE_FLAG in self.__flags: score = 0
        return score

    def has_card(self, card):
        return card in self.__cards
    
    def number_of_cards(self):
        return len(self.__cards)
    
    def has_color(self, color):
        for c in self.__cards:
            if c.is_color(color): return True
        return False

    def get_stitch(self, stitch: Stitch):
        self.__stitches.append(stitch)
        self.__points += stitch.get_points()
        self.__flags += stitch.get_flags()
        self.__red_cards += stitch.get_red_cards()
    
    def get_cards(self, cards):
        self.__cards = cards[:]
    
    def get_card(self, card):
        self.__cards.append(card)
    
    def remove_card(self, card):
        self.__cards.remove(card)
    
    def clear_cards(self):
        self.__cards = []
        self.__stitches = []
        self.__points = 0
        self.__flags = []
        self.__red_cards = 0
