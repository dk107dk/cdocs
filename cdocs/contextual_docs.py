import abc
from typing import NewType, Dict, Callable, Union, Optional, List


# Doc is the contextual documentation content
Doc = NewType("Doc", str)

# DocPath is a relative path structure that points to
# a contextual documentation doc. A DocPath is like
# /x/y/z. It can have a leading '/' char, or not. DocPath
# are passed in from outside the library.
DocPath = NewType("DocPath", str)

# FilePath is the actual physical file path that contains Doc
# content.
FilePath = NewType("FilePath", str)

# JsonDict is a dict with string keys with either a
# string value or a function that takes a string and returns
# a string. At this time the only such function is
# ContextualDocs.get_doc. JsonDict are for tokens and labels.
# Only tokens JsonDict have callable members.
JsonDict = NewType("JsonDict", Dict[str, Union[str, Callable[[str], str]]])

# a Path is either a DocPath or a FilePath. in some cases
# a helper may need to recieve or treat as one or the other
# where another helper might need or treat the other way.
Path = NewType("Path", Union[DocPath, FilePath])


class ContextualDocs(metaclass=abc.ABCMeta):
    """
    See the README.md file for description of the library and
    these methods.
    """

    @abc.abstractmethod
    def get_concat_doc(self, path: DocPath) -> Optional[Doc]:
        pass

    @abc.abstractmethod
    def get_compose_doc(self, path: DocPath) -> Optional[Doc]:
        pass

    @abc.abstractmethod
    def get_doc(self, path: DocPath) -> Optional[Doc]:
        pass

    @abc.abstractmethod
    def get_labels(
        self,
        path: DocPath,
        recurse: Optional[bool] = True,
        addlabels: Optional[bool] = True,
    ) -> Optional[JsonDict]:
        pass

    @abc.abstractmethod
    def get_tokens(self, path: DocPath, recurse: Optional[bool] = True) -> JsonDict:
        pass

    @abc.abstractmethod
    def list_docs(self, path: DocPath) -> List[Doc]:
        pass

    @abc.abstractmethod
    def list_next_layer(self, path: DocPath) -> List[Doc]:
        pass
