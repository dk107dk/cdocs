from cdocs.cdocs import Cdocs, DocNotFoundException, BadDocPath
from cdocs.context import Context
from cdocs.simple_config import SimpleConfig
from cdocs.context_metadata import ContextMetadata
import unittest
import os
import logging
from typing import Optional
import sys


class Repl(object):
    def __init__(self):
        self._config = None
        self._metadata = None
        self._context = None
        self._continue = True
        self._debug = False
        self._commands = {}
        self._logger = logging.getLogger("")
        self._add_commands()
        self._last_roots = []

    def _add_command(self, name, function):
        self.commands[name] = function

    def _add_commands(self):
        self.commands["quit"] = self.quit
        self.commands["read"] = self.read
        self.commands["list"] = self.list
        self.commands["below"] = self.below
        self.commands["roots"] = self.roots
        self.commands["labels"] = self.labels
        self.commands["tokens"] = self.tokens
        self.commands["debug"] = self.debug
        self.commands["help"] = self.help
        self.commands["reload"] = self.reload
        self.commands["config"] = self.config
        self.commands["?"] = self.help

    @property
    def commands(self):
        return self._commands

    @commands.setter
    def commands(self, adict):
        self._commands = adict

    def ask_debug(self):
        d = self._input("want to debug during load? (y/n) ")
        if d == "y":
            self.debug()

    def ask_config(self):
        d = self._input("want to use your own config? (y/n) ")
        if d == "y":
            return self._input("what path? ")
        return None

    def setup(self, configpath: Optional[str] = None, askdebug: Optional[bool] = True):
        if askdebug:
            self.ask_debug()
        if configpath is None:
            configpath = self.ask_config()
        self._config = SimpleConfig(configpath)
        self._metadata = ContextMetadata(self._config)
        self._context = Context(self._metadata)

    def loop(self):
        print("\n")
        while self._continue:
            self._one_loop()

    def _one_loop(self) -> bool:
        cmd = self._input(">> ")
        self.do_cmd(cmd)

    def do_cmd(self, cmd):
        callme = self.commands.get(cmd)
        if callme is None:
            print("")
        else:
            callme()

    def config(self):
        cfg = f"{os.getcwd()}{os.sep}{self._metadata.config.get_config_path()}"
        self._response(cfg)

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
        for k, v in self.commands.items():
            self._response(k)
        return True

    def reload(self):
        self.setup(askdebug=False, configpath=self._metadata.config.get_config_path())

    def read(self):
        roots = self._get_roots()
        docpath = self._input("docpath: ")
        doc = ""
        try:
            if len(roots) >= 1:
                doc = self._context.get_doc_from_roots(roots, docpath)
            else:
                doc = self._context.get_doc(docpath)
            self._response(doc)
            print("\n")
        except BadDocPath as e:
            print(f"Error: {e}")
        return True

    def labels(self):
        roots = self._get_roots()
        docpath = self._input("docpath: ")
        labels = ""
        try:
            if len(roots) >= 1:
                labels = self._context.get_labels_from_roots(roots, docpath)
            else:
                labels = self._context.get_labels(docpath)
            self._response(labels)
        except BadDocPath as e:
            print(f"Error: {e}")
        return True

    def tokens(self):
        roots = self._get_roots()
        docpath = self._input("docpath: ")
        tokens = ""
        try:
            if len(roots) >= 1:
                tokens = self._context.get_tokens_from_roots(roots, docpath)
            else:
                tokens = self._context.get_tokens(docpath)
            self._response(tokens)
        except BadDocPath as e:
            print(f"Error: {e}")
        return True

    def _get_roots(self):
        pres = (
            f"[return] for {self._last_roots} or " if len(self._last_roots) != 0 else ""
        )
        roots = self._input(f"which roots (csv or {pres}'all'): ")
        if roots == "":
            roots = self._last_roots
        elif roots == "all":
            roots = [root[0] for root in self._config.get_items("docs")]
        else:
            roots = roots.split(",")
        self._last_roots = roots
        for root in roots:
            self._response(root)
        return roots

    def list(self):
        roots = self._get_roots()
        docpath = self._input("docpath: ")
        docs = []
        if len(roots) >= 1:
            docs = self._context.list_docs_from_roots(roots, docpath)
        else:
            docs = self._context.list_docs(docpath)
        for doc in docs:
            self._response(doc)
        return True

    def below(self):
        roots = self._get_roots()
        docpath = self._input("docpath: ")
        docs = []
        if len(roots) >= 1:
            docs = self._context.list_next_layer_from_roots(roots, docpath)
        else:
            docs = self._context.list_next_layer(docpath)
        for doc in docs:
            self._response(doc)
        return True

    def roots(self):
        roots = self._config.get_items("docs")
        for root in roots:
            self._response(root)
        return True

    def quit(self):
        self._continue = False
        return True

    def _response(self, text: str) -> None:
        sys.stdout.write(f"\033[92m {text}\033[0m\n")

    def _input(self, prompt: str) -> str:
        try:
            response = input(f"{prompt}\033[93m")
            print("\033[0m ")
            return response.strip()
        except KeyboardInterrupt:
            return "quit"


if __name__ == "__main__":
    repl = Repl()
    repl.setup()
    repl.loop()
