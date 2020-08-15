from pathlib import Path
import os
import json
import logging
from cdocs.contextual_docs import DocPath, FilePath, JsonDict
from cdocs.finder import Finder
from typing import Optional

class FinderException(Exception):
    pass

class SimpleFinder(Finder):

    def __init__(self, cdocs): #can't type hint cdocs
        self._cdocs = cdocs
        self._docroot = cdocs.get_doc_root()

    def find_tokens(self, path:DocPath=None, filename:str="tokens.json", recurse:Optional[bool]=True) -> JsonDict:
        """ first checks "public", then other roots, last "internal". prefered in that order """
        tokens = JsonDict(dict())
        if path is None:
            return tokens
        pointer = os.path.join(self._docroot, path)
        tokens = self._find_tokens( self._docroot, pointer, tokens, filename, recurse)
        return tokens

    def _find_tokens( self, root:FilePath, pointer:FilePath, tokens:JsonDict, filename:str, recurse:Optional[bool]=True ) -> JsonDict:
        if pointer == "" or pointer is None:
            raise FinderException(f"_find_tokens got bad pointer: {pointer} in {root}")
        if pointer == root:
            return tokens
        tfile = self._join(pointer, filename)
        tdict = self._read_json(tfile)
        tokens = {**tdict, **tokens}
        if recurse:
            logging.info(f"simple_finder._find_tokens: recursing on pointer: {pointer}")
            end = int( pointer.rfind("/") )
            logging.info(f"simple_finder._find_tokens: end: {end}")
            pointer = pointer[0:end]
            if pointer == root:
                pointer = pointer + "/"
                recurse = False
            logging.info(f"simple_finder._find_tokens: now pointer: {pointer}")
            return self._find_tokens(root, pointer, tokens, filename, recurse)
        else:
            return tokens

    def _join(self, pointer:FilePath, filename:str) -> FilePath:
        dot = pointer.find(".")
        if dot == -1:
            return os.path.join(pointer, filename)
        else:
            ext = pointer[pointer.rindex('.')+1:]
            p = pointer[0:pointer.rindex('/')]
            logging.info(f"SimpleFinder._join: p: {p}")
            j = os.path.join(p, filename)
            logging.info(f"SimpleFinder._join: j: {j}")
            return j

    def _read_json(self, path) -> JsonDict:
        try:
            with open(path) as f:
                return JsonDict(json.load(f))
        except FileNotFoundError as e:
            logging.debug(f"DictFinder._read_json: no such file {path}. returning empty dict, as expected.")
            return JsonDict(dict())

