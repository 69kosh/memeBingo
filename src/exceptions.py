
class OtherValidationError(Exception):
    def __init__(self, errors: list) -> None:
        self._errors = errors
        super().__init__()

    def errors(self):
        return self._errors