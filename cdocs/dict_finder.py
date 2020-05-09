from pathlib import Path
import os
import json


class BadToken(Exception):
    pass


class DictFinder(object):

    def __init__(self, introot:str, docroot:str, path:str, tokensname:str):
        self._docroot = docroot
        self._introot = introot
        self._path = path
        self._tokens_name = tokensname

    def get_tokens(self):
        pointer = os.path.join(self._docroot, self._path)
        tokens = dict()
        tokens = self._find_tokens( self._docroot, pointer, tokens)
        pointer = os.path.join(self._introot, self._path)
        tokens = self._find_tokens( self._introot, pointer, tokens)
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
            return dict()

