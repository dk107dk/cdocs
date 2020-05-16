from cdocs.cdocs import Cdocs, DocNotFoundException, BadDocPath
from cdocs.config import Config
from cdocs.context import ContextMetaData, Context
import unittest
import os

class ContextTests(unittest.TestCase):

    def test_roots(self):
        print("ContextTests.test_roots")
        metadata = ContextMetaData()
        roots = metadata.roots
        self.assertEqual( len(roots), 3, msg="must be 3 roots" )

    def test_create_context(self):
        print("ContextTests.test_context")
        metadata = ContextMetaData()
        context = Context(metadata)
        cdocs = context.cdocs
        self.assertEqual( len(cdocs), 3, msg="must be 3 cdocs" )

    def test_get_doc(self) :
        print(f"ContextTests.test_get_doc")
        metadata = ContextMetaData()
        context = Context(metadata)
        docpath = "/app/home/teams/todos/assignee"
        txt = context.get_doc(docpath)
        self.assertIsNotNone(txt, msg=f"doc at {docpath} must not be none")
        print(f"test_get_doc: doing get_docs. the doc txt is: {txt}")
        point = txt.find("assignee in company starstruck!")
        self.assertNotEqual(-1,point, msg="must include 'assignee in company starstruck!'")
        point = txt.find("my app name: you should see: my app's name is fruit")
        self.assertNotEqual(-1,point, msg="must include 'my app name: you should see: my app's name is fruit'")

    def test_get_labels(self):
        print(f"ContextTests.test_get_labels")
        docpath = "/app/home/teams/todos/assignee"
        metadata = ContextMetaData()
        context = Context(metadata)
        labels = context.get_labels(docpath)
        print(f"test_get_labels: the labels are: {labels}")
        self.assertIn("app", labels, msg=f"labels at {docpath} must include key 'app'")
        self.assertIn("team", labels, msg=f"labels at {docpath} must include key 'team'")
        self.assertIn("my_app_name", labels, msg=f"labels at {docpath} must include key 'my_app_name'")
        self.assertEqual("my app's name is fruit", labels["my_app_name"], msg=f"label my app name must == my app's name is fruit")
        self.assertEqual("starstruck", labels["company"], msg=f"label company must == starstruck")

    def test_get_doc_from_wrong_root(self) :
        print(f"ContextTests.test_get_doc_from_wrong_root")
        metadata = ContextMetaData()
        context = Context(metadata)
        docpath = "/app/home/teams/todos/assignee"
        txt = context.get_doc_from_roots(["images"], docpath)
        self.assertIsNone(txt, msg=f"doc at {docpath} in root 'images' must be none")

    def test_get_doc_from_right_root(self) :
        print(f"ContextTests.test_get_doc_from_right_root")
        metadata = ContextMetaData()
        context = Context(metadata)
        docpath = "/app/home/teams/todos/assignee"
        txt = context.get_doc_from_roots(["public"], docpath)
        self.assertIsNotNone(txt, msg=f"doc at {docpath} in root 'public' must be none")

