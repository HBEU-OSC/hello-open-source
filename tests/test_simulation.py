import unittest
from types import SimpleNamespace
from unittest.mock import patch

from snake_game import run_simulations

class FakeGame:
    def __init__(self, winner=None, end_after=1):
        self.over = False
        self.winner = None
        self.expected_winner = winner
        self.end_after = end_after
        self.steps = 0

    def step(self):
        self.steps += 1

        if self.end_after is not None and self.steps >= self.end_after:
            self.over = True
            self.winner = self.expected_winner

class TestSimulation(unittest.TestCase):

    def test_zero_games_raises_error(self):
        with self.assertRaises(ValueError):
            run_simulations(0)

    def test_zero_max_steps_raises_error(self):
        with self.assertRaises(ValueError):
            run_simulations(1, max_steps=0)

    def test_simulation_counts_all_outcomes(self):
        games = [
            FakeGame(winner=SimpleNamespace(name="红")),
            FakeGame(winner=SimpleNamespace(name="绿")),
            FakeGame(winner=SimpleNamespace(name="蓝")),
            FakeGame(winner=None),
            FakeGame(end_after=None),
        ]

        with patch("snake_game.Game", side_effect=games):
            stats = run_simulations(5, max_steps=2)

        self.assertEqual(stats["wins"]["红"], 1)
        self.assertEqual(stats["wins"]["绿"], 1)
        self.assertEqual(stats["wins"]["蓝"], 1)
        self.assertEqual(stats["draws"], 1)
        self.assertEqual(stats["timeouts"], 1)
        self.assertEqual(stats["total"], 5)

if __name__ == "__main__":
    unittest.main()
