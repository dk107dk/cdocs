from cdocs.cdocs import Cdocs, DocNotFoundException, BadDocPath
import unittest
import os
import logging

PATH:str = "/Users/davidkershaw/dev/cdocs/docs/example"
PATH2:str = "/Users/davidkershaw/dev/cdocs/docs/internal"
JSON:str = "/Users/davidkershaw/dev/cdocs/docs/json"
APIUI:str = "/Users/davidkershaw/dev/cdocs/docs/apiui"

class CdocsTests(unittest.TestCase):

    logger = logging.getLogger('')
    def _debug(self):
        self.logger.setLevel(level=logging.DEBUG)
        self.logger.debug("SET THE LEVEL TO DEBUG")


    noise = True
    def _print(self, text:str) -> None:
        if self.noise:
            print(text)

    def off(self) -> bool:
        return False

    def test_notfounds(self):
        self._print(f"CdocsTests.test_notfounds")
        if self.off(): return
        cdocs1 = Cdocs(PATH)
        doc = cdocs1.get_404()
        self._print(f"test_notfounds: for {cdocs1}: {doc}")
        found = doc.find("NO")
        self.assertNotEqual(found, -1, msg=f"not found in {cdocs1.rootname} must include 'NO'")
        cdocs2 = Cdocs(PATH2)
        doc = cdocs2.get_404()
        self._print(f"test_notfounds: for {cdocs2}: {doc}")
        found = doc.find("TRY")
        self.assertNotEqual(found, -1, msg=f"not found in {cdocs2.rootname} must include 'NO'")

    def test_get_doc_root_path(self):
        self._print(f"CdocsTests.test_get_doc_root_path")
        if self.off(): return
        cdocs = Cdocs(PATH)
        path = cdocs.get_doc_root()
        self._print(f"test_get_doc_root_path: docs root is {path}")
        self.assertTrue( os.path.exists(path), msg="docs root must exsit" )
        self.assertEqual(path, PATH)

    def test_bad_path_arg(self):
        self._print(f"CdocsTests.test_bad_path_arg")
        if self.off(): return
        cdocs = Cdocs(PATH)
        self._print("test_bad_path_arg: checking for exceptions")
        with self.assertRaises(DocNotFoundException):
            cdocs.get_doc(None)
        with self.assertRaises(BadDocPath):
            cdocs.get_doc("test.xml")

    def test_get_doc(self) :
        self._print(f"CdocsTests.test_get_doc")
        if self.off(): return
        #self._debug()
        docpath = "/app/home/teams/todos/assignee"
        cdocs = Cdocs(PATH)
        txt = cdocs.get_doc(docpath)
        self.assertIsNotNone(txt, msg=f"doc at {docpath} must not be none")
        self._print(f"test_get_doc: doing get_docs. the doc txt is: {txt}")
        point = txt.find("assignee in company starstruck!")
        self.assertNotEqual(-1,point, msg=f"txt: {txt} must include 'assignee in company starstruck!'")
        point = txt.find("my app name: you should see: my app's name is fruit")
        self.assertNotEqual(-1,point, msg="must include 'my app name: you should see: my app's name is fruit'")

    def test_get_doc_not_found(self) :
        self._print(f"CdocsTests.test_get_doc_not_found")
        if self.off(): return
        docpath = "/app/home/teams/todos/assignee/fish"
        cdocs = Cdocs(PATH)
        txt = cdocs.get_doc(docpath)
        self._print(f"test_get_doc_not_found: the doc found is: {txt}")
        self.assertIsNotNone(txt, msg=f"doc at {docpath} must not be none")
        self._print(f"test_get_doc_not_found: doing get_docs. the doc txt is: {txt}")
        point = txt.find("NO")
        self.assertNotEqual(-1,point, msg=f"txt: {txt} must include 'Not found!'")


    def test_add_labels_to_tokens(self):
        self._print(f"CdocsTests.test_add_labels_to_tokens")
        if self.off(): return
        docpath = "/app/home/teams/todos/assignee#new_assignee"
        cdocs = Cdocs(PATH)
        tokens = {}
        tokens = cdocs._add_labels_to_tokens(docpath, tokens)
        self._print(f"test_add_labels_to_tokens: tokens are {tokens}.")
        self.assertIn("label__my_app_name", tokens, msg=f"must include labels_my_app_name")

    def test_get_plus_paths(self):
        self._print(f"CdocsTests.test_get_plus_paths")
        if self.off(): return
        docpath = "/app/home/teams/todos/assignee+edit_assignee"
        cdocs = Cdocs(PATH)
        paths = cdocs._get_plus_paths(docpath)
        self._print(f"test_get_plus_paths: plus paths: {paths}")
        self.assertIn("/app/home/teams/todos/assignee#edit_assignee", paths, msg=f"1. plus paths must include edit_assignee")
        docpath = "/app/home/teams/todos/assignee#new_assignee+edit_assignee"
        paths = cdocs._get_plus_paths(docpath)
        self._print(f"plus paths: {paths}")
        self.assertIn("/app/home/teams/todos/assignee#edit_assignee", paths, msg=f"2. plus paths must include edit_assignee")
        docpath = "/app/home/teams/todos/assignee+new_assignee+edit_assignee"
        paths = cdocs._get_plus_paths(docpath)
        self._print(f"plus paths: {paths}")
        self.assertIn("/app/home/teams/todos/assignee#edit_assignee", paths, msg=f"3. plus paths must include edit_assignee")
        self.assertIn("/app/home/teams/todos/assignee#new_assignee", paths, msg=f"4. plus paths must include new_assignee")

    def test_get_doc_with_plus_path(self):
        self._print(f"CdocsTests.test_get_doc_with_plus_path")
        if self.off(): return
        docpath = "/app/home/teams/todos/assignee+new_assignee+edit_assignee"
        cdocs = Cdocs(PATH)
        doc = cdocs.get_doc(docpath)
        self._print(f"test_get_doc_with_plus_path: content of {docpath} is: {doc}")
        na = doc.find("new assignee")
        ea = doc.find("edit assignee")
        a = doc.find("assignee in company")
        self.assertNotEqual(-1, na, msg=f'must include "new assignee" in {doc}')
        self.assertNotEqual(-1, ea, msg=f'must include "edit assignee" in {doc}')
        self.assertNotEqual(-1, a, msg=f'must include "assignee in company" in {doc}')

    def test_get_tokens(self):
        self._print(f"CdocsTests.test_get_tokens")
        if self.off(): return
        docpath = "/app/home/teams/todos/assignee"
        cdocs = Cdocs(PATH)
        tokens = cdocs.get_tokens(docpath)
        self._print(f"test_get_tokens: tokens: {tokens}")
        self.assertIn("company", tokens, msg=f"tokens at {docpath} must include key 'company'")
        self.assertIn("app", tokens, msg=f"tokens at {docpath} must include key 'app'")
        #self.assertIn("other", tokens, msg=f"tokens at {docpath} must include key 'other'")
        company = tokens["company"]
        self.assertEqual(company, "starstruck")

    def test_get_labels(self):
        self._print(f"CdocsTests.test_get_labels")
        if self.off(): return
        docpath = "/app/home/teams/todos/assignee"
        cdocs = Cdocs(PATH)
        labels = cdocs.get_labels(docpath)
        self._print(f"test_get_labels: the labels are: {labels}")
        self.assertIn("app", labels, msg=f"labels at {docpath} must include key 'app'")
        self.assertIn("team", labels, msg=f"labels at {docpath} must include key 'team'")
        self.assertIn("my_app_name", labels, msg=f"labels at {docpath} must include key 'my_app_name'")
        self.assertEqual("my app's name is fruit", labels["my_app_name"], msg=f"label my app name must == my app's name is fruit")
        self.assertEqual("starstruck", labels["company"], msg=f"label company must == starstruck")


    def test_get_labels_no_recurse(self):
        self._print(f"CdocsTests.test_get_labels_no_recurse")
        if self.off(): return
        docpath1 = "/v1/config/names"
        docpath2 = "/v1/config"
        cdocs = Cdocs(APIUI)

        labels = cdocs.get_labels(docpath1)
        self._print(f"test_get_labels: the labels are: {labels}")
        self.assertIn("docroot", labels, msg=f"labels at {docpath1} must include key 'docroot'")
        self.assertIn("formats", labels, msg=f"labels at {docpath1} must include key 'format'")

        labels = cdocs.get_labels(docpath1, False)
        self._print(f"test_get_labels: the labels are: {labels}")
        self.assertIn("docroot", labels, msg=f"labels at {docpath1} must include key 'docroot'")
        self.assertNotIn("formats", labels, msg=f"labels at {docpath1} must not include key 'format'")

        labels = cdocs.get_labels(docpath2, False)
        self._print(f"test_get_labels: the labels are: {labels}")
        self.assertNotIn("docroot", labels, msg=f"labels at {docpath2} must not include key 'docroot'")
        self.assertIn("formats", labels, msg=f"labels at {docpath2} must include key 'format'")

        labels = cdocs.get_labels(docpath2, True)
        self._print(f"test_get_labels: the labels are: {labels}")
        self.assertNotIn("docroot", labels, msg=f"labels at {docpath2} must not include key 'docroot'")
        self.assertIn("formats", labels, msg=f"labels at {docpath2} must include key 'format'")


    def test_get_filename(self):
        self._print(f"CdocsTests.test_get_filename")
        if self.off(): return
        docpath = "/app/home/teams/todos/assignee#new_assignee"
        cdocs = Cdocs(PATH)
        filename = cdocs._pather.get_filename(docpath)
        self._print(f"test_get_filename: filename: {filename}")
        self.assertEqual(filename, "new_assignee", msg=f"filename must be 'new_assignee'")

    def test_get_filename_special_hashmark(self):
        self._print(f"CdocsTests.test_get_filename_special_hashmark")
        if self.off(): return
        docpath = "/app/home/teams/todos/assignee.new_assignee"
        cdocs = Cdocs(PATH)
        cdocs._pather._hashmark = '.'
        filename = cdocs._pather.get_filename(docpath)
        self._print(f"test_get_filename_special_hashmark: filename: {filename}")
        self.assertEqual(filename, "new_assignee", msg=f"filename must be 'new_assignee'")

    def test_get_full_file_path(self):
        self._print(f"CdocsTests.test_get_full_file_path")
        if self.off(): return
        docpath = "/app/home/teams/todos/assignee#new_assignee"
        cdocs = Cdocs(PATH)
        path = cdocs._pather.get_full_file_path(docpath)
        found = path.find("/assignee/new_assignee.xml")
        self._print(f"test_get_full_file_path: found: {found}")
        self.assertNotEqual( -1, found, msg=f"path {path} must end in '/assignee/new_assignee.xml'")

    def test_get_concat_paths(self):
        self._print(f"CdocsTests.test_get_concat_paths")
        if self.off(): return
        docpath = "/app/home/teams/todos/assignee/concat.concat"
        cdocs = Cdocs(PATH)
        paths = cdocs._get_concat_paths(docpath)
        self.assertNotEqual(None, paths, msg=f'cannot get concat paths from {docpath}')
        self._print(f'test_get_concat_paths: paths: {paths}')
        self.assertIn( "/app/home/teams/todos/assignee#new_assignee", paths, msg=f"paths: {paths} must include in '/app/home/teams/todos/assignee#new_assignee'")

    def test_get_concat_doc(self):
        self._print(f"CdocsTests.test_get_concat_doc")
        if self.off(): return
        docpath = "/app/home/teams/todos/assignee/concat.concat"
        cdocs = Cdocs(PATH)
        doc = cdocs.get_concat_doc(docpath)
        na = doc.find("new assignee")
        ea = doc.find("edit assignee")
        self.assertNotEqual(-1, na, msg=f'{docpath} must include "new assignee" in {doc}')
        self.assertNotEqual(-1, ea, msg=f'{docpath} must include "edit assignee" in {doc}')
        self._print(f'test_get_concat_doc: concat doc: {doc}')

    def test_get_compose_doc(self):
        self._print(f"CdocsTests.test_get_compose_doc")
        #if self.off(): return
        docpath = "/app/home/teams/compose.html"
        cdocs = Cdocs(PATH)
        doc = cdocs.get_compose_doc(docpath)
        na = doc.find("new assignee")
        ea = doc.find("edit assignee")
        self.assertNotEqual(-1, na, msg=f'{docpath} must include "new assignee" in {doc}')
        self.assertNotEqual(-1, ea, msg=f'{docpath} must include "edit assignee" in {doc}')
        self._print(f'test_get_compose_doc: compose doc: {doc}')

    def test_get_doc_from_root_with_multiple_ext(self):
        self._print(f"CdocsTests.test_get_doc_from_root_with_multiple_ext")
        if self.off(): return
        docpath = "/app/home"
        cdocs = Cdocs(PATH2)
        doc = cdocs.get_doc(docpath)
        self.assertIsNotNone(doc, msg=f'{docpath} must not return None')
        home = doc.find("This is home in text!")
        self.assertNotEqual(-1, home, msg=f'{docpath} must include "This is home in text!" in {doc}')
        doc = cdocs.get_doc(docpath + "/teams")
        self.assertIsNotNone(doc, msg=f'{docpath} must not return None')
        home = doc.find("<teams>")
        self.assertNotEqual(-1, home, msg=f'{docpath} must include "<teams>" in {doc}')

    def test_concat_json(self):
        self._print(f"\n\n>>>>>>>>>>>>>>>> CdocsTests.test_concat_json")
        if self.off(): return
        docpath = "/app/home+home_screen"
        cdocs = Cdocs(JSON)
        self._print(f"CdocsTests.test_concat_json: root name: {cdocs.rootname}")
        doc = cdocs.get_doc(docpath)
        self.assertIsNotNone(doc, msg=f'{docpath} must not return None')
        self._print(f"CdocsTests.test_concat_json: doc: {doc}\n\n\n")
        home = doc.find('{"how-to-use": "How to use My Home", "header": "Home Screen", "content": "The home screen is where you land after logging in."}')
        self.assertNotEqual(-1, home, msg=f'{docpath} must include the joined json, not: {doc}')

    def test_list_docs(self):
        self._print(f"CdocsTests.test_list_docs")
        docpath = "/app/home/teams"
        cdocs = Cdocs(PATH)
        self._print(f"CdocsTests.test_list_docs. cdocs: {cdocs}")
        docs = cdocs.list_docs(docpath)
        self._print(f"CdocsTests.test_list_docs: docs: {docs}")
        self.assertIsNotNone(docs, msg=f"docpath: {docpath} must not be None")
        self.assertEqual(len(docs), 3, msg=f"len(docs) at {docpath} must be 3")
        self.assertIn("a.json", docs, msg=f"docs {docs} must include a.json")

        self._print(f"CdocsTests.test_list_docs: listing root")
        docs = cdocs.list_docs("/")
        self._print(f"CdocsTests.test_list_docs: docs: {docs}")
        self.assertIsNotNone(docs, msg=f"docpath: {docpath} must not be None")
        self.assertEqual(len(docs), 2, msg=f"len(docs) at {docpath} must be 2")
        self.assertIn("404a.xml", docs, msg=f"docs {docs} must include 404a.xml")

        self._print(f"CdocsTests.test_list_docs: listing empty string -- which is also the root")
        docs = cdocs.list_docs("")
        self._print(f"CdocsTests.test_list_docs: docs: {docs}")
        self.assertIsNotNone(docs, msg=f"docpath: {docpath} must not be None")
        self.assertEqual(len(docs), 2, msg=f"len(docs) at {docpath} must be 2")
        self.assertIn("404a.xml", docs, msg=f"docs {docs} must include 404a.xml")

        self._print(f"CdocsTests.test_list_docs: listing bogus docpath")
        docs = cdocs.list_docs("fish/can or cannot/fly")
        self._print(f"CdocsTests.test_list_docs: docs: {docs}")
        self.assertIsNotNone(docs, msg=f"docpath: {docpath} must not be None")
        self.assertEqual(len(docs), 0, msg=f"len(docs) at {docpath} must be 0")








