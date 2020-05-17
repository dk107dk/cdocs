from pathlib import Path
import os
import json
import logging
from cdocs.contextual_docs import DocPath, FilePath, JsonDict
from cdocs.finder import Finder

class SimpleFinder(Finder):

    def __init__(self, docroot:str):
        self._docroot = docroot

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
            raise BadDocPath(f"_find_tokens got bad pointer: {pointer} in {root}")
        if pointer == root:
            return tokens
        tfile = os.path.join(pointer, filename)
        tdict = self._read_json(tfile)
        tokens = {**tdict, **tokens}
        end = int( pointer.rfind("/") )
        pointer = pointer[0:end]
        return self._find_tokens(root, pointer, tokens, filename)

    def _read_json(self, path) -> JsonDict:
        try:
            with open(path) as f:
                return JsonDict(json.load(f))
        except FileNotFoundError as e:
            logging.debug(f"DictFinder._read_json: no such file {path}. returning empty dict, as expected.")
            return JsonDict(dict())

