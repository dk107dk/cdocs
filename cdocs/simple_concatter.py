import logging
from typing import List
from cdocs.contextual_docs import DocPath, Doc
from cdocs.concatter import Concatter

class SimpleConcatter(Concatter):

    def __init__(self, cdocs): # can't type hint cdocs because circular
        self._cdocs = cdocs

    # a more sophisticated concatter might assess if some or all DocPath
    # were pointing to JsonDict, and if so combine the dicts
    def concat(self, paths:List[DocPath]) -> Doc:
        result = ''
        for apath in paths:
            if apath.strip() == '':
                pass
            else:
                doc = self._cdocs.get_doc(apath)
                result += '\n' + doc
        return Doc(result)

    # a more capable concatter might check if both were JsonDoc and
    # if so combine them
    def join(self, content:str, morecontent:str) -> str:
        return content + " " + morecontent

