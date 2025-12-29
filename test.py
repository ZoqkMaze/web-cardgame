import unittest
from classes import *


class TestPlayer(unittest.TestCase):
    
    def test_game_score(self):
        player = Player("")
        player.add_game_score(10)
        self.assertEqual(player.total_game_score, 10, "should be 10")
        player.add_game_score(34)
        self.assertEqual(player.total_game_score, 10+34, "should be 44")

    def test_get_cards(self):
        player = Player("")
        card = Card(Color.RED, Card.MAX_RANK - 1)
        card2 = Card(Color.RED, Card.MIN_RANK+1)
        self.assertEqual(player.cards, [], "player should'nt have cards")
        card_id = player.add_card(card)
        self.assertTrue(player.has_card(card), "player should have card")
        self.assertFalse(player.has_card(card2), "found wrong card")
        self.assertEqual(player.cards, [card], "player should habe card")
        self.assertEqual(player.number_of_cards, 1, "player should have 1 card")
        self.assertTrue(player.has_color(Color.RED), "color not found")
        self.assertFalse(player.has_color(Color.YELLOW), "color found")

        card3 = Card(Color.YELLOW, Card.MIN_RANK+1)
        player.add_card(card3)
        player.remove_card_by_id(card_id)
        self.assertTrue(player.has_card(card3))
        self.assertTrue(player.has_color(Color.YELLOW))   
        self.assertFalse(player.has_card(card))
        self.assertFalse(player.has_color(Color.RED))

        player.clear_cards()
        self.assertEqual(player.number_of_cards, 0)

class TestSpecialCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.red_card = Card(Color.RED, 1)
        cls.red_witch = Card(Color.RED, 11)
        cls.green_witch = Card(Color.GREEN, 11)
        cls.green_queen = Card(Color.GREEN, 12)
        cls.blue_witch = Card(Color.BLUE, 11)
        cls.yellow_witch = Card(Color.YELLOW, 11)
        cls.jokers = [Card(Color.BLANCK, 0) for _ in range(4)]
        return super().setUpClass()
    
    def test_flags_and_score(self):
        stitch = Stitch(3)
        player = Player("")
        stitch.play_card(self.red_witch)
        self.assertEqual(stitch.flags, [Flag.RED_FLAG])
        stitch.play_card(self.red_card)
        stitch.play_card(self.green_queen)
        self.assertEqual(stitch.flags, [Flag.RED_FLAG, Flag.HIGH_FLAG])

        player.get_stitch(stitch)
        self.assertEqual(player.flags, [Flag.RED_FLAG, Flag.HIGH_FLAG])
        self.assertEqual(player.score, 12)

        next_stitch = Stitch(3)
        next_stitch.play_card(self.green_witch)
        next_stitch.play_card(self.blue_witch)
        next_stitch.play_card(self.yellow_witch)

        player.get_stitch(next_stitch)
        self.assertEqual(player.score, 0)
        self.assertEqual(player.flags, [Flag.RED_FLAG, Flag.HIGH_FLAG, Flag.LOW_FLAG, Flag.BLUE_FLAG, Flag.YELLOW_FLAG])
    
    def test_spell(self):
        player = Player("")
        player._Player__red_cards = 13
        player._Player__flags.append(self.green_queen.flag)
        self.assertEqual(player.spell, Spell.MEDIUM_SPELL)
        player._Player__flags.append(self.green_witch.flag)
        self.assertEqual(player.spell, Spell.HIGH_SPELL)

        player.clear_cards()
        self.assertEqual(player.spell, Spell.NO_SPELL)

    def test_joker_stitch(self):
        stitch = Stitch(4)
        [stitch.play_card(self.jokers[i]) for i in range(4)]
        self.assertEqual(stitch.winner, 0)

        stitch = Stitch(5)
        [stitch.play_card(self.jokers[i]) for i in range(3)]
        stitch.play_card(self.red_card)
        stitch.play_card(self.green_queen)
        self.assertEqual(stitch.winner, 3)

    def test_card_equality(self):
        self.assertEqual(self.red_card, self.red_card)
        self.assertNotEqual(self.red_card, self.red_witch)
        self.assertNotEqual(self.red_witch, self.green_witch)
        self.assertNotEqual(Card(Color.BLANCK, 0), Card(Color.BLANCK, 0))


class TestGame(unittest.TestCase):
    def test_deal_cards(self):
        players = [Player(f"{i}") for i in range(4)]
        game = GameManager()
        for p in players: game.join(p)
        self.assertEqual(game.player_count, 4)
        game.deal_cards()
        for c in GameManager.ALL_CARDS:
            self.assertEqual(sum([p.has_card(c) for p in players]), 1)
    
    # should test game.play_stitch and game.play_card


if __name__ == "__main__":
    unittest.main()
