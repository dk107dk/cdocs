import abc
from typing import List
from cdocs.contextual_docs import Doc, DocPath


class Lister(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def list_next_layer(self, path: DocPath) -> List[str]:
        """the next layer is the set of docpath names within a folder. e.g.
        dir /x/y/z has a, b, c so list_next_layer returns a, b, c; whereas,
        list_docs would return the files in /x/y that are siblings of /x/y/z"""
        pass

    @abc.abstractmethod
    def list_docs(self, path: DocPath) -> List[Doc]:
        """
        Lister knows how to list the Doc at a docpath. It lists the
        whole set of siblings at the layer. E.g. for /x/y/z it will return
        [/x/y/z/a.xml, /x/y/z/b.xml, /x/y/z.xml]
        """
        pass
