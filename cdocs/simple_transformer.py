import logging
from typing import Optional, Dict
from jinja2 import Template
from cdocs.contextual_docs import DocPath, FilePath, JsonDict
from cdocs.simple_config import SimpleConfig
from cdocs.transformer import Transformer
from cdocs.contextual_docs import DocPath
import inflect

class SimpleTransformer(Transformer):

    def __init__(self, cdocs): # can't type hint cdocs because circular
        self._cdocs = cdocs
        self._engine = inflect.engine()

    def _plural(self, word):
        return self._engine.plural(word)

    def _cap(self, word):
        return word.capitalize()

    def _article(self, word):
        return self._engine.a(word)

    def transform(self, content:str, path:DocPath=None, \
                   tokens:Optional[Dict[str,str]]=None, transform_labels=True) -> str:
        if content is None:
            logging.info("SimpleTransformer.transform: cannot transform None. returning ''")
            return None
        if path is None:
            raise BadDocPath("you must provide the DocPath")
        filetype = self._cdocs.filer.get_filetype(path)
        # more filetypes could go here, but for now this is good.
        # todo: make this list a config option?
        if filetype in ['html','concat','cdocs','xml','md','txt','xhtml','yaml','json','js']:
            if tokens is None:
                tokens:JsonDict = self._cdocs.get_tokens(path)
            if path is not None and transform_labels:
                tokens = self._cdocs._add_labels_to_tokens(path, tokens)
            tokens["get_doc"] = self._cdocs.get_doc
            tokens["get_compose_doc"] = self._cdocs.get_compose_doc
            tokens["get_concat_doc"] = self._cdocs.get_concat_doc
            tokens["plural"] = self._plural
            tokens["cap"] = self._cap
            tokens["article"] = self._article
            tokens["docroot"] = self._cdocs.get_doc_root()
            if self._cdocs.context is not None:
                tokens["get_concat_doc_from_roots"] = self._cdocs.context.get_concat_doc_from_roots
                tokens["get_compose_doc_from_roots"] = self._cdocs.context.get_compose_doc_from_roots
                tokens["get_doc_from_roots"] = self._cdocs.context.get_doc_from_roots
                tokens["get_labels_from_roots"] = self._cdocs.context.get_labels_from_roots
                logging.info("SimpleTransformer.transform: added multi root methods on context to template tokens")
            try:
                template = Template(content)
                content = template.render(tokens)
            except Exception as e:
                logging.info(f"SimpleTransformer.transform: couldn't transform content: {e}")
        return content


