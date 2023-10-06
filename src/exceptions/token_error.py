class TokenError(Exception):
    def __init__(self, token: str):
        self.error_name = "TokenError"
        self.error_message = f"Illegal token: {token}"
        super().__init__()

    def __str__(self) -> str:
        return f"{self.error_name}: {self.error_message}"
