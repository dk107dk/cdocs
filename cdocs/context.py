import abc
from typing import Optional, List, Dict
import logging
from cdocs.config import Config
from cdocs.cdocs import Cdocs
from cdocs.contextual_docs import Doc, DocPath, FilePath, JsonDict, ContextualDocs
from cdocs.multi_context_docs import MultiContextDocs


class ContextMetaData(object):

    def __init__(self, config:Optional[FilePath]=None):
        self._config = Config(config)
        self._roots:List[str] = [ _[1] for _ in self.config.get_items("docs")]
        self._keyed_roots = { _[0]:_[1] for _ in self.config.get_items("docs")}
        self._root_names = [ _[0] for _ in self.config.get_items("docs")]

    @property
    def roots(self) -> List[str]:
        return self._roots

    @property
    def root_names(self) -> List[str]:
        return self._root_names

    @property
    def keyed_roots(self) -> Dict[str,str]:
        return self._keyed_roots

    @property
    def config(self) -> Config:
        return self._config


class Context(ContextualDocs, MultiContextDocs):
    """
    Context provides retrieval against an ordered set of Cdocs.
    Cdocs are internally complete. They do not share or override content.
    get_labels is the exception in that it gets the union of all labels found
    in any of the Cdocs. The value of first use of a label name wins.
    """
    def __init__(self, metadata:ContextMetaData):
        self._metadata = metadata
        self._keyed_cdocs = { k : Cdocs(v, metadata.config) for k,v in metadata.keyed_roots.items() }
        self._cdocs = [ v for k,v in self.keyed_cdocs.items() ]

    @property
    def cdocs(self) -> List[Cdocs]:
        return self._cdocs

    @property
    def keyed_cdocs(self) -> Dict[str, Cdocs]:
        return self._keyed_cdocs

    @property
    def metadata(self) -> ContextMetaData:
        return self._metadata

    # ==== ContextualDocs ==================

    def get_concat_doc(self, path:DocPath) -> Optional[Doc]:
        return self.get_concat_doc_from_roots(self.metadata.root_names, path)

    def get_compose_doc(self, path:DocPath) -> Optional[Doc]:
        return self.get_compose_doc_from_roots(self.metadata.root_names, path)

    def get_doc(self, path:DocPath) -> Optional[Doc]:
        return self.get_doc_from_roots(self.metadata.root_names, path)

    def get_labels(self, path:DocPath) ->  Optional[JsonDict]:
        return self.get_labels_from_roots(self.metadata.root_names, path)

    # ==== MultiContextDocs ==================

    def get_labels_from_roots(self, rootnames:List[str], path:DocPath) ->  Optional[JsonDict]:
        labels = {}
        for _ in rootnames:
            cdocs = self.keyed_cdocs[_]
            labels = { **cdocs.get_labels(path), **labels }
        return labels

    def get_compose_doc_from_roots(self, rootnames:List[str], path:DocPath) -> Optional[Doc]:
        for _ in rootnames:
            cdocs = self.keyed_cdocs[_]
            doc = cdocs.get_compose_doc(path)
            if doc is not None:
                return doc

    def get_concat_doc_from_roots(self, rootnames:List[str], path:DocPath) -> Optional[Doc]:
        for _ in rootnames:
            cdocs = self.keyed_cdocs[_]
            doc = cdocs.get_concat_doc(path)
            if doc is not None:
                return doc

    def get_doc_from_roots(self, rootnames:List[str], path:DocPath) -> Optional[Doc]:
        for _ in rootnames:
            cdocs = self.keyed_cdocs[_]
            doc = cdocs.get_doc(path)
            if doc is not None:
                return doc
            else:
                return None

