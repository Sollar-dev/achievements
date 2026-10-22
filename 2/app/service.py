import logging

log = logging.getLogger("app")


class InvalidNumberError(Exception):
    pass


class DuplicateNumberError(Exception):
    # исключительная ситуация #1: число уже поступало
    pass


class PreviousNumberError(Exception):
    # исключительная ситуация #2: число на единицу меньше уже обработанного
    pass


class NumberService:
    def __init__(self, repository, max_n):
        self.repo = repository
        self.max_n = max_n

    def process(self, n):
        # bool в питоне тоже считается int, поэтому True/False отсекаем отдельно
        if not isinstance(n, int) or isinstance(n, bool) or not 0 <= n <= self.max_n:
            log.error("Некорректное число: %r", n)
            raise InvalidNumberError(f"некорректное число: нужно целое от 0 до {self.max_n}")

        if self.repo.exists(n):
            log.error("Ошибка #1: число %d уже поступало", n)
            raise DuplicateNumberError(f"число {n} уже поступало")

        if self.repo.exists(n + 1):
            log.error("Ошибка #2: число %d на единицу меньше уже обработанного числа %d", n, n + 1)
            raise PreviousNumberError(f"число {n} на единицу меньше уже обработанного числа {n + 1}")

        if not self.repo.save(n):
            # такое может быть, если два одинаковых запроса пришли одновременно:
            # оба прошли проверку, но UNIQUE в базе пропустил только один
            log.error("Ошибка #1: число %d уже поступало", n)
            raise DuplicateNumberError(f"число {n} уже поступало")

        log.info("Число %d обработано, ответ %d", n, n + 1)
        return n + 1
