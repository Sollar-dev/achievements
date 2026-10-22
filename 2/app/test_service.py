import pytest

from service import (
    DuplicateNumberError,
    InvalidNumberError,
    NumberService,
    PreviousNumberError,
)


class FakeRepository:
    # вместо настоящей БД просто множество
    def __init__(self):
        self.numbers = set()

    def exists(self, n):
        return n in self.numbers

    def save(self, n):
        if n in self.numbers:
            return False
        self.numbers.add(n)
        return True


@pytest.fixture
def service():
    return NumberService(FakeRepository(), max_n=100)


def test_returns_number_plus_one(service):
    assert service.process(5) == 6


def test_bounds(service):
    assert service.process(0) == 1
    assert service.process(100) == 101


def test_same_number_twice(service):
    service.process(5)
    with pytest.raises(DuplicateNumberError):
        service.process(5)


def test_number_less_by_one(service):
    service.process(5)
    with pytest.raises(PreviousNumberError):
        service.process(4)


def test_number_greater_by_one_is_ok(service):
    service.process(5)
    assert service.process(6) == 7


@pytest.mark.parametrize("bad", [-1, 101, 3.5, "5", None, True, [1]])
def test_invalid_input(service, bad):
    with pytest.raises(InvalidNumberError):
        service.process(bad)


def test_errors_go_to_log(service, caplog):
    service.process(5)
    with pytest.raises(DuplicateNumberError):
        service.process(5)
    with pytest.raises(PreviousNumberError):
        service.process(4)
    assert "Ошибка #1" in caplog.text
    assert "Ошибка #2" in caplog.text
