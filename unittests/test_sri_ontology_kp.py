import unittest
import logging
import json
import sys

from trapi_model.biolink.constants import *

from chp_utils import SriOntologyKpApiClient

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

    def test_get_ontology_descendents(self):
        # Load in test
        with open('json_responses/test_get_ontology_descendents.json', 'r') as f_:
            saved_resp = json.load(f_)
        client = SriOntologyKpApiClient()
        resp = client.get_ontology_descendents(
                ['MONDO:0005015', 'MONDO:0005148'],
                BIOLINK_DISEASE_ENTITY,
                )
        for curie in resp:
            self.assertSetEqual(set(resp[curie]), set(saved_resp[curie]))
