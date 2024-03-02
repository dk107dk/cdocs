from cdocs.cdocs import Cdocs, DocNotFoundException, BadDocPath
from cdocs.context import Context
from cdocs.context_metadata import ContextMetadata
import unittest
import os
import logging


class ContextTests(unittest.TestCase):
    def test_split_plus_concat(self):
        # tests the use of:
        #    split-plus searches
        #    non-split-plus searches
        #    split-plus searches with roots that deny split-plus
        #    implicitly, the order of multi-root searches
        # see config.ini re: order of roots under [doc] in the
        # context of split-plus searches
        docpath = "app/home/teams#delete_assignee+todo"
        metadata = ContextMetadata()
        context = Context(metadata)

        # split plus: true
        #    both roots allow split plus
        doc = context.get_doc(docpath)
        logging.info(f"ContextTests.test_split_plus_concat: doc 1:\n{doc}")
        self.assertIsNotNone(doc, msg=f"doc at {docpath} must not be none")
        found = doc.find("edit assignee") > -1
        found = found and doc.find("my app name: you should see") > -1
        self.assertEqual(found, True, msg=f"doc: {doc} doesn't have expected content")

        # split plus: false
        #    both roots allow split plus
        doc = context.get_doc(docpath, False, False)
        logging.info(f"\nContextTests.test_split_plus_concat: doc 2:\n{doc}")
        found = doc.find("edit assignee") > -1
        found = found and doc.find("my app name: you should see") > -1
        self.assertEqual(found, False, msg=f"doc: {doc} doesn't have expected content")

        context._nosplitplus = ["internal", "public"]

        # split plus: true
        #    both roots deny split plus
        doc = context.get_doc(docpath)
        logging.info(f"\nContextTests.test_split_plus_concat: doc 3:\n{doc}")
        self.assertIsNotNone(doc, msg=f"doc at {docpath} must not be none")
        found = doc.find("edit assignee") == -1
        found = found and doc.find("my app name: you should see") == -1
        self.assertEqual(found, True, msg=f"doc: {doc} doesn't have expected content")
        # split plus: false
        #    both roots deny split plus
        doc = context.get_doc(docpath, False, False)
        logging.info(f"\nContextTests.test_split_plus_concat: doc 4:\n{doc}")
        found = doc.find("edit assignee") == -1
        found = found and doc.find("my app name: you should see") == -1
        self.assertEqual(found, False, msg=f"doc: {doc} doesn't have expected content")

        context._nosplitplus = ["public"]

        # split plus: true
        #    public denies split plus
        doc = context.get_doc(docpath)
        logging.info(f"\nContextTests.test_split_plus_concat: doc 5:\n{doc}")
        self.assertIsNotNone(doc, msg=f"doc at {docpath} must not be none")
        found = doc.find("edit assignee") > -1
        found = found and doc.find("my app name: you should see") == -1
        self.assertEqual(found, True, msg=f"doc: {doc} doesn't have expected content")
        # split plus: false
        #    public denies split plus
        doc = context.get_doc(docpath, False, False)
        logging.info(f"\nContextTests.test_split_plus_concat: doc 6:\n{doc}")
        found = doc.find("edit assignee") == -1
        found = found and doc.find("my app name: you should see") > -1
        self.assertEqual(found, True, msg=f"doc: {doc} doesn't have expected content")

        context._nosplitplus = ["internal"]

        # split plus: true
        #    internal denies split plus
        doc = context.get_doc(docpath)
        logging.info(f"\nContextTests.test_split_plus_concat: doc 7:\n{doc}")
        self.assertIsNotNone(doc, msg=f"doc at {docpath} must not be none")
        found = doc.find("edit assignee") == -1
        found = found and doc.find("my app name: you should see") > -1
        self.assertEqual(found, True, msg=f"doc: {doc} doesn't have expected content")

        # split plus: false
        #    internal denies split plus
        doc = context.get_doc(docpath, False, False)
        logging.info(f"\nContextTests.test_split_plus_concat: doc 8:\n{doc}")
        found = doc.find("edit assignee") == -1
        found = found and doc.find("my app name: you should see") > -1
        self.assertEqual(found, True, msg=f"doc: {doc} doesn't have expected content")

    def test_roots(self):
        logging.info("ContextTests.test_roots")
        metadata = ContextMetadata()
        roots = metadata.roots
        self.assertEqual(len(roots), 5, msg="must be 4 roots")

    def test_accepts(self):
        logging.info("ContextTests.test_accepts")
        metadata = ContextMetadata()
        accepts = metadata.accepts
        logging.info(f"accepts: {accepts}")
        self.assertIsNotNone(accepts, msg="accepts must not be None")
        self.assertEqual(
            len(accepts), 5, msg=f"must be 4 keys in accepts, not {accepts}"
        )
        self.assertIsNotNone(accepts["images"], msg="accepts must have an 'images' key")
        images = accepts["images"]
        self.assertEqual(len(images), 4, msg="must be 4 items in images")
        self.assertIn("gif", images, msg="images must include item 'gif'")
        self.assertIn("png", images, msg="images must include item 'png'")
        self.assertIn("jpg", images, msg="images must include item 'jpg'")
        self.assertIn("jpeg", images, msg="images must include item 'jpeg'")

    def test_accepted_by(self):
        logging.info("ContextTests.test_accepted_by")
        metadata = ContextMetadata()
        accceptedby = metadata.accepted_by
        logging.info(f"accceptedby: {accceptedby}")
        self.assertIsNotNone(accceptedby, msg="accceptedby must not be None")
        self.assertEqual(
            len(accceptedby), 7, msg=f"must be 7 keys in accceptedby, not {accceptedby}"
        )
        self.assertIsNotNone(
            accceptedby["cdocs"], msg="accepts must have a 'cdocs' key"
        )
        cdocs = accceptedby["cdocs"]
        self.assertEqual(len(cdocs), 2, msg="must be 2 items in cdocs")
        self.assertIn("public", cdocs, msg="cdocs must include item 'public'")
        self.assertIn("internal", cdocs, msg="cdocs must include item 'internal'")
        gif = accceptedby["gif"]
        self.assertIn("images", gif, msg="gif must include item 'images'")

    def test_get_filetype(self):
        logging.info("ContextTests.test_get_filetype")
        metadata = ContextMetadata()
        context = Context(metadata)
        atype = context.get_filetype("/x/y/z.gif")
        logging.info(f"type for /x/y/z.gif: {atype}")
        self.assertEqual(atype, "gif", msg="type must be gif")
        atype = context.get_filetype("/x/y/z")
        logging.info(f"type for /x/y/z: {atype}")
        self.assertEqual(atype, "cdocs", msg="type must be cdocs")

    def test_filter_root_names_for_path(self):
        logging.info("ContextTests.test_filter_root_names_for_path")
        metadata = ContextMetadata()
        context = Context(metadata)
        roots = ["images", "fish", "public"]
        rs = context.filter_root_names_for_path(roots, "/x/y/z")
        logging.info(f"filtered roots: {rs}")
        self.assertIsNotNone(rs, msg="filtered roots must not be None")
        self.assertEqual(len(rs), 1, msg="must be 1 filtered root")
        self.assertEqual(rs, ["public"], msg="filtered roots must be ['public']")

    def test_get_root_names_accepting_path(self):
        logging.info("ContextTests.test_get_root_names_accepting_path")
        metadata = ContextMetadata()
        context = Context(metadata)
        gifs = context.get_root_names_accepting_path("/x/y/z.gif")
        logging.info(f"roots for /x/y/z.gif: {gifs}")
        self.assertIsNotNone(gifs, msg="gifs must not be None")
        self.assertEqual(len(gifs), 1, msg="must be 1 items in gifs")
        cdocs = context.get_root_names_accepting_path("/x/y/z")
        logging.info(f"roots for /x/y/z: {cdocs}")
        self.assertIsNotNone(cdocs, msg="cdocs must not be None")
        self.assertEqual(len(cdocs), 2, msg="must be 2 items in cdocs")

    def test_create_context(self):
        logging.info("ContextTests.test_context")
        metadata = ContextMetadata()
        context = Context(metadata)
        cdocs = context.cdocs
        self.assertEqual(
            len(cdocs), 5, msg=f"must be 4 cdocs, not {len(cdocs)} from {cdocs}"
        )

    def test_get_known_type_doc(self):
        logging.info("ContextTests.test_get_known_type_doc")
        metadata = ContextMetadata()
        context = Context(metadata)
        docpath = "/app/home/teams/3-copy.png"
        f = context.get_doc(docpath)
        logging.info(f"the image doc {type(f)} ")
        self.assertIsNotNone(f, msg=f"doc at {docpath} must not be none")
        self.assertEqual(type(f).__name__, "bytes", msg="type must be 'bytes'")

    def test_get_doc(self):
        logging.info("ContextTests.test_get_doc")
        metadata = ContextMetadata()
        context = Context(metadata)
        docpath = "/app/home/teams/todos/assignee"
        txt = context.get_doc(docpath)
        self.assertIsNotNone(txt, msg=f"doc at {docpath} must not be none")
        logging.info(f"test_get_doc: doing get_docs. the doc txt is: {txt}")
        point = txt.find("assignee in company starstruck!")
        self.assertNotEqual(
            -1, point, msg="must include 'assignee in company starstruck!'"
        )
        point = txt.find("my app name: you should see: my app's name is fruit")
        self.assertNotEqual(
            -1,
            point,
            msg="must include 'my app name: you should see: my app's name is fruit'",
        )

    def test_get_doc_just_checking(self):
        logging.info("ContextTests.test_get_doc_just_checking")
        metadata = ContextMetadata()
        context = Context(metadata)
        docpath = "/app/home/teams*delete_assignee"
        txt = context.get_doc(docpath)
        # this doc could be a not-found doc. for what I need today that's fine.
        self.assertIsNotNone(txt, msg=f"doc at {docpath} must not be none")
        logging.info(
            f"ContextTests.test_get_doc_just_checking: doing get_docs. the doc txt is: {txt}"
        )

    def test_get_labels(self):
        logging.info("ContextTests.test_get_labels")
        docpath = "/app/home/teams/todos/assignee"
        # docpath = "/v1/test/fish"
        metadata = ContextMetadata()
        context = Context(metadata)
        labels = context.get_labels(docpath)
        print(f"test_get_labels: the labels are: {labels}")
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

    def test_get_doc_from_wrong_root(self):
        logging.info("ContextTests.test_get_doc_from_wrong_root")
        metadata = ContextMetadata()
        context = Context(metadata)
        docpath = "/app/home/teams/todos/assignee"
        txt = context.get_doc_from_roots(["images"], docpath, False)
        self.assertIsNone(txt, msg=f"doc at {docpath} in root 'images' must be none")

    def test_get_doc_from_right_root(self):
        logging.info("ContextTests.test_get_doc_from_right_root")
        metadata = ContextMetadata()
        context = Context(metadata)
        docpath = "/app/home/teams/todos/assignee"
        txt = context.get_doc_from_roots(["public"], docpath)
        self.assertIsNotNone(
            txt, msg=f"doc at {docpath} in root 'public' must not be none"
        )

    def test_get_compose_doc_with_roots(self):
        logging.info("ContextTests.test_get_compose_doc_with_roots")
        docpath = "/app/home/teams"
        metadata = ContextMetadata()
        context = Context(metadata)
        doc = context.get_doc_from_roots(["internal"], docpath, False)
        logging.info(f"test_get_compose_doc_with_roots: doc from 'internal': {doc}")
        assignee = doc.find("assignee in company starstruck!")
        self.assertNotEqual(
            -1,
            assignee,
            msg=f'{docpath} must include "assignee in company starstruck!" in {doc}',
        )
        edit = doc.find("edit assignee")
        self.assertNotEqual(
            -1, edit, msg=f'{docpath} must include "edit assignee" in {doc}'
        )
        doc = context.get_doc_from_roots(["public"], docpath)
        logging.info(f"test_get_compose_doc_with_roots: doc from 'public': {doc}")
        notfound = doc.find("Not found!")
        self.assertNotEqual(
            notfound, -1, msg=f'doc at {docpath} must include "Not found!"'
        )
