from logging import Filter


class QuietDownElasticsearch(Filter):
    """
    Don't log INFO level Elasticsearch
    """
    def filter(self, record):
        if record.name == 'elasticsearch' and record.levelname == 'INFO':
            return False
        else:
            return True
