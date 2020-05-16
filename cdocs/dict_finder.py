from pathlib import Path
from typing import List
import os
import json
import logging


class BadToken(Exception):
    pass


class DictFinder(object):

    def __init__(self, docroot:str, path:str, tokensname:str):
        self._docroot = docroot
        self._path = path
        self._tokens_name = tokensname

    def get_tokens(self):
        """ first checks "public", then other roots, last "internal". prefered in that order """
        pointer = os.path.join(self._docroot, self._path)
        tokens = dict()
        tokens = self._find_tokens( self._docroot, pointer, tokens)
        return tokens

    def _find_tokens( self, root:str, pointer:str, tokens:dict) -> dict:
        if pointer == "" or pointer is None:
            raise BadDocPath(f"_find_tokens got bad pointer: {pointer} in {root}")
        if pointer == root:
            return tokens
        tfile = os.path.join(pointer, self._tokens_name )
        tdict = self._read_json(tfile)
        tokens = {**tdict, **tokens}
        end = int( pointer.rfind("/") )
        pointer = pointer[0:end]
        return self._find_tokens(root, pointer, tokens)

    def _read_json(self, path):
        try:
            with open(path) as f:
                return json.load(f)
        except FileNotFoundError as e:
            logging.debug(f"DictFinder._read_json: no such file {path}. returning empty dict, as expected.")
            return dict()

