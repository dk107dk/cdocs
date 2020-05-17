import abc
from cdocs.contextual_docs import DocPath, JsonDict


class Finder(metaclass=abc.ABCMeta):

    def find_tokens(self, path:DocPath=None, filename:str="tokens.json") -> JsonDict:
        pass

