import abc
from typing import Optional, List, Dict, Any
import logging
from cdocs.config import Config
from cdocs.simple_config import SimpleConfig
from cdocs.simple_filer import SimpleFiler
from cdocs.cdocs import Cdocs
from cdocs.contextual_docs import Doc, DocPath, FilePath, JsonDict, ContextualDocs
from cdocs.multi_context_docs import MultiContextDocs
from cdocs.context_metadata import ContextMetadata

class Context(ContextualDocs, MultiContextDocs):
    """
    Context provides retrieval against an ordered set of Cdocs.
    Cdocs are internally complete. They do not share or override content.
    get_labels is the exception in that it gets the union of all labels found
    in any of the Cdocs. The value of first use of a label name wins.
    """
    def __init__(self, metadata:ContextMetadata):
        self._metadata = metadata
        self._keyed_cdocs = { k : Cdocs(v, metadata.config, self) for k,v in metadata.keyed_roots.items() }
        self._cdocs = [ v for k,v in self.keyed_cdocs.items() ]
        self._nosplitplus = None

    @property
    def cdocs(self) -> List[Cdocs]:
        return self._cdocs

    @property
    def keyed_cdocs(self) -> Dict[str, Cdocs]:
        return self._keyed_cdocs

    @property
    def metadata(self) -> ContextMetadata:
        return self._metadata

    # ==== ContextualDocs ==================

    def get_concat_doc(self, path:DocPath) -> Optional[Doc]:
        return self.get_concat_doc_from_roots(self.metadata.root_names, path)

    def get_compose_doc(self, path:DocPath) -> Optional[Doc]:
        return self.get_compose_doc_from_roots(self.metadata.root_names, path)

    def get_doc(self, path:DocPath, notfound:Optional[bool]=True, splitplus:Optional[bool]=True) -> Optional[Doc]:
        return self.get_doc_from_roots(self.metadata.root_names, path, notfound, splitplus)

    def get_labels(self, path:DocPath) ->  Optional[JsonDict]:
        return self.get_labels_from_roots(self.metadata.root_names, path)

    # ==== MultiContextDocs ==================

    def get_filetype( self, path:DocPath) -> str:
        return SimpleFiler(self).get_filetype(path)

    def get_root_names_accepting_path( self, path:DocPath) -> List[str]:
        filetype = self.get_filetype(path)
        l = self.metadata.accepted_by.get(filetype)
        if l is None:
            l = []
        return l

    def filter_root_names_for_path(self, roots:List[str], path:DocPath) -> List[str]:
        filetype = self.get_filetype(path)
        aroots = self.metadata.accepted_by.get(filetype)
        if aroots is None:
            aroots = []
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

    def get_compose_doc_from_roots(self, rootnames:List[str], path:DocPath, notfound:Optional[bool]=True) -> Optional[Doc]:
        rootnames = self.filter_root_names_for_path(rootnames, path)
        for _ in rootnames:
            cdocs = self.keyed_cdocs[_]
            doc = cdocs.get_compose_doc(path)
            if doc is not None:
                return doc
        if notfound:
            return self._get_default_not_found()

    def get_concat_doc_from_roots(self, rootnames:List[str], path:DocPath, notfound:Optional[bool]=True) -> Optional[Doc]:
        rootnames = self.filter_root_names_for_path(rootnames, path)
        for _ in rootnames:
            cdocs = self.keyed_cdocs[_]
            doc = cdocs.get_concat_doc(path)
            if doc is not None:
                return doc
        if notfound:
            return self._get_default_not_found()

    def get_doc_from_roots(self, rootnames:List[str], path:DocPath, notfound:Optional[bool]=True, splitplus:Optional[bool]=True) -> Optional[Doc]:
        """
            rootnames: a list of named roots to search
            path: the docpath. may have hash and plusses
            notfound: if true, return a default notfound if no results
            splitplus: if true, plus concats can be on different roots.
                       i.e. for /x/y/z+a+b /x/y/z, /x/y/z/a, /x/y/z/b
                       can all be on different roots.
        """
        plusmark = self._metadata.config.get("filenames", "plus")
        plus = path.find( plusmark )
        if plus > -1 and splitplus:
            if self._nosplitplus is None:
                nsp = self._metadata.config.get_with_default("defaults","nosplitplus", "")
                self._nosplitplus = nsp.split(',')
            if len(self._nosplitplus) > 0:
                rootnames = [name for name in rootnames if not name in self._nosplitplus]
                print(f"Context.get_doc_from_roots: nsp filtered rootnames: {rootnames}")
            # split into paths and call get_doc_from_roots on each, then concat
            #
            #  /r/o/o/t.html#fish
            # needs to become /r/o/o
            #
            #  /r/o/o/t#fish
            # needs to become /r/o/o/t
            #
            #  /r/o/o/t
            # needs to become /r/o/o/t
            #
            print(f"Context.get_doc_from_roots: path: {path}")
            print(f"Context.get_doc_from_roots: rootnames: {rootnames}")
            print(f"Context.get_doc_from_roots: notfound: {notfound}")
            print(f"Context.get_doc_from_roots: splitplus: {splitplus}")
            paths = path.split(plusmark)
            print(f"Context.get_doc_from_roots: paths: {paths}")
            rootpath = paths[0]
            print(f"Context.get_doc_from_roots: rootpath: {rootpath}")
            hashmark = self._metadata.config.get("filenames", "hashmark")
            print(f"Context.get_doc_from_roots: hashmark: {hashmark}")
            rootpath = rootpath.split( hashmark )[0]
            print(f"Context.get_doc_from_roots: rootpath: {rootpath}")
            paths = [p if p.find(rootpath) > -1 else rootpath + "/" + p for p in paths]
            print(f"Context.get_doc_from_roots: paths: {paths}")
            result = []
            for path in paths:
                print(f"Context.get_doc_from_roots: .... next path: {path}")
                r = self.get_doc_from_roots(rootnames, path, notfound)
                if r is not None:
                    result.append(r)
            if len(result) == 0 and notfound:
                return self._get_default_not_found()
            return "".join(result)
        else:
            rootnames = self.filter_root_names_for_path(rootnames, path)
            logging.info(f"Context.get_doc_from_roots: rootnames: {rootnames}")
            for _ in rootnames:
                cdocs = self.keyed_cdocs[_]
                logging.info(f"Context.get_doc_from_roots: cdocs: {_} -> {cdocs}")
                doc = cdocs.get_doc(path, False)
                logging.info(f"found doc: {type(doc)}")
                if doc is not None:
                    return doc
            if notfound:
                return self._get_default_not_found()

    def _get_default_not_found(self) -> Optional[Doc]:
        notfound = self._metadata.config.get("defaults", "notfound")
        if notfound is None:
            return None
        if notfound.find("/") == -1:
            logging.error(f"Context.get_doc_from_roots: notfound {notfound} should be in form root/docpath. you should fix this.")
            return None
        root = notfound[0:notfound.index("/")]
        docpath = notfound[notfound.index("/"):]
        cdocs = self.keyed_cdocs[root]
        doc = cdocs.get_doc(docpath, False)
        if doc is None:
            logging.error(f"Context.get_doc_from_roots: notfound {notfound} in root: {root} with docpath: {docpath} is None. you should fix this.")
        return doc
