import logging
from typing import List
from cdocs.contextual_docs import DocPath, Doc, JsonDict
from cdocs.concatter import Concatter
import json

class SimpleConcatter(Concatter):

    def __init__(self, cdocs): # can't type hint cdocs because circular
        self._cdocs = cdocs

    def concat(self, paths:List[DocPath]) -> Doc:
        result = ''
        for apath in paths:
            if apath.strip() == '':
                pass
            else:
                doc = self._cdocs.get_doc(apath)
                result += self.join(result, doc)
        return Doc(result)

    def join(self, content:str, morecontent:str) -> str:
        if content is None:
            logging.warning("SimpleConcatter.join: content is None. cannot concat.")
            if morecontent is not None:
                return morecontent
            else:
                logging.warn("SimpleConcatter.join: morecontent is also None. cannot concat.")
                return ""
        if morecontent is None:
            logging.warn("SimpleConcatter.join: morecontent is None. cannot concat.")
            return content
        j1 = self._load(content)
        if j1 is None:
            return content + " " + morecontent
        j2 = self._load(morecontent)
        if j2 is None:
            return content + " " + morecontent
        newdict = {**j1, **j2}
        return json.dumps(newdict)

    def _load(self, string) -> JsonDict:
        try:
            return JsonDict(json.loads(string))
        except:
            return None
