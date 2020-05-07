from logging import Filter


class QuietDownElasticsearch(Filter):
    """ Don't log INFO level Elasticsearch """
    def filter(self, record):
        if record.name == 'elasticsearch' and record.levelname == 'INFO':
            return False
        return True


class is404Error(Filter):
    """ Log 404 Errors """
    def filter(self,record):
        if record.status_code == 404:
            print(record.request.method)
            return True
        return False


class isNot404Error(Filter):
    """ Omit 404 Errors """
    def filter(self,record):
        if record.status_code != 404:
            print(record.request.method)
            return True
        return False
