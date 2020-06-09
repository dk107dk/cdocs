import abc
from typing import List
from cdocs.contextual_docs import Doc, DocPath

class Lister(metaclass=abc.ABCMeta):
    """
    Lister knows how to list the Doc below a docpath. It doesn't include
    the doc pointed to by the docpath. E.g. for /x/y/z it will return
    [/x/y/z/a.xml, /x/y/z/b.xml] (actually 'a.xml' and 'b.xml') but it
    won't include /x/y/z.xml.
    """

    @abc.abstractmethod
    def list_docs(self, path:DocPath) -> List[Doc]:
        pass


