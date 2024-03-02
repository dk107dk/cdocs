import abc
from typing import Optional, List
from cdocs.contextual_docs import Doc, DocPath, JsonDict


class MultiContextDocs(metaclass=abc.ABCMeta):
    """
    MultiContextDocs retrieves docs and labels from one
    or more Cdocs named in a list.
    """

    @abc.abstractmethod
    def get_root_names_accepting_path(self, path: DocPath) -> List[str]:
        """
        returns root names that work with docpath in the get_docs method
        based on the doc's extension.
            /x/y/z would work with any root taking "cdocs".
            /x/y/z.html would work with any root taking "html".
        note that any docpath with a dotted extension is unacceptable for
        get_docs in a "cdocs" root. docpath with dotted extensions are
        fine for get_docs on roots that are declared to handle other formats.

        ".config" and dotted extension compose docs have methods that
        permit them in "cdocs" roots.

        accepts is set in the config.ini as a csv.

        formats is for dicovering files identified by cdocs docpaths. if
        you pass a docpath in cdocs format without extensions, the formats
        configuration values are checked by appending them as extensions.

        so accepts determines which roots we look in and formats determines
        what extensions we check when the docpath doesn't include any.
        extensions.
        """
        pass

    @abc.abstractmethod
    def get_concat_doc_from_roots(
        self, rootnames: List[str], path: DocPath
    ) -> Optional[Doc]:
        pass

    @abc.abstractmethod
    def get_compose_doc_from_roots(
        self, rootnames: List[str], path: DocPath
    ) -> Optional[Doc]:
        pass

    @abc.abstractmethod
    def get_doc_from_roots(
        self,
        rootnames: List[str],
        path: DocPath,
        notfound: Optional[bool] = True,
        splitplus: Optional[bool] = True,
    ) -> Optional[Doc]:
        pass

    @abc.abstractmethod
    def get_labels_from_roots(
        self, rootnames: List[str], path: DocPath, recurse: Optional[bool] = True
    ) -> Optional[JsonDict]:
        pass

    @abc.abstractmethod
    def get_tokens_from_roots(
        self, rootnames: List[str], path: DocPath, recurse: Optional[bool] = True
    ) -> Optional[JsonDict]:
        pass

    @abc.abstractmethod
    def list_docs_from_roots(
        self, rootnames: List[str], path: DocPath
    ) -> Optional[JsonDict]:
        pass
