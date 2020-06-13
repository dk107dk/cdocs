from pathlib import Path
import os
import json
import logging
from cdocs.contextual_docs import DocPath, FilePath, JsonDict
from cdocs.finder import Finder

class FinderException(Exception):
    pass

class SimpleFinder(Finder):

    def __init__(self, cdocs): #can't type hint cdocs
        self._cdocs = cdocs
        self._docroot = cdocs.get_doc_root()

    def find_tokens(self, path:DocPath=None, filename:str="tokens.json" ) -> JsonDict:
        """ first checks "public", then other roots, last "internal". prefered in that order """
        tokens = JsonDict(dict())
        if path is None:
            return tokens
        pointer = os.path.join(self._docroot, path)
        tokens = self._find_tokens( self._docroot, pointer, tokens, filename)
        return tokens

    def _find_tokens( self, root:FilePath, pointer:FilePath, tokens:JsonDict, filename:str) -> JsonDict:
        if pointer == "" or pointer is None:
            raise FinderException(f"_find_tokens got bad pointer: {pointer} in {root}")
        if pointer == root:
            return tokens
        logging.info(f"SimpleFinder._find_tokens: root: {root}, pointer: {pointer}, tokens: {tokens}, filename: {filename}")
        tfile = self._join(pointer, filename)
        tdict = self._read_json(tfile)
        tokens = {**tdict, **tokens}
        end = int( pointer.rfind("/") )
        pointer = pointer[0:end]
        return self._find_tokens(root, pointer, tokens, filename)

    def _join(self, pointer:FilePath, filename:str) -> FilePath:
        dot = pointer.find(".")
        if dot == -1:
            return os.path.join(pointer, filename)
        else:
            accepts = self._cdocs.accepts
            ext = pointer[pointer.rindex('.')+1:]
            if ext in accepts:
                p = pointer[0:pointer.rindex('/')]
                logging.info(f"SimpleFinder._join: p: {p}")
                j = os.path.join(p, filename)
                logging.info(f"SimpleFinder._join: j: {j}")
                return j
            else:
                raise FinderException(f"SimpleFinder._join: {pointer} has '.' and {ext} not in {accepts}")

    def _read_json(self, path) -> JsonDict:
        try:
            with open(path) as f:
                return JsonDict(json.load(f))
        except FileNotFoundError as e:
            logging.debug(f"DictFinder._read_json: no such file {path}. returning empty dict, as expected.")
            return JsonDict(dict())

