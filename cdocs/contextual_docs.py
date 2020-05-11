import abc
from typing import NewType, Dict, Callable, Union


# Doc is the contextual documentation content
Doc = NewType('Doc', str)

# DocPath is a relative path structure that points to
# a contextual documentation doc. A DocPath is like
# /x/y/z. It can have a leading '/' char, or not. DocPath
# are passed in from outside the library.
DocPath = NewType('DocPath', str)

# FilePath is the actual physical file path that contains Doc
# content. FilePath are for internal use only.
FilePath = NewType('FilePath', str)

# JsonDict is a dict with string keys with either a
# string value or a function that takes a string and returns
# a string. At this time the only such function is
# ContextualDocs.get_doc. JsonDict are for tokens and labels.
# Only tokens JsonDict have callable members.
JsonDict = NewType('JsonDict', Dict[str, Union[str,Callable[[str],str]]])

# DocVersion is a string indicating a revision of the docs
# in the public and internal trees
DocsVersion = NewType('DocsVersion', str)

# DocsName is the name of the corpus. A corpus named by DocsName
# has an impied or explicit DocVersion.
DocsName = NewType('DocsName', str)


class ContextualDocs(metaclass=abc.ABCMeta):
    """
    See the README.md file for description of the library and
    these methods.
    """

    @abc.abstractmethod
    def get_concat_doc(self, path:DocPath) -> Doc:
        pass

    @abc.abstractmethod
    def get_compose_doc(self, path:DocPath) -> Doc:
        pass

    @abc.abstractmethod
    def get_doc(self, path:DocPath) -> Doc:
        pass

    @abc.abstractmethod
    def get_labels(self, path:DocPath) -> JsonDict:
        pass



