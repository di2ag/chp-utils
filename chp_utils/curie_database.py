""" A helper class to handle CHP supported curies.
"""
import json

from trapi_model.biolink.constants import *


class CurieDatabase:
    def __init__(self, curies=None, curies_filename=None):
        if curies is None and curies_filename is None:
            raise ValueError('Must pass in either conflation map or filename.')
        elif curies is not None and curies_filename is not None:
            raise ValueError('Must pass in either conflation map or filename, not both.')
        self.curies = self.load_curies(curies, curies_filename)

    @staticmethod
    def load_curies(curies, curies_filename):
        _curies = {}
        if curies_filename is not None:
            with open(curies_filename) as f_:
                curies = json.load(f_)
        for biolink_entity, curies_list in curies.items():
            _curies[get_biolink_entity(biolink_entity)] = curies_list
        return _curies
