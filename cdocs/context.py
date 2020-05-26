import abc
from typing import Optional, List, Dict
import logging
from cdocs.config import Config
from cdocs.simple_config import SimpleConfig
from cdocs.simple_filer import SimpleFiler
from cdocs.cdocs import Cdocs
from cdocs.contextual_docs import Doc, DocPath, FilePath, JsonDict, ContextualDocs
from cdocs.multi_context_docs import MultiContextDocs


class ContextMetaData(object):

    def __init__(self, config:Optional[Config]=None):
        self._config = SimpleConfig() if config is None else config
        self._roots:List[str] = [ _[1] for _ in self.config.get_items("docs")]
        self._keyed_roots = { _[0]:_[1] for _ in self.config.get_items("docs")}
        self._root_names = [ _[0] for _ in self.config.get_items("docs")]
        self._accepts = {_[0]:[s for s in _[1].split(",")] for _ in self.config.get_items("accepts")}
        self._accepted_by = dict()
        for k in self._accepts:
            v = self._accepts[k]
            for av in v:
                acceptors = self._accepted_by.get(av)
                if acceptors is None:
                    acceptors = []
                acceptors.append(k)
                self._accepted_by[av] = acceptors

    @property
    def accepted_by(self) -> Dict[str,List[str]]:
        return self._accepted_by

    @property
    def accepts(self) -> Dict[str,List[str]]:
        return self._accepts

    @property
    def roots(self) -> List[FilePath]:
        return self._roots

    @property
    def root_names(self) -> List[str]:
        return self._root_names

    @property
    def keyed_roots(self) -> Dict[str,FilePath]:
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
        self._keyed_cdocs = { k : Cdocs(v, metadata.config, self) for k,v in metadata.keyed_roots.items() }
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

    def get_filetype( self, path:DocPath) -> str:
        return SimpleFiler().get_filetype(path)

    def get_root_names_accepting_path( self, path:DocPath) -> List[str]:
        filetype = self.get_filetype(path)
        l = self.metadata.accepted_by.get(filetype)
        if l is None:
            l = []
        return l

    def filter_root_names_for_path(self, roots:List[str], path:DocPath) -> List[str]:
        filetype = self.get_filetype(path)
        aroots = self.metadata.accepted_by.get(filetype)
        filtered = [item for item in roots if item in aroots]
        if roots != filtered:
            logging.info(f"Context.get_labels_from_roots: filtered {roots} to {filtered}")
        return filtered

    def get_labels_from_roots(self, rootnames:List[str], path:DocPath) ->  Optional[JsonDict]:
        labels = {}
        rootnames = self.filter_root_names_for_path(rootnames, path)
        for _ in rootnames:
            cdocs = self.keyed_cdocs[_]
            labels = { **cdocs.get_labels(path), **labels }
        return labels

    def get_compose_doc_from_roots(self, rootnames:List[str], path:DocPath) -> Optional[Doc]:
        rootnames = self.filter_root_names_for_path(rootnames, path)
        for _ in rootnames:
            cdocs = self.keyed_cdocs[_]
            doc = cdocs.get_compose_doc(path)
            if doc is not None:
                return doc

    def get_concat_doc_from_roots(self, rootnames:List[str], path:DocPath) -> Optional[Doc]:
        rootnames = self.filter_root_names_for_path(rootnames, path)
        for _ in rootnames:
            cdocs = self.keyed_cdocs[_]
            doc = cdocs.get_concat_doc(path)
            if doc is not None:
                return doc

    def get_doc_from_roots(self, rootnames:List[str], path:DocPath) -> Optional[Doc]:
        rootnames = self.filter_root_names_for_path(rootnames, path)
        for _ in rootnames:
            cdocs = self.keyed_cdocs[_]
            doc = cdocs.get_doc(path)
            if doc is not None:
                return doc
            else:
                return None

