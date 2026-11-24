# Скат-Шлюз

Проект № 2 для практической работы «Безумное средство передвижения». Стихия — вода.
Автор ТЗ и тестов — Альзоаби Адель Фаридович, БСБО-16-23. Разработчик (роль D) — реализация `skate_lock.py`.

Подвижный шлюз капсулы выравнивает уровень воды перед воротами. Подъём расходует запас,
спуск возвращает часть воды, а крайние участки служат причалами для пополнения бака.

## Структура

| Файл | Назначение |
|---|---|
| [SPEC.md](SPEC.md) | Техническое задание (версия 0.1.3) |
| [TEST_CASES.md](TEST_CASES.md) | Приёмочные сценарии ПТ-01…ПТ-14 |
| [TEST_PLAN.md](TEST_PLAN.md) | План тестирования |
| [REVIEW.md](REVIEW.md) | Журнал ревью |
| [DEMO.md](DEMO.md) | Демонстрационный рейс |
| `skate_lock.py` | Реализация класса `SkateLock` |
| `tests/test_acceptance.py` | Приёмочные тесты автора (14 штук) |
| [BUGREPORT.md](BUGREPORT.md) | Вопросы разработчика к ТЗ и тестам |

## Требования

Python 3.10 или новее. Сторонние библиотеки не нужны.

## Запуск тестов

Из корня проекта:

```sh
python -m unittest discover -s tests -t . -v
```

Ожидается: `Ran 14 tests ... OK`.

Только демонстрационный рейс (ПТ-13):

```sh
python -m unittest tests.test_acceptance.SkateLockAcceptance.test_pt13_round_trip -v
```

## Пример использования

```python
from skate_lock import SkateLock

capsule = SkateLock()
capsule.refill()
capsule.equalize(direction=1)   # подготовка к переходу на участок 1
capsule.cross(direction=1)      # переход
print(capsule.get_state())
# {'section': 1, 'waterline': 4, 'reserve': 3, 'gates_passed': 1}
```

## Интерфейс

- `SkateLock()` — новая капсула: участок 0, уровень 1, запас 4, ворота 0.
- `equalize(direction)`, `cross(direction)` — `direction` только `1` или `-1` точного типа `int`.
- `refill()` — пополнение бака до 6, только на участках 0 и 3.
- `get_state()` — новый словарь `section`, `waterline`, `reserve`, `gates_passed`.

Ошибки: `ValueError` для недопустимого направления; `RuntimeError` (его подклассы
`OutOfCanalError`, `NotEnoughWaterError`, `LevelMismatchError`, `NotAtDockError`) для
отказов по правилам канала. При любой ошибке состояние не меняется.

Открытые вопросы к ТЗ — в [BUGREPORT.md](BUGREPORT.md).
