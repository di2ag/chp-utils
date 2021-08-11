""" Class for handling conflation in TRAPI and Biolink.
"""

import json

from trapi_model.biolink.constants import *

class ConflationMap:
    def __init__(self, conflation_map=None, conflation_map_filename=None):
        if conflation_map is None and conflation_map_filename is None:
            raise ValueError('Must pass in either conflation map or filename.')
        elif conflation_map is not None and conflation_map_filename is not None:
            raise ValueError('Must pass in either conflation map or filename, not both.')
        self.map = self.load_conflation_map(conflation_map, conflation_map_filename)

    @staticmethod
    def load_conflation_map(conflation_map, conflation_map_filename):
        _map = {}
        if conflation_map_filename is not None:
            with open(conflation_map_filename) as f_:
                conflation_map = json.load(f_)
        for biolink_entity, conflated_entity in conflation_map.items():
            _map[get_biolink_entity(biolink_entity)] = get_biolink_entity(conflated_entity)
        return _map

    def find_conflation(self, biolink_entity):
        if biolink_entity in self.map:
            return self.map[biolink_entity]
        return None

    def conflate(self, trapi_query):
        for entity, conflated_entity in self.map.items():
            conflated_message = trapi_query.message.find_and_replace(entity.get_curie(), conflated_entity.get_curie())
            if conflated_message.to_dict() != trapi_query.message.to_dict():
                trapi_query.message = conflated_message
                trapi_query.warning(
                        'Conflated {} with {}'.format(
                            entity.get_curie(),
                            conflated_entity.get_curie(),
                            )
                        )
        return trapi_query
