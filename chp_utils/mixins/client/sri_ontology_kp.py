from collections import defaultdict

from trapi_model.biolink.constants import *

from chp_utils.exceptions import *

class SriOntologyKpMixin:

    def _query(self, ontology_query, **kwargs):
        """ Returns all ontological descendants that are present in a given ONTOLOGY query. The KP
        will iteratively go through the query and list all descendants if the curie and biolink type are 
        supported by the SRI Ontology KP.

        :param ontology_query: The specific ontology query that is created via the _build_ontology_query method.
        :type ontology_query: dict
        """
        _url = self.url + 'query'
        verbose = kwargs.pop('verbose', True)
        try:
            from_cache, out = self._post(_url, params=ontology_query, verbose=verbose)
        except GeneralApiErrorException as ex:
            raise SriOntologyKpException(ex.resp, _url, ontology_query)
        if verbose and from_cache:
            print('Result from cache.')
        return out.json()

    def _build_ontology_query(self, curies, biolink_entity):
        """ Have to load a special form of TRAPI message, so we'll just build it
        without the help of the trapi_model.

        :param curies: A list of containing all the curies you want ontological descendants.
        :type curies: list
        :param biolink_entity: The Biolink Entitiy that pertains to the curies.
        :type biolink_entity: trapi_model.biolink.BiolinkEntity
        
        :returns: A dictionary of the Ontology KP result.
        :rtype: dict
        """
        banned_curies = {'UBERON:0000062', 'UBERON:0002530', 'UBERON:0000058', 'UBERON:0009912', 'UBERON:0000483', 'UBERON:0003129', 'UBERON:0000483', 'UBERON:0002103', 'UBERON:0000970', 'UBERON:0001015'}
        cleaned_curies = []
        for curie in curies:
            if curie not in banned_curies:
                cleaned_curies.append(curie)

        # Build weird Ontology KP Query graph.
        query_graph = {
                "nodes": {
                    "n0": {
                        "ids": cleaned_curies
                        },
                    "n1": {
                        "categories": [biolink_entity.get_curie()]
                        },
                    },
                "edges": {
                    "e0": {
                        "subject": "n1",
                        "object": "n0",
                        "predicates": [BIOLINK_SUBCLASS_OF_ENTITY.get_curie(), BIOLINK_PART_OF_ENTITY.get_curie()],
                        }
                    }
                }
        # Wrap in a message and in a query
        query = {
                "message": {
                    "query_graph": query_graph,
                    }
                }

        return query

    def _get_ontology_descendants(self, curies, biolink_entity, **kwargs):
        """ Wrapper function that builds an ontology KP query from a list of curies and associated
        biolink entity and wraps the Ontology KP query endpoint.

        :param curies: A list of containing all the curies you want ontological descendants.
        :type curies: list
        :param biolink_entity: The Biolink Entitiy that pertains to the curies.
        :type biolink_entity: trapi_model.biolink.BiolinkEntity
        
        :returns: A dictionary of the Ontology KP result.
        :rtype: dict
        """

        ontology_query = self._build_ontology_query(curies, biolink_entity)
        # Pass to query endpoint
        resp = self._query(ontology_query, **kwargs)
        return self._parse_ontology_descendants_response(resp)

    def _parse_ontology_descendants_response(self, resp):
        parse = defaultdict(list)
        for res in resp["message"]["results"]:
            curie = res["node_bindings"]["n0"][0]["id"]
            descendant = res["node_bindings"]["n1"][0]["id"]
            parse[curie].append(descendant)
        return dict(parse)
