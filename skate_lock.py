"""«Скат-Шлюз»: плавучая капсула с подвижным шлюзом в ступенчатом канале.

Реализация по SPEC.md версии 0.1.3 (стихия «Вода»).
Публичный интерфейс: класс :class:`SkateLock`.
"""
from __future__ import annotations

from typing import Dict, Final, Tuple

__all__ = [
    "SkateLock",
    "SkateLockError",
    "OutOfCanalError",
    "NotEnoughWaterError",
    "LevelMismatchError",
    "NotAtDockError",
]


class SkateLockError(RuntimeError):
    """Базовая доменная ошибка симулятора (остаётся ``RuntimeError``, Т-09)."""


class OutOfCanalError(SkateLockError):
    """Соседнего участка в выбранном направлении нет (выход за границы)."""


class NotEnoughWaterError(SkateLockError):
    """В баке не хватает воды для подъёма уровня."""


class LevelMismatchError(SkateLockError):
    """Уровень шлюза не совпадает с уровнем соседнего участка."""


class NotAtDockError(SkateLockError):
    """Пополнение бака возможно только на причале."""


class SkateLock:
    """Капсула «Скат-Шлюз».

    Один вызов команды выполняет один шаг симуляции. Любая команда,
    завершившаяся ошибкой, не меняет состояние капсулы (Т-09).
    """

    #: Уровни воды участков канала 0..3 (Т-01).
    SECTION_LEVELS: Final[Tuple[int, ...]] = (1, 4, 2, 5)
    #: Участки-причалы (Т-01).
    DOCKS: Final[Tuple[int, ...]] = (0, 3)
    #: Вместимость бака (Т-02).
    TANK_CAPACITY: Final[int] = 6

    _START_SECTION: Final[int] = 0
    _START_WATERLINE: Final[int] = 1
    _START_RESERVE: Final[int] = 4

    def __init__(self) -> None:
        """Создаёт капсулу на участке 0 в начальном состоянии (Т-02)."""
        self._section: int = self._START_SECTION
        self._waterline: int = self._START_WATERLINE
        self._reserve: int = self._START_RESERVE
        self._gates_passed: int = 0

    # Состояние
    def get_state(self) -> Dict[str, int]:
        """Возвращает независимый снимок состояния (Т-03)."""
        return {
            "section": int(self._section),
            "waterline": int(self._waterline),
            "reserve": int(self._reserve),
            "gates_passed": int(self._gates_passed),
        }

    # Команды
    def equalize(self, direction: int) -> None:
        """Готовит шлюз к переходу: выравнивает уровень воды (Т-04).

        Подъём тратит из бака столько воды, на сколько растёт уровень.
        Спуск возвращает в бак половину разности (с округлением вниз),
        излишек сверх вместимости бака сбрасывается.

        :raises ValueError: направление не ``1`` и не ``-1`` точного типа int.
        :raises OutOfCanalError: соседнего участка нет.
        :raises NotEnoughWaterError: для подъёма не хватает запаса.
        """
        target = self._neighbour(direction)
        diff = self.SECTION_LEVELS[target] - self._waterline

        new_reserve = self._reserve
        if diff > 0:
            if self._reserve < diff:
                raise NotEnoughWaterError(
                    f"not enough water: required {diff}, have {self._reserve}"
                )
            new_reserve = self._reserve - diff
        elif diff < 0:
            new_reserve = min(self.TANK_CAPACITY, self._reserve + (-diff) // 2)

        self._reserve = new_reserve
        self._waterline = self.SECTION_LEVELS[target]

    def cross(self, direction: int) -> None:
        """Переходит через ворота на соседний участок (Т-05).

        :raises ValueError: недопустимое направление.
        :raises OutOfCanalError: соседнего участка нет.
        :raises LevelMismatchError: уровень шлюза не равен уровню соседа.
        """
        target = self._neighbour(direction)
        if self._waterline != self.SECTION_LEVELS[target]:
            raise LevelMismatchError(
                f"waterline {self._waterline} does not match "
                f"section {target} level {self.SECTION_LEVELS[target]}"
            )
        self._section = target
        self._gates_passed += 1

    def refill(self) -> None:
        """Пополняет бак до вместимости; допустимо только на причале (Т-06).

        :raises NotAtDockError: капсула не на причале.
        """
        if self._section not in self.DOCKS:
            raise NotAtDockError(f"section {self._section} is not a dock")
        self._reserve = self.TANK_CAPACITY

    # Внутренняя реализация
    def _neighbour(self, direction: int) -> int:
        """Проверяет направление и возвращает индекс соседнего участка.

        Сначала проверяется направление (ValueError), затем наличие
        соседа (RuntimeError) — порядок из Т-09.
        """
        # type(...) is int: подклассы (bool, Direction) запрещены (Т-08).
        if type(direction) is not int or direction not in (-1, 1):
            raise ValueError(f"direction must be exactly 1 or -1, got {direction!r}")
        target = self._section + direction
        if not 0 <= target < len(self.SECTION_LEVELS):
            raise OutOfCanalError(
                f"no section {target} next to section {self._section}"
            )
        return target
