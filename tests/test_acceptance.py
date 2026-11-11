"""Приёмочные сценарии из TEST_CASES.md."""
import unittest


class Direction(int):
    """Подкласс int для проверки требования точного типа аргумента."""



class SkateLockAcceptance(unittest.TestCase):
    def setUp(self):
        from skate_lock import SkateLock

        self.capsule = SkateLock()

    def assert_state(self, section, waterline, reserve, gates_passed):
        state = self.capsule.get_state()
        self.assertIsInstance(state, dict)
        self.assertEqual(
            state,
            dict(
                section=section,
                waterline=waterline,
                reserve=reserve,
                gates_passed=gates_passed,
            ),
        )
        for field, value in state.items():
            self.assertIs(type(value), int, field)

    def assert_rejected(self, exception, command, *args):
        before = dict(self.capsule.get_state())
        with self.assertRaises(exception):
            command(*args)
        self.assert_state(**before)

    def travel(self, direction):
        self.assertIsNone(self.capsule.equalize(direction))
        self.assertIsNone(self.capsule.cross(direction))

    def test_pt01_initial_state(self):
        self.assert_state(0, 1, 4, 0)

    def test_pt02_prepare_then_cross(self):
        self.assertIsNone(self.capsule.equalize(direction=1))
        self.assert_state(0, 4, 1, 0)
        self.assertIsNone(self.capsule.cross(direction=1))
        self.assert_state(1, 4, 1, 1)

    def test_pt03_repeat_preparation(self):
        for _ in range(2):
            self.assertIsNone(self.capsule.equalize(1))
            self.assert_state(0, 4, 1, 0)

    def test_pt04_recover_water_with_rounding_down(self):
        self.travel(1)
        self.assertIsNone(self.capsule.equalize(1))
        self.assert_state(1, 2, 2, 1)
        self.assertIsNone(self.capsule.equalize(-1))
        self.assert_state(1, 1, 2, 1)

    def test_pt05_cross_without_preparation(self):
        self.assert_rejected(RuntimeError, self.capsule.cross, 1)
        self.assert_state(0, 1, 4, 0)

    def test_pt06_wrong_gate_after_preparation(self):
        self.travel(1)
        self.assertIsNone(self.capsule.equalize(1))
        self.assert_rejected(RuntimeError, self.capsule.cross, -1)
        self.assert_state(1, 2, 2, 1)

    def test_pt07_not_enough_water_to_raise_level(self):
        self.travel(1)
        self.travel(1)
        self.assert_rejected(RuntimeError, self.capsule.equalize, 1)
        self.assert_state(2, 2, 2, 2)

    def test_pt08_refill_and_reserve_capacity(self):
        self.assertIsNone(self.capsule.refill())
        self.assert_state(0, 1, 6, 0)
        for _ in range(3):
            self.travel(1)
        self.assert_state(3, 5, 1, 3)
        for _ in range(2):
            self.assertIsNone(self.capsule.refill())
            self.assert_state(3, 5, 6, 3)
        self.assertIsNone(self.capsule.equalize(-1))
        self.assert_state(3, 2, 6, 3)
        self.assertIsNone(self.capsule.refill())
        self.assert_state(3, 2, 6, 3)
        self.assertIsNone(self.capsule.cross(-1))
        self.assert_state(2, 2, 6, 4)

    def test_pt09_exact_reserve(self):
        self.assertIsNone(self.capsule.refill())
        self.travel(1)
        self.assertIsNone(self.capsule.equalize(-1))
        self.assert_state(1, 1, 4, 1)
        self.travel(1)
        self.assert_state(2, 2, 3, 2)
        self.assertIsNone(self.capsule.equalize(1))
        self.assert_state(2, 5, 0, 2)
        self.assertIsNone(self.capsule.cross(1))
        self.assert_state(3, 5, 0, 3)

    def test_pt10_refill_away_from_dock(self):
        self.travel(1)
        self.assert_rejected(RuntimeError, self.capsule.refill)
        self.assert_state(1, 4, 1, 1)
        self.travel(1)
        self.assert_state(2, 2, 2, 2)
        self.assert_rejected(RuntimeError, self.capsule.refill)
        self.assert_state(2, 2, 2, 2)

    def test_pt11_direction_and_canal_boundary(self):
        for command in (self.capsule.equalize, self.capsule.cross):
            for direction in (0, 2, -2, True, 1.0, "1", None, Direction(1), Direction(-1)):
                with self.subTest(command=command.__name__, direction=direction):
                    self.assert_rejected(ValueError, command, direction)
            self.assert_rejected(RuntimeError, command, -1)
        self.assert_state(0, 1, 4, 0)

    def test_pt12_snapshots_and_instances_are_independent(self):
        other = type(self.capsule)()
        first = self.capsule.get_state()
        second = self.capsule.get_state()
        initial = dict(section=0, waterline=1, reserve=4, gates_passed=0)
        self.assertIsNot(first, second)
        first["reserve"] = 0
        self.assert_state(0, 1, 4, 0)
        self.assertIsNone(self.capsule.equalize(1))
        self.assert_state(0, 4, 1, 0)
        self.assertEqual(second, initial)
        self.assertEqual(other.get_state(), initial)

    def test_pt13_round_trip(self):
        expected_outbound = ((1, 4, 3, 1), (2, 2, 4, 2), (3, 5, 1, 3))
        expected_return = ((2, 2, 6, 4), (1, 4, 4, 5), (0, 1, 5, 6))

        for trip in range(2):
            with self.subTest(trip=trip + 1):
                self.capsule = type(self.capsule)()
                self.assertIsNone(self.capsule.refill())
                self.assert_state(0, 1, 6, 0)
                for state in expected_outbound:
                    self.travel(1)
                    self.assert_state(*state)

                self.assert_rejected(RuntimeError, self.capsule.equalize, 1)
                self.assert_rejected(RuntimeError, self.capsule.cross, 1)
                self.assertIsNone(self.capsule.refill())
                self.assert_state(3, 5, 6, 3)
                for state in expected_return:
                    self.travel(-1)
                    self.assert_state(*state)

    def test_pt14_refill_preserves_prepared_departure(self):
        self.assertIsNone(self.capsule.equalize(1))
        self.assert_state(0, 4, 1, 0)
        self.assertIsNone(self.capsule.refill())
        self.assert_state(0, 4, 6, 0)
        self.assertIsNone(self.capsule.cross(1))
        self.assert_state(1, 4, 6, 1)
