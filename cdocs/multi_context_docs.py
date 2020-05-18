import abc
from typing import Optional, List
from cdocs.contextual_docs import Doc, DocPath, JsonDict


class MultiContextDocs(metaclass=abc.ABCMeta):
    """
    MultiContextDocs retrieves docs and labels from one
    or more Cdocs named in a list.
    """

    @abc.abstractmethod
    def get_root_names_accepting_path(self, path:DocPath) -> List[str]:
        pass

    @abc.abstractmethod
    def get_concat_doc_from_roots(self, rootnames:List[str], path:DocPath) -> Optional[Doc]:
        pass

    @abc.abstractmethod
    def get_compose_doc_from_roots(self, rootnames:List[str], path:DocPath) -> Optional[Doc]:
        pass

    @abc.abstractmethod
    def get_doc_from_roots(self, rootnames:List[str], path:DocPath) -> Optional[Doc]:
        pass

    @abc.abstractmethod
    def get_labels_from_roots(self, rootnames:List[str], path:DocPath) ->  Optional[JsonDict]:
        pass

