from typing import List
from cdocs.contextual_docs import Doc, DocPath
from cdocs.lister import Lister
import os
import logging

class SimpleLister(Lister):

    def __init__(self, cdocs):
        self._cdocs = cdocs

    def list_docs(self, path:DocPath) -> List[Doc]:
        logging.info(f"SimpleLister.list_docs: path: {path}")
        #
        # a docpath points to a directory which may have a sibling file named
        # the same as the directory, but with a file extension.
        #
        # listing the docpath means listing the parent directory's files
        # so docpath:
        #    /x/y/z
        # would list:
        #    /x/y
        # and might return:
        #    /x/y/z.xml
        #    /x/y/fish.xml
        #    /x/y/bats.xml
        # it would not return anything anything like:
        #    /x/y/z/z.xml
        #    /x/y/z/fish.xml
        #    /x/y/z/bats.xml
        #
        # why does it work that way? because /x/y/z is an identifier
        # in concept-space, not a filesystem path. as a concept, it includes
        # materials that explain the space. the materials may require
        # multiple files that are all grouped by the concept /x/y/z. we
        # address the fish.xml and bats.xml files as:
        #    /x/y/z#fish.xml
        #    /x/y/z#bats.xml
        #
        # one way to think about it is that z.xml is the important thing and
        # 'z' the directory is just an indication that the concept described
        # by z.xml contains more things.
        #
        # if /x/y/z/a.xml doesn't have a sibling 'a' directory, is /x/y/z/a
        # still good docpath? yes. that just means that the concept
        # /x/y/z/a doesn't contain any further concepts.
        #
        # all this nets out that z.xml, fish.xml and bats.xml just
        # describe /x/y/z.
        #
        # is that a good way to do it? sure. it works, it makes sense
        # logically and you can get used to it pretty easily.
        #
        apath = path
        if path[0:1] == '/' and path.count('/') >=2 or path[0:1] != '/' and path.count('/') >=1:
            apath = path[0:apath.rindex('/')]
        logging.info(f"SimpleLister.list_docs: apath: {apath}")
        root_path = self._cdocs.get_doc_root()
        logging.info(f"SimpleLister.list_docs: root: {root_path}")
        if apath[0:1] == '/':
            apath = apath[1:]
        the_path = os.path.join(root_path, apath)
        logging.info(f"SimpleLister.list_docs: the_path: {the_path}")
        files = os.listdir(the_path)
        logging.info(f"SimpleLister.list_docs: files: {files}")
        files = [f for f in files if f[0:1] != '.' and os.path.isfile(os.path.join(the_path, f))]
        logging.info(f"SimpleLister.list_docs: returning: {files}")
        return files

