from cdocs.pather import Pather
from cdocs.reader import Reader
from cdocs.finder import Finder

class Physical(object):
    """
    Physical (along with Config, a subclass of Physical) knows
    which classes should be used to find and read files. The
    default reader, finder, pather and config classes work from
    the local filesystem.
    """

    def __init__(self):
        self._reader:Reader = None
        self._finder:Finder = None
        self._pather:Pather = None

    @property
    def reader(self) -> Reader:
        return self._reader

    @reader.setter
    def reader(self, reader:Reader) -> None:
        self._reader = reader

    @property
    def finder(self) -> Finder:
        return self._finder

    @finder.setter
    def finder(self, finder:Finder) -> None:
        self._finder = finder

    @property
    def pather(self) -> Pather:
        return self._pather

    @pather.setter
    def pather(self, pather:Pather) -> None:
        self._pather = pather


