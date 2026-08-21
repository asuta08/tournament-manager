class TournamentError(Exception):
    pass

class MatchCreationError(TournamentError):
    pass

class TournamentCreationError(TournamentError):
    pass

class TournamentOperationError(TournamentError):
    pass