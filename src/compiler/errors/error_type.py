from enum import Enum, auto


class MessageType(Enum):
    ...


class ErrorType(MessageType):
    TEST_ERROR = auto()


error_to_message: dict[ErrorType, str] = {ErrorType.TEST_ERROR: "This is a test error"}


class WarningType(MessageType):
    TEST_WARNING = auto()


warning_to_message: dict[WarningType, str] = {WarningType.TEST_WARNING: "This is a test warning"}
