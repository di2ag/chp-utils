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

    def to_dict(self):
        curies_dict = {}
        for biolink_entity, curies_list in self.curies.items():
            curies_dict[biolink_entity.get_curie()] = curies_list
        return curies_dict


    def json(self, filename=None):
        if filename is None:
            return json.dumps(self.to_dict(), indent=2)
        with open(filename, 'w') as f_:
            json.dump(self.to_dict(), f_, indent=2)

