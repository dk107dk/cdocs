from cdocs.cdocs import Cdocs, DocNotFoundException, BadDocPath
from cdocs.context import Context
from cdocs.simple_config import SimpleConfig
from cdocs.context_metadata import ContextMetadata
import unittest
import os
import logging
from typing import Optional

class Repl(object):

    def __init__(self):
        self._config = None
        self._metadata = None
        self._context = None
        self._continue = True
        self._debug = False
        self._commands = {}
        self._logger = logging.getLogger('')
        self._add_commands()

    def _add_commands(self):
        self.commands["quit"] = self.quit
        self.commands["read"] = self.read
        self.commands["list"] = self.list
        self.commands["roots"] = self.roots
        self.commands["labels"] = self.labels
        self.commands["tokens"] = self.tokens
        self.commands["debug"] = self.debug
        self.commands["help"] = self.help
        self.commands["?"] = self.help

    @property
    def commands(self):
        return self._commands

    @commands.setter
    def commands(self, adict):
        self._commands = adict

    def ask_debug(self):
        d = input("want to debug during load? (y/n) ")
        if (d=='y'):
            self.debug()

    def ask_config(self):
        d = input("want to use your own config? (y/n) ")
        if (d=='y'):
            return input("what path? ")
        return None

    def setup(self, configpath:Optional[str]=None, askdebug:Optional[bool]=True):
        self.ask_debug()
        configpath = self.ask_config()
        metadata = None
        self._config = SimpleConfig(configpath)
        self._metadata = ContextMetadata(self._config)
        self._context = Context(self._metadata)

    def loop(self):
        print("\n")
        while self._continue:
            self._one_loop()

    def _one_loop(self) -> bool:
        cmd = input("cmd: ")
        self.do_cmd(cmd)

    def do_cmd(self, cmd):
        print(f"do_cmd: {cmd}")
        callme = self.commands.get(cmd)
        if callme is None:
            print(f"not sure what {cmd} means")
        else:
            callme()

    def debug(self):
        if self._debug:
            self._logger.setLevel(level=logging.WARN)
            self._logger.warning("Set level to WARN")
            self._debug = False
        else:
            self._logger.setLevel(level=logging.DEBUG)
            self._logger.debug("Set level to DEBUG")
            self._debug = True

    def help(self):
        print("\nHelp:")
        for k,v in self.commands.items():
            print(f"   {k}")
        return True

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
        return True

    def labels(self):
        roots = self._get_roots()
        docpath = input("docpath: ")
        labels = ""
        try:
            if len(roots) >= 1:
                labels = self._context.get_labels_from_roots(roots, docpath)
            else:
                labels = self._context.get_labels(docpath)
            print("\nlabels: ")
            print(f"{labels}")
        except BadDocPath as e:
            print(f"Error: {e}")
        return True

    def tokens(self):
        roots = self._get_roots()
        docpath = input("docpath: ")
        labels = ""
        try:
            if len(roots) >= 1:
                labels = self._context.get_tokens_from_roots(roots, docpath)
            else:
                tokens = self._context.get_tokens(docpath)
            print("\ntokens: ")
            print(f"{tokens}")
        except BadDocPath as e:
            print(f"Error: {e}")
        return True

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
        return True

    def roots(self):
        roots = self._config.get_items("docs")
        print("\nroots:")
        for root in roots:
            print(f"   {root}")
        return True

    def quit(self):
        self._continue = False
        return True


if __name__ == "__main__":
    repl = Repl()
    repl.setup()
    repl.loop()


