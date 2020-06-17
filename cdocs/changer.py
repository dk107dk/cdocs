import abc
from typing import Optional
import datetime

class Changer(metaclass=abc.ABCMeta):
    """
    Changer knows how to hold a last change date
    """

    @abc.abstractmethod
    def get_last_change(self) -> datetime:
        pass

    @abc.abstractmethod
    def set_last_change(self) -> None:
        pass

    @abc.abstractmethod
    def reset_last_change(self, dt:datetime, root:Optional[str]=None) -> None:
        pass



