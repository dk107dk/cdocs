import abc
from cdocs.contextual_docs import Doc, FilePath
from cdocs.reader import Reader, ReadMetaData


class SimpleReader(Reader):

    def read(self, filepath:FilePath, meta:ReadMetaData=None) -> Doc:
        try:
            with open(filepath) as f:
                return Doc(f.read())
        except FileNotFoundError as fnfe:
            print(f'cannot read: {fnfe}')
            raise DocNotFoundException(f"unreadable path: {filepath}")



