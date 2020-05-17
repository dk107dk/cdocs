import abc
from cdocs.contextual_docs import DocPath, JsonDict


class Finder(metaclass=abc.ABCMeta):
    """
    Finder knows how to collect and aggregate JsonDict. by default
    it finds them in the local filesystem.
    """

    def find_tokens(self, path:DocPath=None, filename:str="tokens.json") -> JsonDict:
        pass

