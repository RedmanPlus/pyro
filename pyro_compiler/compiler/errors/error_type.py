from enum import Enum, auto


class MessageType(Enum):
    ...


class ErrorType(MessageType):
    TEST_ERROR = auto()
    ILLEGAL_VARIABLE_NAME = auto()
    UNKNOWN_TOKEN = auto()
    MISMATCHING_INDENT = auto()
    ILLEGAL_IF_CONSTRUCT = auto()
    ILLEGAL_DECLARATION = auto()
    MISSING_TOKEN = auto()
    MISSMATCH_PARENS_LESS = auto()
    MISSMATCH_PARENS_MORE = auto()
    MISSMATCH_TOKEN = auto()
    EMPTY_SCOPE = auto()
    UNKNOWN_VARIABLE = auto()
    CALLABLE_ARGUMENT_ERROR = auto()
    DOES_NOT_EXIST = auto()
    UNKNOWN_CALL_PARAMETER = auto()


error_to_message: dict[ErrorType, str] = {
    ErrorType.TEST_ERROR: "This is a test error",
    ErrorType.ILLEGAL_VARIABLE_NAME: "Variable name cannot start with digits",
    ErrorType.UNKNOWN_TOKEN: "Unknown token: '{token}'",
    ErrorType.MISMATCHING_INDENT: "Indentation missmatch, must be {required} spaces, but got {got}",
    ErrorType.ILLEGAL_IF_CONSTRUCT: "If-statement set up incorrectly: {reason}",
    ErrorType.ILLEGAL_DECLARATION: "Variable declaration set up incorrectly: {reason}",
    ErrorType.MISSING_TOKEN: "Missing '{missing}' for the {stmt_type} statement",
    ErrorType.MISSMATCH_PARENS_LESS: "Some parentheses are not closed",
    ErrorType.MISSMATCH_PARENS_MORE: "Closing non-existing parentheses",
    ErrorType.MISSMATCH_TOKEN: "Expected {expected_type} here, but got {got_type}",
    ErrorType.EMPTY_SCOPE: "Missing scope declarations for the {stmt_type} statement",
    ErrorType.UNKNOWN_VARIABLE: "Variable {varname} used before assignment",
    ErrorType.CALLABLE_ARGUMENT_ERROR: "Cannot mix positional and keyword arguments, first positional, than keyword",
    ErrorType.DOES_NOT_EXIST: "{missing_type} does not exist",
    ErrorType.UNKNOWN_CALL_PARAMETER: "Unknown call parameter by the name {param_name} was supplied to the {callable}",
}


class WarningType(MessageType):
    TEST_WARNING = auto()


warning_to_message: dict[WarningType, str] = {
    WarningType.TEST_WARNING: "This is a test warning"
}
