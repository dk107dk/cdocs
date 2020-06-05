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
        for k in self._accepts:
            v = self._accepts[k]
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


