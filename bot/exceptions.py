class NoDataException(Exception):
    """Raised whenever there is no data for the bot to work on, i.e. when there are no sentences in db"""
    pass
