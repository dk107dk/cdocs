from cdocs.cdocs import Cdocs, DocNotFoundException, BadDocPath
import unittest
import os
import logging

PATH: str = "docs/example"
PATH2: str = "docs/internal"


class CdocsSchemeTests(unittest.TestCase):
    def test_finding_doc_at_root_using_cdoc(self):
        logging.info("CdocsSchemeTests.test_finding_doc_at_root_using_cdoc")
        logging.info(
            "CdocsSchemeTests.test_finding_doc_at_root_using_cdoc: THIS TEST IS NOT YET DETERMINISTIC."
        )
        #
        # we have:
        #   /404x.html
        #   /404
        #   /404a.xml
        #
        # which is the concept?
        # concepts are:
        #    directory names
        #    any file without an extension
        #    any file with an extension in the exts array
        # everything else must be addressed as directory#filename
        # so:
        #    /404 is a concept you get with /404
        #    /404a.xml is a concept (xml is in the exts array) you get with /404a
        #    /404x.html is a file you get using /#404x.html
        #
        #
        logging.info(
            "CdocsSchemeTests.test_finding_doc_at_root_using_cdoc: NOT A DETERMINISTIC TEST!"
        )
        cdocs = Cdocs(PATH)
        logging.info(
            f"CdocsSchemeTests.test_finding_doc_at_root_using_cdoc. cdocs: {cdocs}"
        )
        logging.info("")
        docpath1 = (
            "/404x.html"  # should be not found because not in root with accepts html
        )
        docpath2 = "/#404x.html"  # same
        docpath3 = "/404x"  # not found. this is correct, 404x is html
        docpath4 = "/#404x"  # not found. this is correct, 404x is html
        docpath5 = "/404a"  # found because 404a.xml exists
        docpath6 = "/#404a"  # found because 404a.xml exists. concepts can also be addressed as supporting files.
        docpath7 = "/404a.xml"  # not found because its a full file path not cdocs path
        docpath8 = "/#404a.xml"  # found because can find a full filename on hashmark with cdocs in accepts. the accepts needs to have 'cdocs' because the hashmark is cdocs.
        docpath9 = "/404"  # not found. this is right. cdocs docpath may not have an extension, but files must have extensions.
        docpath10 = (
            "/#404"  # not found. this is right, there is no 404.xml or 404.json.
        )

        doc = cdocs.get_doc(docpath1)
        logging.info(
            f"CdocsSchemeTests.test_finding_doc_at_root_using_cdoc: docpath: {docpath1}: doc: {doc}"
        )

        doc = cdocs.get_doc(docpath2)
        logging.info(
            f"CdocsSchemeTests.test_finding_doc_at_root_using_cdoc: docpath: {docpath2}: doc: {doc}"
        )

        doc = cdocs.get_doc(docpath3)
        logging.info(
            f"CdocsSchemeTests.test_finding_doc_at_root_using_cdoc: docpath: {docpath3}: doc: {doc}"
        )

        doc = cdocs.get_doc(docpath4)
        logging.info(
            f"CdocsSchemeTests.test_finding_doc_at_root_using_cdoc: docpath: {docpath4}: doc: {doc}"
        )

        doc = cdocs.get_doc(docpath5)
        logging.info(
            f"CdocsSchemeTests.test_finding_doc_at_root_using_cdoc: docpath: {docpath5}: doc: {doc}"
        )

        doc = cdocs.get_doc(docpath6)
        logging.info(
            f"CdocsSchemeTests.test_finding_doc_at_root_using_cdoc: docpath: {docpath6}: doc: {doc}"
        )

        doc = cdocs.get_doc(docpath7)
        logging.info(
            f"CdocsSchemeTests.test_finding_doc_at_root_using_cdoc: docpath: {docpath7}: doc: {doc}"
        )

        doc = cdocs.get_doc(docpath8)
        logging.info(
            f"CdocsSchemeTests.test_finding_doc_at_root_using_cdoc: docpath: {docpath8}: doc: {doc}"
        )

        doc = cdocs.get_doc(docpath9)
        logging.info(
            f"CdocsSchemeTests.test_finding_doc_at_root_using_cdoc: docpath: {docpath9}: doc: {doc}"
        )

        doc = cdocs.get_doc(docpath10)
        logging.info(
            f"CdocsSchemeTests.test_finding_doc_at_root_using_cdoc: docpath: {docpath10}: doc: {doc}"
        )

        # self.assertIsNotNone(doc, msg=f"docpath: {docpath} must not be None")
        # found = doc.find("REALLY") >= 0
        # self.assertEqual(found, True, msg=f"doc at {docpath} must include 'REALLY'")
