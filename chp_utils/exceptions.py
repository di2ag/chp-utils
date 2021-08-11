class GeneralApiErrorException(Exception):
    def __init__(self, resp, message=''):
        self.resp = resp
        self.message = message
        super().__init__(self.message)


class SriNodeNormalizerException(GeneralApiErrorException):
    def __init__(self, resp, url, query, message=''):
        self.resp = resp
        self.url = url
        self.query = query
        self.message = message
        super().__init__(self.resp, self.message)

    def __str__(self):
        string = f'Url: {self.url} returned error with status code: {self.resp.status_code} '
        string += f' for query: {self.query}.'
        string += f' Query returned: {self.resp.content}. Could not normalize nodes.'
        return string

class SriOntologyKpException(GeneralApiErrorException):
    def __init__(self, resp, url, query, message=''):
        self.resp = resp
        self.url = url
        self.query = query
        self.message = message
        super().__init__(self.resp, self.message)

    def __str__(self):
        string = f'Url: {self.url} returned error with status code: {self.resp.status_code} '
        string += f' for query: {self.query}.'
        string += f' Query returned: {self.resp.content}. Could not get ontology descendents.'
        return string
