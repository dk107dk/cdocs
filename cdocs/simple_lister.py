from typing import List
from cdocs.contextual_docs import Doc, DocPath
from cdocs.lister import Lister
import os
import logging


class SimpleLister(Lister):
    def __init__(self, cdocs):
        self._cdocs = cdocs

    def list_next_layer(self, path: DocPath) -> List[str]:
        logging.info(f"SimpleLister.list_next_layer: path: {path}")
        apath = path
        if apath[0:1] == "/":
            apath = apath[1:]
        logging.info(f"SimpleLister.list_next_layer: apath: {apath}")
        root_path = self._cdocs.get_doc_root()
        logging.info(f"SimpleLister.list_next_layer: root: {root_path}")
        the_path = os.path.join(root_path, apath)
        logging.info(f"SimpleLister.list_next_layer: the_path: {the_path}")
        if os.path.exists(the_path):
            logging.info("SimpleLister.list_next_layer: the path exists")
            files = os.listdir(the_path)
            logging.info(f"SimpleLister.list_next_layer: files: {files}")
            files = [
                f
                for f in files
                if f[0:1] != "."
                # and os.path.isfile(os.path.join(the_path, f))
            ]
            rf = []
            for f in files:
                dot = f.rfind(".")
                if dot > -1:
                    rf.append(f[0:dot])
                else:
                    rf.append(f)

            logging.info(f"SimpleLister.list_next_layer: files filtered: {rf}")
            return rf
        return []

    def list_docs(self, path: DocPath) -> List[Doc]:
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
        if apath[0:1] == "/":
            apath = apath[1:]
        logging.info(f"SimpleLister.list_docs: apath: {apath}")
        root_path = self._cdocs.get_doc_root()
        logging.info(f"SimpleLister.list_docs: root: {root_path}")
        the_path = os.path.join(root_path, apath)
        logging.info(f"SimpleLister.list_docs: the_path: {the_path}")
        # check if the_path refers to a file path or to a file minus its extension
        if self._name_exists(the_path):
            logging.info("SimpleLister.list_docs: path exists")
            up = the_path[0 : the_path.rindex("/")]
            logging.info(f"SimpleLister.list_docs: up: {up}")
            files = os.listdir(up)
            logging.info(f"SimpleLister.list_docs: files: {files}")
            files = [
                f
                for f in files
                if f[0:1] != "." and os.path.isfile(os.path.join(up, f))
            ]
            logging.info(f"SimpleLister.list_docs: files filtered: {files}")
            return files
        else:
            logging.info(
                f"SimpleLister.list_docs: directory at {the_path} doesn't exist. no files found. returning []."
            )
            return []

    def _name_exists(self, the_path: str) -> bool:
        logging.info(f"SimpleLister._name_exists: {the_path}")
        if os.path.exists(the_path):
            logging.info("SimpleLister._name_exists: the path exists")
            return True
        else:
            logging.info("SimpleLister._name_exists: the path does not exist")
        up = the_path[0 : the_path.rindex("/")]
        if not os.path.exists(up):
            logging.info(f"SimpleLister._name_exists: {the_path} does not exist")
            return False
        else:
            logging.info(f"SimpleLister._name_exists: up: {up} exists")
        name = the_path[the_path.rindex("/") + 1 :]
        logging.info(f"SimpleLister._name_exists: the name is {name}")
        files = os.listdir(up)
        for f in files:
            logging.info(f"SimpleLister._name_exists: checking {f} for {name}")
            if not f.startswith(name):
                logging.info(f"SimpleLister._name_exists: {f} not start with {name}")
                continue
            pre = f[: len(name) + 1]
            logging.info(f"SimpleLister._name_exists: pre: {pre}")
            if pre[len(pre) - 1] == ".":
                return True
        return False
