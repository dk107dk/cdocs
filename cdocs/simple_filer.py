import logging
from typing import Union
from cdocs.contextual_docs import DocPath, FilePath
from cdocs.filer import Filer

class SimpleFiler(Filer):

    def __init__(self):
        self._binary = ["gif","jpg","jpeg","png","pdf"]

    def get_filetype( self, path:Union[DocPath,FilePath]) -> str:
        filetype = ''
        if path.find('/') == -1:
            filetype = 'cdocs'
        else:
            last = path.rindex('/')
            if last == -1:
                filetype = 'cdocs'
            else:
                filename = path[last:]
                ext = filename.find('.')
                if ext == -1:
                    filetype = 'cdocs'
                else:
                    filetype = filename[ext+1:]
        return filetype

    def is_probably_not_binary(self, path:Union[DocPath,FilePath] ) -> bool:
        filetype = self.get_filetype(path)
        return filetype not in self._binary


