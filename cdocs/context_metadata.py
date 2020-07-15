from typing import Optional, List, Dict
import logging
from cdocs.config import Config
from cdocs.simple_config import SimpleConfig
from cdocs.contextual_docs import FilePath


class ContextMetadata(object):

    def __init__(self, config:Optional[Config]=None):
        self._config = SimpleConfig() if config is None else config
        self._roots:List[str] = [ _[1] for _ in self.config.get_items("docs")]
        self._keyed_roots = { _[0]:_[1] for _ in self.config.get_items("docs")}
        self._root_names = [ _[0] for _ in self.config.get_items("docs")]
        self._accepts = {_[0]:[s for s in _[1].split(",")] for _ in self.config.get_items("accepts")}
        self._accepted_by = dict()
        self._load_accepted_by()
        """for k in self._accepts:
            v = self._accepts[k]
            for av in v:
                acceptors = self._accepted_by.get(av)
                if acceptors is None:
                    acceptors = []
                acceptors.append(k)
                self._accepted_by[av] = acceptors
        """
        self._formats = {_[0]:[s for s in _[1].split(",")] for _ in self.config.get_items("formats")}
        self._uses_format = dict()
        for k in self._formats:
            v = self._formats[k]
            for av in v:
                fs = self._uses_format.get(av)
                if fs is None:
                    fs = []
                fs.append(k)
                self._uses_format[av] = fs

    def _load_accepted_by(self):
        logging.info(f"ContextMetadata._load_accepted_by: starting with: {self._accepts}")
        for k,v in self._accepts.items():
            #v = self._accepts[k]
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
    def uses_format(self) -> Dict[str,List[str]]:
        return self._uses_format

    @property
    def formats(self) -> Dict[str,List[str]]:
        return self._formats

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

    @config.setter
    def config(self, config:Config) -> None:
        self._config = config


