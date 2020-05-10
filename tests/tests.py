from cdocs.cdocs import Cdocs, DocNotFoundException, BadDocPath
from cdocs.config import Config
import unittest
import os

class FirstTests(unittest.TestCase):

    def test_get_with_default(self):
        cfg = Config()
        oh = cfg.get_with_default("fish", "bats", "yeah!")
        print(f"test_get_with_default: {oh}")
        self.assertEqual( oh, "yeah!", msg="must equal the default value" )

    def test_get_doc_root_path(self):
        cdocs = Cdocs()
        path = cdocs.get_doc_root()
        print(f"test_get_doc_root_path: docs root is {path}")
        self.assertTrue( os.path.exists(path), msg="docs root must exsit" )

    def test_bad_path_arg(self):
        cdocs = Cdocs()
        print("test_bad_path_arg: checking for exceptions")
        with self.assertRaises(DocNotFoundException):
            cdocs.get_doc(None)
        with self.assertRaises(BadDocPath):
            cdocs.get_doc("test.xml")

    def test_get_doc(self) :
        docpath = "/app/home/teams/todos/assignee"
        cdocs = Cdocs()
        txt = cdocs.get_doc(docpath)
        self.assertIsNotNone(txt, msg=f"doc at {docpath} must not be none")
        print(f"test_get_doc: doing get_docs. the doc txt is: {txt}")
        point = txt.find("assignee in company starstruck!")
        self.assertNotEqual(-1,point, msg="must include 'assignee in company starstruck!'")
        point = txt.find("my app name: you should see: my app's name is fruit")
        self.assertNotEqual(-1,point, msg="must include 'my app name: you should see: my app's name is fruit'")

    def test_add_labels_to_tokens(self):
        docpath = "/app/home/teams/todos/assignee#new_assignee"
        cdocs = Cdocs()
        tokens = {}
        tokens = cdocs._add_labels_to_tokens(docpath, tokens)
        print(f"test_add_labels_to_tokens: tokens are {tokens}.")
        self.assertIn("label__my_app_name", tokens, msg=f"must include labels_my_app_name")

    def test_get_plus_paths(self):
        docpath = "/app/home/teams/todos/assignee+edit_assignee"
        cdocs = Cdocs()
        paths = cdocs._get_plus_paths(docpath)
        print(f"test_get_plus_paths: plus paths: {paths}")
        self.assertIn("/app/home/teams/todos/assignee#edit_assignee", paths, msg=f"1. plus paths must include edit_assignee")

        docpath = "/app/home/teams/todos/assignee#new_assignee+edit_assignee"
        paths = cdocs._get_plus_paths(docpath)
        print(f"plus paths: {paths}")
        self.assertIn("/app/home/teams/todos/assignee#edit_assignee", paths, msg=f"2. plus paths must include edit_assignee")

        docpath = "/app/home/teams/todos/assignee+new_assignee+edit_assignee"
        paths = cdocs._get_plus_paths(docpath)
        print(f"plus paths: {paths}")
        self.assertIn("/app/home/teams/todos/assignee#edit_assignee", paths, msg=f"3. plus paths must include edit_assignee")
        self.assertIn("/app/home/teams/todos/assignee#new_assignee", paths, msg=f"4. plus paths must include new_assignee")

    def test_get_doc_with_plus_path(self):
        docpath = "/app/home/teams/todos/assignee+new_assignee+edit_assignee"
        cdocs = Cdocs()
        doc = cdocs.get_doc(docpath)
        print(f"test_get_doc_with_plus_path: content of {docpath} is: {doc}")
        na = doc.find("new assignee")
        ea = doc.find("edit assignee")
        a = doc.find("assignee in company")
        self.assertNotEqual(-1, na, msg=f'must include "new assignee" in {doc}')
        self.assertNotEqual(-1, ea, msg=f'must include "edit assignee" in {doc}')
        self.assertNotEqual(-1, a, msg=f'must include "assignee in company" in {doc}')

    def test_get_tokens(self):
        docpath = "/app/home/teams/todos/assignee"
        cdocs = Cdocs()
        tokens = cdocs.get_tokens(docpath)
        print(f"test_get_tokens: tokens: {tokens}")
        self.assertIn("company", tokens, msg=f"tokens at {docpath} must include key 'company'")
        self.assertIn("app", tokens, msg=f"tokens at {docpath} must include key 'app'")
        company = tokens["company"]
        self.assertEqual(company, "starstruck")

    def test_get_labels(self):
        docpath = "/app/home/teams/todos/assignee"
        cdocs = Cdocs()
        labels = cdocs.get_labels(docpath)
        print(f"test_get_labels: the labels are: {labels}")
        self.assertIn("app", labels, msg=f"labels at {docpath} must include key 'app'")
        self.assertIn("team", labels, msg=f"labels at {docpath} must include key 'team'")
        self.assertIn("my_app_name", labels, msg=f"labels at {docpath} must include key 'my_app_name'")
        self.assertEqual("my app's name is fruit", labels["my_app_name"], msg=f"label my app name must == my app's name is fruit")
        self.assertEqual("starstruck", labels["company"], msg=f"label company must == starstruck")

    def test_get_filename(self):
        docpath = "/app/home/teams/todos/assignee#new_assignee"
        cdocs = Cdocs()
        filename = cdocs._get_filename(docpath)
        print(f"test_get_filename: filename: {filename}")
        self.assertEqual(filename, "new_assignee", msg=f"filename must be 'new_assignee'")

    def test_get_filename_special_hashmark(self):
        docpath = "/app/home/teams/todos/assignee.new_assignee"
        cdocs = Cdocs()
        cdocs._hashmark = '.'
        filename = cdocs._get_filename(docpath)
        print(f"test_get_filename_special_hashmark: filename: {filename}")
        self.assertEqual(filename, "new_assignee", msg=f"filename must be 'new_assignee'")

    def test_get_full_doc_path(self):
        docpath = "/app/home/teams/todos/assignee#new_assignee"
        cdocs = Cdocs()
        path = cdocs._get_full_doc_path(docpath)
        found = path.find("/assignee/new_assignee.xml")
        print(f"test_get_full_doc_path: found: {found}")
        self.assertNotEqual( -1, found, msg=f"path {path} must end in '/assignee/new_assignee.xml'")

    def test_get_concat_paths(self):
        docpath = "/app/home/teams/todos/assignee/concat.txt"
        cdocs = Cdocs()
        paths = cdocs._get_concat_paths(docpath)
        self.assertNotEqual(None, paths, msg=f'cannot get concat paths from {docpath}')
        print(f'test_get_concat_paths: paths: {paths}')
        self.assertIn( "/app/home/teams/todos/assignee#new_assignee", paths, msg=f"paths: {paths} must include in '/app/home/teams/todos/assignee#new_assignee'")

    def test_get_concat_doc(self):
        docpath = "/app/home/teams/todos/assignee/concat.txt"
        cdocs = Cdocs()
        doc = cdocs.get_concat_doc(docpath)
        na = doc.find("new assignee")
        ea = doc.find("edit assignee")
        self.assertNotEqual(-1, na, msg=f'{docpath} must include "new assignee" in {doc}')
        self.assertNotEqual(-1, ea, msg=f'{docpath} must include "edit assignee" in {doc}')
        print(f'test_get_concat_doc: concat doc: {doc}')

    def test_get_compose_doc(self):
        docpath = "/app/home/teams/compose.html"
        cdocs = Cdocs()
        doc = cdocs.get_compose_doc(docpath)
        na = doc.find("new assignee")
        ea = doc.find("edit assignee")
        self.assertNotEqual(-1, na, msg=f'{docpath} must include "new assignee" in {doc}')
        self.assertNotEqual(-1, ea, msg=f'{docpath} must include "edit assignee" in {doc}')
        print(f'test_get_compose_doc: compose doc: {doc}')










