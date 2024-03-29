from cdocs.cdocs import Cdocs, DocNotFoundException, BadDocPath
import unittest
import os
import logging
from time import sleep

PATH: str = "docs/example"
PATH2: str = "docs/internal"
JSON: str = "docs/json"
APIUI: str = "docs/apiui"


class CdocsTests(unittest.TestCase):
    def test_notfounds(self):
        logging.info("CdocsTests.test_notfounds")
        cdocs1 = Cdocs(PATH)
        doc = cdocs1.get_404()
        logging.info(f"test_notfounds: for {cdocs1}: {doc}")
        found = doc.find("NO")
        self.assertNotEqual(
            found, -1, msg=f"not found in {cdocs1.rootname} must include 'NO'"
        )
        cdocs2 = Cdocs(PATH2)
        doc = cdocs2.get_404()
        logging.info(f"test_notfounds: for {cdocs2}: {doc}")
        found = doc.find("TRY")
        self.assertNotEqual(
            found, -1, msg=f"not found in {cdocs2.rootname} must include 'NO'"
        )

    def test_get_doc_root_path(self):
        logging.info("CdocsTests.test_get_doc_root_path")
        cdocs = Cdocs(PATH)
        path = cdocs.get_doc_root()
        logging.info(f"test_get_doc_root_path: docs root is {path}")
        self.assertTrue(os.path.exists(path), msg="docs root must exsit")
        self.assertEqual(path, PATH)

    def test_bad_path_arg(self):
        logging.info("CdocsTests.test_bad_path_arg")
        cdocs = Cdocs(PATH)
        logging.info("test_bad_path_arg: checking for exceptions")
        with self.assertRaises(DocNotFoundException):
            cdocs.get_doc(None)
        with self.assertRaises(BadDocPath):
            cdocs.get_doc("test.xml")

    def test_get_doc(self):
        logging.info("CdocsTests.test_get_doc")
        docpath = "/app/home/teams/todos/assignee"
        cdocs = Cdocs(PATH)
        txt = cdocs.get_doc(docpath)
        self.assertIsNotNone(txt, msg=f"doc at {docpath} must not be none")
        logging.info(f"test_get_doc: doing get_docs. the doc txt is: {txt}")
        point = txt.find("assignee in company starstruck!")
        self.assertNotEqual(
            -1, point, msg=f"txt: {txt} must include 'assignee in company starstruck!'"
        )
        point = txt.find("my app name: you should see: my app's name is fruit")
        self.assertNotEqual(
            -1,
            point,
            msg="must include 'my app name: you should see: my app's name is fruit'",
        )

    def test_get_doc2(self):
        logging.info("CdocsTests.test_get_doc2")
        docpath = "/app/home/teams/todos/assignee#new_assignee"
        cdocs = Cdocs(PATH)
        txt = cdocs.get_doc(docpath)
        self.assertIsNotNone(txt, msg=f"doc at {docpath} must not be none")
        logging.info(f"test_get_doc2: doing get_docs. the doc txt is: {txt}")
        point = txt.find("new assignee")
        self.assertNotEqual(
            -1, point, msg=f"txt: {txt} must include 'assignee in company starstruck!'"
        )

    def test_get_doc_not_found(self):
        logging.info("CdocsTests.test_get_doc_not_found")
        docpath = "/app/home/teams/todos/assignee/fish"
        cdocs = Cdocs(PATH)
        txt = cdocs.get_doc(docpath)
        logging.info(f"test_get_doc_not_found: the doc found is: {txt}")
        self.assertIsNotNone(txt, msg=f"doc at {docpath} must not be none")
        logging.info(f"test_get_doc_not_found: doing get_docs. the doc txt is: {txt}")
        point = txt.find("NO")
        self.assertNotEqual(-1, point, msg=f"txt: {txt} must include 'Not found!'")

    def test_add_labels_to_tokens(self):
        logging.info("CdocsTests.test_add_labels_to_tokens")
        docpath = "/app/home/teams/todos/assignee#new_assignee"
        cdocs = Cdocs(PATH)
        tokens = {}
        tokens = cdocs._add_labels_to_tokens(docpath, tokens)
        logging.info(f"test_add_labels_to_tokens: tokens are {tokens}.")
        self.assertIn(
            "label__my_app_name", tokens, msg="must include labels_my_app_name"
        )

    def test_get_plus_paths(self):
        logging.info("CdocsTests.test_get_plus_paths")
        docpath = "/app/home/teams/todos/assignee+edit_assignee"
        cdocs = Cdocs(PATH)
        logging.info(f"test_get_plus_paths: docpath {docpath}")
        paths = cdocs._get_plus_paths(docpath)
        logging.info(f"test_get_plus_paths: plus paths: {paths}")
        self.assertIn(
            "/app/home/teams/todos/assignee#edit_assignee",
            paths,
            msg="1. plus paths must include edit_assignee",
        )
        docpath = "/app/home/teams/todos/assignee#new_assignee+edit_assignee"
        logging.info(f"test_get_plus_paths: docpath {docpath}")
        paths = cdocs._get_plus_paths(docpath)
        logging.info(f"test_get_plus_paths: plus paths: {paths}")
        self.assertIn(
            "/app/home/teams/todos/assignee#edit_assignee",
            paths,
            msg="2. plus paths must include edit_assignee",
        )
        docpath = "/app/home/teams/todos/assignee+new_assignee+edit_assignee"
        logging.info(f"test_get_plus_paths: docpath {docpath}")
        paths = cdocs._get_plus_paths(docpath)
        logging.info(f"test_get_plus_paths: plus paths: {paths}")
        self.assertIn(
            "/app/home/teams/todos/assignee#edit_assignee",
            paths,
            msg="3. plus paths must include edit_assignee",
        )
        self.assertIn(
            "/app/home/teams/todos/assignee#new_assignee",
            paths,
            msg="4. plus paths must include new_assignee",
        )

    def test_get_doc_with_plus_path(self):
        logging.info("CdocsTests.test_get_doc_with_plus_path")
        docpath = "/app/home/teams/todos/assignee+new_assignee+edit_assignee"
        cdocs = Cdocs(PATH)
        doc = cdocs.get_doc(docpath)
        logging.info(f"test_get_doc_with_plus_path: content of {docpath} is: {doc}")
        na = doc.find("new assignee")
        ea = doc.find("edit assignee")
        a = doc.find("assignee in company")
        self.assertNotEqual(-1, na, msg=f'must include "new assignee" in {doc}')
        self.assertNotEqual(-1, ea, msg=f'must include "edit assignee" in {doc}')
        self.assertNotEqual(-1, a, msg=f'must include "assignee in company" in {doc}')

    def test_get_tokens(self):
        logging.info("CdocsTests.test_get_tokens")
        docpath = "/app/home/teams/todos/assignee"
        cdocs = Cdocs(PATH)
        tokens = cdocs.get_tokens(docpath)
        logging.info(f"test_get_tokens: tokens: {tokens}")
        self.assertIn(
            "company", tokens, msg=f"tokens at {docpath} must include key 'company'"
        )
        self.assertIn("app", tokens, msg=f"tokens at {docpath} must include key 'app'")
        # self.assertIn("other", tokens, msg=f"tokens at {docpath} must include key 'other'")
        company = tokens["company"]
        self.assertEqual(company, "starstruck")

    def test_get_labels(self):
        logging.info("CdocsTests.test_get_labels")
        docpath = "/app/home/teams/todos/assignee"
        cdocs = Cdocs(PATH)
        labels = cdocs.get_labels(docpath)
        logging.info(f"test_get_labels: the labels are: {labels}")
        self.assertIn("app", labels, msg=f"labels at {docpath} must include key 'app'")
        self.assertIn(
            "team", labels, msg=f"labels at {docpath} must include key 'team'"
        )
        self.assertIn(
            "my_app_name",
            labels,
            msg=f"labels at {docpath} must include key 'my_app_name'",
        )
        self.assertEqual(
            "my app's name is fruit",
            labels["my_app_name"],
            msg="label my app name must == my app's name is fruit",
        )
        self.assertEqual(
            "starstruck", labels["company"], msg="label company must == starstruck"
        )
        #
        # get labels from the top
        #
        self.assertIn(
            "filenames",
            labels,
            msg=f"labels at {docpath} must include key 'filenames' from /",
        )

    def test_get_labels_no_recurse(self):
        logging.info("CdocsTests.test_get_labels_no_recurse")
        docpath1 = "/v1/config/names"
        docpath2 = "/v1/config"
        cdocs = Cdocs(APIUI)

        labels = cdocs.get_labels(docpath1)
        logging.info(f"test_get_labels: the labels are: {labels}")
        self.assertIn(
            "docroot", labels, msg=f"labels at {docpath1} must include key 'docroot'"
        )
        self.assertIn(
            "formats", labels, msg=f"labels at {docpath1} must include key 'format'"
        )

        labels = cdocs.get_labels(docpath1, False)
        logging.info(f"test_get_labels: the labels are: {labels}")
        self.assertIn(
            "docroot", labels, msg=f"labels at {docpath1} must include key 'docroot'"
        )
        self.assertNotIn(
            "formats", labels, msg=f"labels at {docpath1} must not include key 'format'"
        )

        labels = cdocs.get_labels(docpath2, False)
        logging.info(f"test_get_labels: the labels are: {labels}")
        self.assertNotIn(
            "docroot",
            labels,
            msg=f"labels at {docpath2} must not include key 'docroot'",
        )
        self.assertIn(
            "formats", labels, msg=f"labels at {docpath2} must include key 'format'"
        )

        labels = cdocs.get_labels(docpath2, True)
        logging.info(f"test_get_labels: the labels are: {labels}")
        self.assertNotIn(
            "docroot",
            labels,
            msg=f"labels at {docpath2} must not include key 'docroot'",
        )
        self.assertIn(
            "formats", labels, msg=f"labels at {docpath2} must include key 'format'"
        )

    def test_get_filename(self):
        logging.info("CdocsTests.test_get_filename")
        docpath = "/app/home/teams/todos/assignee#new_assignee"
        cdocs = Cdocs(PATH)
        filename = cdocs._pather.get_filename(docpath)
        logging.info(f"test_get_filename: filename: {filename}")
        self.assertEqual(
            filename, "new_assignee", msg="filename must be 'new_assignee'"
        )

    def test_get_filename_special_hashmark(self):
        logging.info("CdocsTests.test_get_filename_special_hashmark")
        docpath = "/app/home/teams/todos/assignee.new_assignee"
        cdocs = Cdocs(PATH)
        cdocs._pather._hashmark = "."
        filename = cdocs._pather.get_filename(docpath)
        logging.info(f"test_get_filename_special_hashmark: filename: {filename}")
        self.assertEqual(
            filename, "new_assignee", msg="filename must be 'new_assignee'"
        )

    def test_get_full_file_path(self):
        logging.info("CdocsTests.test_get_full_file_path")
        docpath = "/app/home/teams/todos/assignee#new_assignee"
        cdocs = Cdocs(PATH)
        logging.info(f"test_get_full_file_path: docpath: {docpath}")
        path = cdocs._pather.get_full_file_path(docpath)
        found = path.find("/assignee/new_assignee.xml")
        logging.info(f"test_get_full_file_path: found: {found}")
        self.assertNotEqual(
            -1, found, msg=f"path {path} must end in '/assignee/new_assignee.xml'"
        )

    def test_get_concat_paths(self):
        logging.info("CdocsTests.test_get_concat_paths")
        docpath = "/app/home/teams/todos/assignee/concat.concat"
        cdocs = Cdocs(PATH)
        paths = cdocs._get_concat_paths(docpath)
        self.assertNotEqual(None, paths, msg=f"cannot get concat paths from {docpath}")
        logging.info(f"test_get_concat_paths: paths: {paths}")
        self.assertIn(
            "/app/home/teams/todos/assignee#new_assignee",
            paths,
            msg=f"paths: {paths} must include in '/app/home/teams/todos/assignee#new_assignee'",
        )

    def test_get_concat_doc(self):
        logging.info("CdocsTests.test_get_concat_doc")
        docpath = "/app/home/teams/todos/assignee/concat.concat"
        cdocs = Cdocs(PATH)
        doc = cdocs.get_concat_doc(docpath)
        na = doc.find("new assignee")
        ea = doc.find("edit assignee")
        self.assertNotEqual(
            -1, na, msg=f'{docpath} must include "new assignee" in {doc}'
        )
        self.assertNotEqual(
            -1, ea, msg=f'{docpath} must include "edit assignee" in {doc}'
        )
        logging.info(f"test_get_concat_doc: concat doc: {doc}")

    def test_get_compose_doc(self):
        logging.info("CdocsTests.test_get_compose_doc")
        docpath = "/app/home/teams/compose.html"
        cdocs = Cdocs(PATH)
        doc = cdocs.get_compose_doc(docpath)
        na = doc.find("new assignee")
        ea = doc.find("edit assignee")
        self.assertNotEqual(
            -1, na, msg=f'{docpath} must include "new assignee" in {doc}'
        )
        self.assertNotEqual(
            -1, ea, msg=f'{docpath} must include "edit assignee" in {doc}'
        )
        logging.info(f"test_get_compose_doc: compose doc: {doc}")

    def test_get_doc_from_root_with_multiple_ext(self):
        logging.info("CdocsTests.test_get_doc_from_root_with_multiple_ext")
        docpath = "/app/home"
        cdocs = Cdocs(PATH2)
        doc = cdocs.get_doc(docpath)
        self.assertIsNotNone(doc, msg=f"{docpath} must not return None")
        home = doc.find("This is home in text!")
        self.assertNotEqual(
            -1, home, msg=f'{docpath} must include "This is home in text!" in {doc}'
        )
        doc = cdocs.get_doc(docpath + "/teams")
        self.assertIsNotNone(doc, msg=f"{docpath} must not return None")
        home = doc.find("<teams>")
        self.assertNotEqual(-1, home, msg=f'{docpath} must include "<teams>" in {doc}')

    def test_concat_json(self):
        logging.info("CdocsTests.test_concat_json")
        docpath = "/app/home+home_screen"
        cdocs = Cdocs(JSON)
        logging.info(f"CdocsTests.test_concat_json: root name: {cdocs.rootname}")
        doc = cdocs.get_doc(docpath)
        self.assertIsNotNone(doc, msg=f"{docpath} must not return None")
        logging.info(f"CdocsTests.test_concat_json: doc: {doc}")
        home = doc.find(
            '{"how-to-use": "How to use My Home", "header": "Home Screen", "content": "The home screen is where you land after logging in."}'
        )
        self.assertNotEqual(
            -1, home, msg=f"{docpath} must include the joined json, not: {doc}"
        )

    def test_list_docs(self):
        logging.info("CdocsTests.test_list_docs")
        docpath = "/app/home/teams"
        cdocs = Cdocs(PATH)
        logging.info(f"CdocsTests.test_list_docs. cdocs: {cdocs}")
        docs = cdocs.list_docs(docpath)
        logging.info(f"CdocsTests.test_list_docs: docs: {docs}")
        self.assertIsNotNone(docs, msg=f"docpath: {docpath} must not be None")
        self.assertEqual(len(docs), 3, msg=f"len(docs) at {docpath} must be 3")
        self.assertIn("a.json", docs, msg=f"docs {docs} must include a.json")

        logging.info("CdocsTests.test_list_docs: listing root")
        docs = cdocs.list_docs("/")
        logging.info(f"CdocsTests.test_list_docs: docs: {docs}")
        self.assertIsNotNone(docs, msg=f"docpath: {docpath} must not be None")
        self.assertEqual(len(docs), 4, msg=f"len(docs) at {docpath} must be 3")
        self.assertIn("404a.xml", docs, msg=f"docs {docs} must include 404a.xml")

        logging.info(
            "CdocsTests.test_list_docs: listing empty string -- which is also the root"
        )
        docs = cdocs.list_docs("")
        logging.info(f"CdocsTests.test_list_docs: docs: {docs}")
        self.assertIsNotNone(docs, msg=f"docpath: {docpath} must not be None")
        self.assertEqual(len(docs), 4, msg=f"len(docs) at {docpath} must be 3")
        self.assertIn("404a.xml", docs, msg=f"docs {docs} must include 404a.xml")

        logging.info("CdocsTests.test_list_docs: listing bogus docpath")
        docs = cdocs.list_docs("fish/can or cannot/fly")
        logging.info(f"CdocsTests.test_list_docs: docs: {docs}")
        self.assertIsNotNone(docs, msg=f"docpath: {docpath} must not be None")
        self.assertEqual(len(docs), 0, msg=f"len(docs) at {docpath} must be 0")

    def test_doc_at_root(self):
        logging.info("CdocsTests.test_doc_at_root")
        #
        # we have:
        #   /404x.html
        #   /404
        #   /404a.xml
        #
        docpath = "/#404x.html"
        cdocs = Cdocs(PATH)
        # self._debug()
        logging.info(f"CdocsTests.test_doc_at_root. cdocs: {cdocs}")
        doc = cdocs.get_doc(docpath)
        logging.info(f"CdocsTests.test_doc_at_root: doc: {doc}")
        self.assertIsNotNone(doc, msg=f"docpath: {docpath} must not be None")
        found = doc.find("REALLY") >= 0
        # should not be found because this root doesn't have html as a format
        # simple pather look using its exts resulting in 404x.html.xml and 404x.html.json
        self.assertEqual(
            found, False, msg=f"doc at {docpath} must not include 'REALLY'"
        )
