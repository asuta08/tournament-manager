class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code

class TournamentError(AppError):
    pass

class TournamentOperationError(TournamentError):
    pass

class TournamentRepositoryError(TournamentError):
    pass

class AuthError(AppError):
    pass