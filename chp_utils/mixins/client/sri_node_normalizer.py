from collections import defaultdict

from trapi_model.biolink.constants import *

from chp_utils.exceptions import GeneralApiErrorException, SriNodeNormalizerException

class SriNodeNormalizerMixin:
    def _get_normalized_nodes(self, curies, **kwargs):
        """ Returns normalizations for all curies passed.

        :param curies: A list of curies to be normalized.
        :type curies: list

        :returns: Normalized nodes.
        :rtype: dict
        """
        _url = self.url + 'get_normalized_nodes'
        #Build json params
        params = {"curie": curies}

        verbose = kwargs.pop('verbose', True)
        try: 
            from_cache, out = self._get(_url, params=params, verbose=verbose)
        except GeneralApiErrorException as ex:
            raise SriNodeNormalizerException(ex.resp, _url, ontology_query)

        if verbose and from_cache:
            print('Result from cache.')
        return self._parse_normalized_nodes_response(out.json())
    
    def _get_curie_prefixes(self, semantic_types, **kwargs):
        """ Returns the prefixes supported for a given list of Biolink semantic_types.

        :param semantic_types: A list of Biolink semantic_types.
        :type semantic_types: list

        :returns: Associated Biolink curie prefixes.
        :rtype: dict
        """
        _url = self.url + 'get_curie_prefixes/'
        #TODO: Build json params
        params = {"semantic_type": semantic_types}

        verbose = kwargs.pop('verbose', True)
        try:
            from_cache, out = self._get(_url, params=params, verbose=verbose)
        except GeneralApiErrorException as ex:
            raise SriNodeNormalizerException(ex.resp, _url, ontology_query)

        if verbose and from_cache:
            print('Result from cache.')
        return self._parse_curie_prefixes_response(out.json())
    
    def _get_semantic_types(self, **kwargs):
        """ Gets the Biolink semantic types that can be normalized.

        :returns: Biolink semantic types that are supported by the node normalizer.
        :rtype: dict
        """
        _url = self.url + 'get_semantic_types'
        #TODO: Build json params
        params = None

        verbose = kwargs.pop('verbose', True)
        try:
            from_cache, out = self._get(_url, params=params, verbose=verbose)
        except GeneralApiErrorException as ex:
            raise SriNodeNormalizerException(ex.resp, _url, ontology_query)
        if verbose and from_cache:
            print('Result from cache.')
        return self._parse_semantic_types_response(out.json())

    def _parse_normalized_nodes_response(self, resp):
        parse = defaultdict(dict)
        for curie, normalization_dict in resp.items():
            parsed_normalization_dict = defaultdict(list)
            for equal_identifier in normalization_dict["equivalent_identifiers"]:
                parsed_normalization_dict["equivalent_identifier"].append(equal_identifier)
            parsed_normalization_dict["types"] = [get_biolink_entity(biolink_curie) for biolink_curie in normalization_dict["type"]]
            parse[curie] = dict(parsed_normalization_dict)
        return dict(parse)

    def _parse_curie_prefixes_response(self, resp):
        parse = defaultdict(list)
        for curie, prefix_dict in resp.items():
            for prefix in prefix_dict["curie_prefix"]:
                parse[curie].append(prefix)
        return dict(parse)

    def _parse_semantic_types_response(self, resp):
        return resp["semantic_types"]["types"]
