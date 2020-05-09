import abc

class ContextualDocs(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def get_concat_doc(self, path:str) -> str:
        pass

    @abc.abstractmethod
    def get_compose_doc(self, path:str) -> str:
        pass

    @abc.abstractmethod
    def get_doc(self, path:str) -> str:
        pass

    @abc.abstractmethod
    def get_labels(self, path:str) -> dict:
        pass



