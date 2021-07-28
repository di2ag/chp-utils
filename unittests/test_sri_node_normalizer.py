import unittest
import logging
import json
import sys

import trapi_model
trapi_model.set_biolink_debug_mode(False)
from trapi_model.query import Query
from trapi_model.biolink.constants import *

from chp_utils import SriNodeNormalizerApiClient

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)

logger_root = logging.getLogger()
logger_root.setLevel(logging.INFO)

class TestSriNodeNormalizerApiClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestSriNodeNormalizerApiClient, cls).setUpClass()
        #TODO: Load in sample query graphs

    def test_get_semantic_types(self):
        # Load in test
        with open('json_responses/test_get_semantic_types.json', 'r') as f_:
            saved_resp = json.load(f_)
        client = SriNodeNormalizerApiClient()
        resp = client.get_semantic_types()
        self.assertListEqual(resp, saved_resp)

    def test_get_curie_prefixes(self):
        # Load in test
        with open('json_responses/test_get_curie_prefixes.json', 'r') as f_:
            saved_resp = json.load(f_)
        client = SriNodeNormalizerApiClient()
        resp = client.get_curie_prefixes(
                [
                    BIOLINK_CHEMICAL_SUBSTANCE_ENTITY.get_curie(),
                    BIOLINK_DISEASE_ENTITY.get_curie(),
                    ]
                )
        self.assertDictEqual(resp, saved_resp)

    def test_get_normalized_nodes(self):
        # Load in test
        with open('json_responses/test_get_normalized_nodes.json', 'r') as f_:
            saved_resp = json.load(f_)
        client = SriNodeNormalizerApiClient()
        resp = client.get_normalized_nodes(
                [
                    "HP:0007354", 
                    "HGNC:613",
                    ]
                )
        self.assertDictEqual(resp, saved_resp)

