import unittest
from classes import *


class TestCard(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.red_card = Card(Color.RED, 12)
        cls.red_witch = Card(Color.RED, 11)
        cls.green_witch = Card(Color.GREEN, 11)
        cls.green_queen = Card(Color.GREEN, 12)
        cls.blue_witch = Card(Color.BLUE, 11)
        cls.yellow_witch = Card(Color.YELLOW, 11)
        cls.jokers = [Card(Color.BLANCK, 0) for _ in range(4)]
    
    def test_all_cards(self):
        self.assertEqual(len(GameManager.ALL_CARDS), 60)

    def test_card_equality(self):
        self.assertEqual(self.red_card, self.red_card)
        self.assertNotEqual(self.red_card, self.red_witch)
        self.assertNotEqual(self.red_witch, self.green_witch)
        self.assertNotEqual(self.jokers[0], self.jokers[1])
    
    def test_special_cards(self):
        self.assertTrue(self.red_witch.witch)
        self.assertTrue(self.green_witch.witch)
        self.assertFalse(self.red_card.witch)
        self.assertFalse(self.green_queen.witch)

        self.assertTrue(self.green_queen.queen)
        self.assertFalse(self.green_witch.queen)
        self.assertTrue(self.red_card.queen)
    
    def test_change(self):
        self.assertTrue(self.red_card.set_color(Color.BLANCK))
        self.assertEqual(self.red_card.color, Color.RED)
        self.assertTrue(self.green_witch.set_rank(12))
        self.assertFalse(self.green_witch.queen)


class TestStitch(unittest.TestCase):

    def test_play_card(self):
        stitch = Stitch(3)
        self.assertEqual(stitch.color, Color.BLANCK)
        self.assertEqual(stitch.winner, -1)
        stitch.play_card(Card(Color.BLANCK, 0))
        self.assertEqual(stitch.color, Color.BLANCK)
        self.assertEqual(stitch.winner, 0)
        stitch.play_card(Card(Color.RED, 5))
        self.assertEqual(stitch.color, Color.RED)
        self.assertEqual(stitch.winner, 1)
        stitch.play_card(Card(Color.YELLOW, 6))
        self.assertEqual(stitch.color, Color.RED)
        self.assertEqual(stitch.winner, 1)

        self.assertTrue(stitch.full)
        self.assertTrue(stitch.play_card(Card(Color.BLANCK, 4)))
        self.assertEqual(stitch.winner, 1)


class TestPlayer(unittest.TestCase):
    
    def test_game_score(self):
        player = Player("")
        player.add_game_score(10)
        self.assertEqual(player.total_game_score, 10, "should be 10")
        player.add_game_score(34)
        self.assertEqual(player.total_game_score, 10+34, "should be 44")

    def test_cards(self):
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
        card_id3 = player.add_card(card3)
        player.remove_card_by_id(card_id)
        self.assertTrue(player.has_card(card3))
        self.assertTrue(player.has_color(Color.YELLOW))   
        self.assertFalse(player.has_card(card))
        self.assertFalse(player.has_color(Color.RED))

        self.assertEqual(player.pop_card(card_id3), card3)
        self.assertEqual(player.number_of_cards, 0)

        player.add_card(card2)
        player.clear_cards()
        self.assertEqual(player.number_of_cards, 0)
        self.assertEqual(player.cards, [])
        self.assertEqual(player.card_ids, [])
        self.assertEqual(player.card_dict, {})
    
    def test_switch(self):
        player = Player("")
        self.assertFalse(player.switched_correct(3))
        c_ids = [player.add_card(Card(Color.RED, 2+i)) for i in range(2)]
        player.switch_card_ids = c_ids[:]
        self.assertFalse(player.switched_correct(3))
        self.assertTrue(player.switched_correct(2))
        player.switch_card_ids.append(c_ids[0])
        self.assertFalse(player.switched_correct(3))
        player.switch_card_ids = c_ids + [player.add_card(Card(Color.YELLOW, 6))]
        self.assertTrue(player.switched_correct(3))


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


class TestGameSetup(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.manager = GameManager()
        cls.players = [Player(f"p{i+1}") for i in range(4)]

    def test_a_join(self):
        self.assertEqual(self.manager.state, LobbyState.JOIN)
        self.assertEqual(self.manager.player_count, 0)
        [self.manager.join(p) for p in self.players]
        self.assertEqual(self.manager.player_count, 4)
        self.assertEqual(self.manager.player_ids, [f"p{i+1}" for i in range(4)])
    
    def test_b_leave(self):
        p = Player("test")
        self.manager.join(Player("tmp_player"))
        self.manager.join(p)
        self.manager.leave_by_id("tmp_player")
        self.manager.leave(p)
        self.assertEqual(self.manager.player_count, 4)
        self.assertNotIn("tmp_player", self.manager.player_ids)
        self.assertNotIn("test", self.manager.player_ids)
    
    def test_c_start(self):
        self.assertEqual(self.manager.round, 0)
        self.manager.start()
        self.assertEqual(self.manager.state, LobbyState.SETUP)
        self.assertEqual(self.manager.total_stitches, 60/4)
        self.assertEqual(self.manager.round, 0)
        for c in GameManager.ALL_CARDS:
            self.assertEqual(sum([p.has_card(c) for p in self.players]), 1)
    
    def test_d_switch_type(self):
        self.assertEqual(self.manager.switch_type, SwitchType.CLOCK)
        self.manager.set_switch_type(SwitchType.REVERSED)
        self.assertEqual(self.manager.switch_type, SwitchType.REVERSED)
        self.manager.next_switch_type()
        self.assertEqual(self.manager.switch_type, SwitchType.PAIR)

    def test_e_switch(self):
        self.assertEqual(self.manager.state, LobbyState.SETUP)
        self.assertEqual(self.manager.switch_card_number, 3)
        self.assertFalse(self.manager.all_switched)

        p = self.players[0]
        self.assertFalse(self.manager.switch_cards(p.id, p.card_ids[:3]))
        self.assertTrue(self.manager.switched_correct(p.id))
        self.assertTrue(p.switched_correct(self.manager.switch_card_number))
        self.assertNotIn(p.id, self.manager.missing_switch_player_ids)

        p = self.players[1]
        self.assertTrue(self.manager.switch_cards(p.id, []))
        self.assertFalse(self.manager.switched_correct(p.id))
        self.assertIn(p.id, self.manager.missing_switch_player_ids)

        self.manager.switch_cards(p.id, p.card_ids[:4])
        self.assertFalse(self.manager.switched_correct(p.id))
        self.manager.switch_cards(p.id, p.card_ids[:2] + p.card_ids[:1])
        self.assertFalse(self.manager.switched_correct(p.id))
        self.manager.switch_cards(p.id, ["x", "y", "z"])
        self.assertFalse(self.manager.switched_correct(p.id))

        # apply switch
        cards = [ p.cards[:3] for p in self.players]
        [self.manager.switch_cards(p.id, p.card_ids[:3]) for p in self.players]
        self.assertFalse(self.manager.all_switched)  # should be false because of the switch
        for i, p in enumerate(self.players):
            self.assertFalse(any([p.has_card(c) for c in cards[i]]))
            self.assertTrue(all([p.has_card(c) for c in cards[(i+2)%4]]))
        self.assertEqual(self.manager.switch_type, SwitchType.CLOCK)
        self.assertEqual(self.manager.state, LobbyState.GAME)
    
    def test_f_wrong_join_and_leave(self):
        self.assertTrue(self.manager.start())
        self.assertTrue(self.manager.join(Player("test")))
        self.assertNotIn("test", self.manager.player_ids)
        self.assertTrue(self.manager.leave(Player("")))
        self.assertTrue(self.manager.leave_by_id("ghjksdsdfj"))
        self.assertFalse(self.manager.leave_by_id("p1"))
        self.assertEqual(self.manager.state, LobbyState.CANCEL)


class TestGamePlay(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.manager = GameManager()
        cls.players = [Player(f"p{i+1}") for i in range(3)]
        cls.manager._GameManager__players = cls.players[:]
        cls.manager._GameManager__state = LobbyState.GAME
        cls.manager._GameManager__current_stitch = Stitch(3)
        cls.manager._GameManager__round = 1

        cls.players[0]._Player__cards = {
            "c1": Card(Color.RED, 14),  # +1
            "c2": Card(Color.BLUE, 14), 
            "c3": Card(Color.BLANCK, 0)
        }
        cls.players[1]._Player__cards = {
            "c1": Card(Color.RED, 7),  # +1
            "c2": Card(Color.RED, 11),  # x2
            "c3": Card(Color.YELLOW, 11)  # -5
        }
        cls.players[2]._Player__cards = {
            "c1": Card(Color.BLANCK, 0),
            "c2": Card(Color.GREEN, 1),
            "c3": Card(Color.RED, 10)  # +1
        }

    def test_a_play_card(self):
        self.assertEqual(self.manager.current_player_id, "p1")
        self.assertFalse(self.manager.play_card("p1", "c1"))  # RED-14
        self.assertTrue(self.manager.play_card("p2", "c3"))  # YELLOW-14 (wrong)
        self.assertTrue(self.manager.play_card("p3", "c3"))  # wrong player
        self.assertFalse(self.manager.play_card("p2", "c2"))  # RED-11
        self.assertEqual(self.manager.current_player_id, "p3")
        self.assertFalse(self.manager.stitch_full)
        self.assertEqual(self.manager.current_color, Color.RED)
        self.assertFalse(self.manager.play_card("p3", "c1"))  # joker

        self.assertNotIn("c1", self.players[0].card_dict)
        self.assertEqual(self.players[0].flags, [Flag.RED_FLAG])
        self.assertEqual(self.players[0].score, 2)
        self.assertEqual(self.manager.round, 2)
        self.assertEqual(self.players[1].flags, [])
        self.assertEqual(self.players[2].score, 0)

        self.assertEqual(self.manager.current_player_id, "p1")
        self.assertFalse(self.manager.play_card("p1", "c3"))  # joker
        self.assertEqual(self.manager.current_color, Color.BLANCK)
        self.assertTrue(self.manager.play_card("p2", "c2"))  # same card as before
        self.assertFalse(self.manager.play_card("p2", "c1"))  # RED-7
        self.assertEqual(self.manager.current_color, Color.RED)
        self.assertTrue(self.manager.play_card("p3", "c2"))  # GREEN-1 (wrong)
        self.assertFalse(self.manager.play_card("p3", "c3"))  # RED-10

        self.assertEqual(self.manager.current_player_id, "p3")
        self.assertEqual(self.players[2].score, 2)
        self.assertEqual(self.manager.round, 3)

        self.manager._GameManager__round = self.manager.total_stitches

        self.assertFalse(self.manager.play_card("p3", "c2"))
        self.assertFalse(self.manager.play_card("p1", "c2"))
        self.assertFalse(self.manager.play_card("p2", "c3"))

        self.assertEqual(self.manager.current_player_id, "p3")
        self.assertEqual(self.players[0].score, 2)
        self.assertEqual(self.players[1].score, 0)
        self.assertEqual(self.players[2].score, 0)

        self.assertEqual(self.manager.state, LobbyState.IDLE)
        self.assertEqual(self.players[0].total_game_score, 2)
        self.assertEqual(self.players[1].total_game_score, 0)
        self.assertEqual(self.players[2].total_game_score, 0)
        self.assertEqual(self.manager.winner_ids, ["p2", "p3"])

    def test_b_new_start(self):
        self.assertFalse(self.manager.start())
        self.assertEqual(self.manager.state, LobbyState.SETUP)


if __name__ == "__main__":
    unittest.main()
