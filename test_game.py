""" Basic tests for the `Literature` class. """

from typing import List

import pytest

from actor import Actor
from card import (
    Card,
    Suit,
    HalfSuit,
    Half
)
from constants import SETS
from literature import Literature, Team


def two_player_mock(_: int) -> List[List[Card.Name]]:
    return [
        [Card.Name(r, s) for r in SETS[Half.MINOR] for s in Suit],
        [Card.Name(r, s) for r in SETS[Half.MAJOR] for s in Suit],
        [],
        []
    ]


@pytest.fixture()
def game():
    # Give two players all of the cards
    return Literature(4, hands_fn=two_player_mock, turn_picker=lambda: 0)


def test_game_not_complete(game):
    # There is no winner before the game is complete
    with pytest.raises(ValueError):
        assert game.winner == Team.NEITHER


def test_turn_change(game):
    assert not game.completed
    assert game.turn == Actor(0)
    claims_1 = game.players[1].evaluate_claims()
    c = claims_1.pop(HalfSuit(Half.MAJOR, Suit.DIAMONDS))
    game.commit_claim(Actor(1), c)
    assert game.turn == Actor(1)
    game.switch_turn()
    assert game.turn == Actor(0)


def test_end_game_condition(game):
    for c in game.players[0].evaluate_claims().values():
        game.commit_claim(Actor(0), c)
    assert game.completed
    assert game.winner == Team.EVEN
    # Allow claims after the game is over
    for c in game.players[1].evaluate_claims().values():
        game.commit_claim(Actor(1), c)
    assert game.winner == Team.NEITHER


def test_wrong_claim_conditions(game):
    # Discard if we have all of the cards
    claims_0 = game.players[0].evaluate_claims()
    wrong_player = claims_0.pop(HalfSuit(Half.MINOR, Suit.DIAMONDS))
    wrong_player[Card.Name(3, Suit.DIAMONDS)] = Actor(2)
    game.commit_claim(Actor(0), wrong_player)
    assert game.claims[HalfSuit(Half.MINOR, Suit.DIAMONDS)] == Team.DISCARD
    # Award to the other team if we do not have all of the cards
    claims_1 = game.players[1].evaluate_claims()
    wrong_team = claims_1.pop(HalfSuit(Half.MAJOR, Suit.DIAMONDS))
    for c in wrong_team:
        wrong_team[c] = Actor(0)
    game.commit_claim(Actor(0), wrong_team)
    assert game.claims[HalfSuit(Half.MAJOR, Suit.DIAMONDS)] == Team.ODD
