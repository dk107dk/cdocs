from cdocs.cdocs import Cdocs, DocNotFoundException, BadDocPath
from cdocs.context import Context
from cdocs.simple_config import SimpleConfig
from cdocs.context_metadata import ContextMetadata
import unittest
import os
import logging

class REPL(object):

    def __init__(self):
        self._config = None
        self._metadata = None
        self._context = None
        self._continue = True
        self._debug = False
        self._logger = logging.getLogger('')


    def setup(self, configpath:str=None):
        d = input("want to debug during load? (y/n) ")
        if (d=='y'):
            self.debug()
        metadata = None
        self._config = SimpleConfig(configpath)
        self._metadata = ContextMetadata(self._config)
        self._context = Context(self._metadata)

    def loop(self):
        print("\n")
        while self._continue:
            cmd = input("cmd: ")
            if cmd == "quit":
                self.quit()
            elif cmd == "read":
                self.read()
            elif cmd == "root info":
                self.root_info()
            elif cmd == "list":
                self.list()
            elif cmd == "roots":
                self.roots()
            elif cmd == "debug":
                self.debug()
            else:
                print("\nHelp:")
                print("   read")
                print("   list")
                print("   roots")
                print("   root info")
                print("   debug")
                print("   quit")

    def debug(self):
        if self._debug:
            self._logger.setLevel(level=logging.WARN)
            self._logger.warning("Set level to WARN")
            self._debug = False
        else:
            self._logger.setLevel(level=logging.DEBUG)
            self._logger.debug("Set level to DEBUG")
            self._debug = True

    def read(self):
        roots = self._get_roots()
        docpath = input("docpath: ")
        doc = ""
        try:
            if len(roots) >= 1:
                doc = self._context.get_doc_from_roots(roots, docpath)
            else:
                doc = self._context.get_doc(docpath)
            print("\ndoc: ")
            print(f"{doc}")
        except BadDocPath as e:
            print(f"Error: {e}")

    def _get_roots(self):
        roots = input("which roots (Csv or return for all): ")
        print("roots are: " + roots)
        roots = [] if roots == "" else roots.split(",")
        print(f"roots are: {roots}")
        return roots

    def list(self):
        roots = self._get_roots()
        docpath = input("docpath: ")
        docs = []
        if len(roots) >= 1:
            docs = self._context.list_docs_from_roots(roots, docpath)
        else:
            docs = self._context.list_docs(docpath)
        print("\ndocs: ")
        for doc in docs:
            print(f"   {doc}")

    def roots(self):
        roots = self._config.get_items("docs")
        print("\nroots:")
        for root in roots:
            print(f"   {root}")

    def root_info(self):
        print("\nroot info not available in Cdocs")
        pass

    def quit(self):
        self._continue = False


if __name__ == "__main__":
    repl = REPL()
    repl.setup()
    repl.loop()


