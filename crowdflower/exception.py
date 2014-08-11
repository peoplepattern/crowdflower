class CrowdFlowerError(Exception):
    """
    General CrowdFlower error
    """
    def __init__(self, request, response):
        self.request = request
        self.response = response

    def __str__(self):
        return '%s: %d %s at %s' % (
            self.__class__.__name__,
            self.response.status_code,
            self.response.reason,
            self.request.url)

    __repr__ = __str__


class CrowdFlowerJSONError(CrowdFlowerError):
    """
    CrowdFlower JSON parsing error.

    This is raised when JSON is expected from CrowdFlower API,
    but fails to parse for whatever reason.
    """
    def __init__(self, request, response, json_error):
        self.request = request
        self.response = response
        self.json_error = json_error
