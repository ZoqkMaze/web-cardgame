import unittest
from classes import *

class _Player(Player):
    def choose_card(self):
        return super().choose_card()


class TestPlayer(unittest.TestCase):

    # @classmethod
    # def setUpClass(cls):
    #     return super().setUpClass()
    
    def test_game_score(self):
        player = _Player()
        player.add_game_score(10)
        self.assertEqual(player.get_game_score(), 10, "should be 10")
        player.add_game_score(34)
        self.assertEqual(player.get_game_score(), 10+34, "should be 44")

    def test_get_cards(self):
        player = _Player()
        card = Card(Game.RED, Game.MAX_RANK - 1)
        card2 = Card(Game.YELLOW, Game.MIN_PLAYER+1)
        self.assertEqual(player.cards, [], "player should'nt have cards")
        player.add_card(card)
        self.assertTrue(player.has_card(card), "player should have card")
        self.assertFalse(player.has_card(card2), "found wrong card")
        self.assertEqual(player.cards, [card], "player should habe card")
        self.assertEqual(player.number_of_cards(), 1, "player should have 1 card")
        self.assertTrue(player.has_color(Game.RED), "color not found")
        self.assertFalse(player.has_color(Game.YELLOW), "color found")

        player.add_card(card2)
        player.remove_card(card)
        self.assertTrue(player.has_card(card2))
        self.assertTrue(player.has_color(Game.YELLOW))   
        self.assertFalse(player.has_card(card))
        self.assertFalse(player.has_color(Game.RED))

        player.clear_cards()
        self.assertEqual(player.number_of_cards(), 0)

class TestSpecialCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.red_card = Card(Game.RED, 1)
        cls.red_witch = Card(Game.RED, 11)
        cls.green_witch = Card(Game.GREEN, 11)
        cls.green_queen = Card(Game.GREEN, 12)
        cls.blue_witch = Card(Game.BLUE, 11)
        cls.yellow_witch = Card(Game.YELLOW, 11)
        cls.jokers = [Card(Game.BLANCK, 0) for _ in range(4)]
        return super().setUpClass()
    
    def test_flags_and_score(self):
        stitch = Stitch(3)
        player = _Player()
        stitch.play_card(self.red_witch)
        self.assertEqual(stitch.get_flags(), [Game.RED_FLAG])
        stitch.play_card(self.red_card)
        stitch.play_card(self.green_queen)
        self.assertEqual(stitch.get_flags(), [Game.RED_FLAG, Game.HIGH_FLAG])

        player.get_stitch(stitch)
        self.assertEqual(player.get_score(), 12)
        self.assertEqual(player.flags, [Game.RED_FLAG, Game.HIGH_FLAG])

        next_stitch = Stitch(3)
        next_stitch.play_card(self.green_witch)
        next_stitch.play_card(self.blue_witch)
        next_stitch.play_card(self.yellow_witch)

        player.get_stitch(next_stitch)
        self.assertEqual(player.get_score(), 0)
        self.assertEqual(player.flags, [Game.RED_FLAG, Game.HIGH_FLAG, Game.LOW_FLAG, Game.BLUE_FLAG, Game.YELLOW_FLAG])
    
    def test_spell(self):
        player = _Player()
        player._Player__red_cards = 13
        player._Player__flags.append(self.green_queen.flag())
        self.assertEqual(player.has_spell(), Game.MEDIUM_SPELL)
        player._Player__flags.append(self.green_witch.flag())
        self.assertEqual(player.has_spell(), Game.HIGH_SPELL)

        player.clear_cards()
        self.assertEqual(player.has_spell(), Game.NO_SPELL)

    def test_joker_stitch(self):
        stitch = Stitch(4)
        [stitch.play_card(self.jokers[i]) for i in range(4)]
        self.assertEqual(stitch.evaluate(), 0)

        stitch = Stitch(5)
        [stitch.play_card(self.jokers[i]) for i in range(3)]
        stitch.play_card(self.red_card)
        stitch.play_card(self.green_queen)
        self.assertEqual(stitch.evaluate(), 3)

    def test_card_equality(self):
        self.assertEqual(self.red_card, self.red_card)
        self.assertNotEqual(self.red_card, self.red_witch)
        self.assertNotEqual(self.red_witch, self.green_witch)
        self.assertNotEqual(Card(Game.BLANCK, 0), Card(Game.BLANCK, 0))


class TestGame(unittest.TestCase):
    def test_deal_cards(self):
        players = [_Player() for _ in range(4)]
        game = Game(players)
        self.assertEqual(game.get_player_count(), 4)
        game.deal_cards()
        for c in game.cards:
            self.assertEqual(sum([p.has_card(c) for p in players]), 1)
    
    # should test game.play_stitch and game.play_card


if __name__ == "__main__":
    unittest.main()
