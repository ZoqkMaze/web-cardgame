import random
from enum import Enum, auto

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
    RED_FLAG = auto()  # double red points
    BLUE_FLAG = auto()  # clear all points
    YELLOW_FLAG = auto()  # minus 5 points
    LOW_FLAG = auto()  # plus 5 points
    HIGH_FLAG = auto()  # plus 10 points
    NONE_FLAG = auto()  # no effect


class Spell(Enum):
    NO_SPELL = 0
    LOW_SPELL = 20
    MEDIUM_SPELL = 25
    HIGH_SPELL = 30


class SwitchType(Enum):
    CLOCK = "clock"
    REVERSED = "reversed"
    PAIR = "pair"


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
    def queen(self):  # todo: only green 12 is queen?
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

        if self.__winner == -1:
            self.__winner = 0
        elif card.color is self.__color and card > self.__cards[self.__winner]:
            self.__winner = self.__next_index

        self.__next_index += 1
        self.__cards.append(card)
        self.__points += card.points
        flag = card.flag
        if flag != Flag.NONE_FLAG: self.__flags.append(flag)
        if card.color is Color.RED: self.__red_cards += 1
        return
    

class Player:

    MIN_POINTS = 0  # inklusive
    MAX_DOUBLE_POINTS = 15
    HIGH_POINTS = 10
    LOW_POINTS = 5

    START_ID = 0

    def __init__(self, id):
        self.__id = id
        self.__cards: dict[str, Card] = {}
        self.__stitches: list[Stitch] = []
        self.__points = 0  # Punkte über alle Stiche einer Spielrunde
        self.__flags = []
        self.__red_cards = 0
        self.__game_scores = []  # Punkte in jeder Runde
        self.__next_card_id = Player.START_ID
        self.switch_card_ids = []  # should not be protected
    
    @property
    def id(self):
        return self.__id
    
    @property
    def card_dict(self):
        return self.__cards
    
    @property
    def cards(self):
        return list(self.__cards.values())
    
    @property
    def card_ids(self):
        return list(self.__cards.keys())
    
    @property
    def flags(self):
        return self.__flags

    @property
    def number_of_cards(self):
        return len(self.__cards)

    @property
    def total_game_score(self):
        return sum(self.__game_scores)
    
    @property
    def game_scores(self):
        return self.__game_scores
    
    def switched_correct(self, number_of_cards):
        c_ids = []
        for card_id in self.switch_card_ids:
            if not self.has_card_id(card_id) or card_id in c_ids:
                return False
            c_ids.append(card_id)
        if len(c_ids) == number_of_cards:
            return True
        return False

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
        self.__game_scores.append(points)

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

    def pop_card(self, card_id):
        return self.__cards.pop(card_id)
    
    def get_card_by_id(self, card_id):
        return self.__cards[card_id]
    
    def add_cards(self, cards):
        for c in cards:
            self.__cards[f"c{self.__next_card_id}"] = c
            self.__next_card_id += 1
    
    def add_card(self, card):
        next_id = f"c{self.__next_card_id}"
        self.__cards[next_id] = card
        self.__next_card_id += 1
        return next_id
    
    def remove_card_by_id(self, card_id):
        del self.__cards[card_id]
    
    def remove_cards_by_id(self, card_ids):
        for c_id in card_ids: self.remove_card_by_id(c_id)
    
    def clear_cards(self):
        self.__cards = {}
        self.__stitches = []
        self.__points = 0
        self.__flags = []
        self.__red_cards = 0
        self.__next_card_id = 0
        self.switch_card_ids = []


class GameManager:
    # 1. every player: join
    # 2. start
    # 3. every player: switch cards
    # 4. every player: play card
    # 5. finish game
    # 6. goto 2

    MIN_PLAYER = 3  # inclusiv
    MAX_PLAYER = 6  # inclusiv

    SWITCH_CARDS = {
        3: 4,
        4: 3,
        5: 3,
        6: 2,
    }
        
    ALL_CARDS = [
        Card(c, r)
        for c in Color
        for r in range(Card.MIN_RANK+1, Card.MAX_RANK)
        if c is not Color.BLANCK
    ] + [Card(Color.BLANCK, Card.MIN_RANK) for c in Color if c is not Color.BLANCK]

    def __init__(self):
        self.__players: list[Player] = []
        self.__current_player = 0
        self.__state = LobbyState.JOIN

        self.__current_stitch: Stitch = None
        self.__round = 0

        self.__switch_type = 1

        self.__stitch_feedback = lambda winner_id: None
        self.__game_feedback = lambda: None
    
    @property
    def state(self):
        return self.__state

    @property
    def player_ids(self):
        return [p.id for p in self.__players]
    
    @property
    def switch_card_number(self):
        return GameManager.SWITCH_CARDS[self.player_count]
    
    @property
    def current_player_id(self):
        return self.player_ids[self.__current_player]
    
    @property
    def missing_switch_player_ids(self):
        return [p.id for p in self.__players if not p.switched_correct(self.switch_card_number)]
    
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
    
    @property
    def winner_ids(self):
        min_score = min([p.total_game_score for p in self.__players])
        return [p.id for p in self.__players if p.total_game_score == min_score]
    
    @property
    def all_switched(self):
        return all(self.switched_correct(p_id) for p_id in self.player_ids)
    
    @property
    def switch_type(self):
        match self.__switch_type:
            case 1: return SwitchType.CLOCK
            case -1: return SwitchType.REVERSED
            case 2: return SwitchType.PAIR
            case 3: return SwitchType.PAIR
            case _: raise ValueError(f"unknown switch type {self.__switch_type}")
    
    @property
    def stacks(self):
        # no check for correctness! only call after check (on start)
        # returns all shuffled cards on player_count many stacks 
        if len(GameManager.ALL_CARDS) % self.player_count: raise ValueError(f"wrong number of players ({self.player_count}) for {len(GameManager.ALL_CARDS)} cards")
        stacks = [[] for _ in range(self.player_count)]
        card_per_player = len(GameManager.ALL_CARDS) / self.player_count
        open_p = [x for x in range(self.player_count)]
        for c in GameManager.ALL_CARDS:
            p = random.randint(0, len(open_p)-1)
            stacks[open_p[p]].append(c)
            if len(stacks[open_p[p]]) >= card_per_player:
                open_p.pop(p)
        return stacks
    
    def set_switch_type(self, s_type: SwitchType):
        if s_type is SwitchType.CLOCK:
            self.__switch_type = 1
            return
        if s_type is SwitchType.REVERSED:
            self.__switch_type = -1
            return
        if s_type is SwitchType.PAIR:
            if self.player_count == 4:
               self.__switch_type = 2
               return
            if self.player_count == 6:
                self.__switch_type = 3
                return
        return 1
    
    def next_switch_type(self):
        match self.switch_type:
            case SwitchType.CLOCK:
                self.set_switch_type(SwitchType.REVERSED)
            case SwitchType.REVERSED:
                if self.player_count % 2:
                    self.set_switch_type(SwitchType.CLOCK)
                else:
                    self.set_switch_type(SwitchType.PAIR)
            case SwitchType.PAIR:
                self.set_switch_type(SwitchType.CLOCK)
            case _:
                raise ValueError(f"unknown switch type {self.switch_type}")

    def register_stitch_feedback(self, func):
        if callable(func):
            self.__stitch_feedback = func
            return
        return 1
    
    def register_game_feedback(self, func):
        if callable(func):
            self.__game_feedback = func
            return
        return 1
    
    def get_player_by_id(self, player_id):
        return self.__players[self.player_ids.index(player_id)]

    def switched_correct(self, player_id):
        player = self.get_player_by_id(player_id)
        return player.switched_correct(self.switch_card_number)

    def join(self, player: Player):
        if self.__state is LobbyState.JOIN:
            self.__players.append(player)
            return 0
        return 1
    
    def leave(self, player):
        if player not in self.__players:
            return 1
        if self.__state is LobbyState.JOIN:
            self.__players.remove(player)
            return 0
        self.__state = LobbyState.CANCEL
        # todo: handle break
    
    def leave_by_id(self, player_id):
        if player_id not in self.player_ids:
            return 1
        if self.__state is LobbyState.JOIN:
            self.__players.pop(self.player_ids.index(player_id))
            return 0
        self.__state = LobbyState.CANCEL
    
    def start(self):
        # startup for a new game round
        if self.__state not in [LobbyState.JOIN, LobbyState.IDLE]:
            return 1
        if GameManager.MIN_PLAYER <= self.player_count <= GameManager.MAX_PLAYER:
            self.__state = LobbyState.SETUP
            self.__current_player = 0
            self.__current_stitch = Stitch(self.player_count)
            # self.__round = 1
            # [p.clear_cards() for p in self.__players]  # already in deal_cards
            self.deal_cards()
            return
        return 1
    
    def deal_cards(self):
        # no check for correctness! only call after check (on start)
        # todo: check correctness (not multiple calls for stacks)
        [p.clear_cards() for p in self.__players]
        stacks = self.stacks
        [self.__players[i].add_cards(stacks[i]) for i in range(self.player_count)]
        return
    
    def _skip_card_switch(self):
        if self.__state is LobbyState.SETUP:
            self.__state = LobbyState.GAME
            return
        return 1
    
    def switch_cards(self, player_id, card_ids):
        if self.__state is not LobbyState.SETUP:
            return 1
        
        player = self.get_player_by_id(player_id)
        player.switch_card_ids = card_ids[:]
        if self.switched_correct(player_id):
            if self.all_switched: self.apply_switch()
            return 0
        player.switch_card_ids = []
        return 1
    
    def apply_switch(self):
        if not self.__state is LobbyState.SETUP:
            return 1
        
        if not self.all_switched:
            return 1

        switch_card_stacks = [[p.pop_card(c_id) for c_id in p.switch_card_ids] for p in self.__players]
        for i in range(self.player_count):
            self.__players[i].add_cards(switch_card_stacks[(i+self.__switch_type)%self.player_count])

        self.next_switch_type()
        self.__state = LobbyState.GAME
        self.__round = 1
    
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
        
        card = player.get_card_by_id(card_id)
        color = self.current_color

        if color is not Color.BLANCK and card.color is not Color.BLANCK:
            # apply zugzwang
            if player.has_color(color) and card.color is not color:
                return 1
        
        if self.__current_stitch.play_card(card):
            raise ValueError()
        
        player.remove_card_by_id(card_id)
        self.__current_player = (self.__current_player + 1) % self.player_count

        if self.stitch_full:
            self.evaluate_stitch()
            self.__stitch_feedback(self.player_ids[self.__current_player])

        return 0

    def evaluate_stitch(self):
        if not self.stitch_full:
            return 1
        if self.__state is not LobbyState.GAME:
            return 1
        
        self.__current_player = (self.__current_player + self.__current_stitch.winner) % self.player_count
        self.__players[self.__current_player].get_stitch(self.__current_stitch)

        self.__current_stitch = Stitch(self.player_count)
        self.__round += 1

        if self.__round > self.total_stitches:
            self.evaluate_round()

    def evaluate_round(self):
        if self.__state is not LobbyState.GAME:
            return 1
        
        if self.round <= self.total_stitches:
            return 1
        
        spell = max([p.spell.value for p in self.__players])
        if spell:
            for p in self.__players:
                if not p.spell: p.add_game_score(spell)
        else:
            for p in self.__players:
                p.add_game_score(p.score)
        
        self.__game_feedback()
        
        self.__state = LobbyState.IDLE
