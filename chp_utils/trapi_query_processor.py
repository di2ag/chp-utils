import logging
import itertools
from copy import deepcopy
from collections import defaultdict
import json

from trapi_model.query import Query
from trapi_model.biolink import BiolinkEntity
from trapi_model.message import Message
from trapi_model.biolink.constants import *
from trapi_model.logger import Logger

from chp_utils import SriNodeNormalizerApiClient, SriOntologyKpApiClient
from chp_utils.exceptions import *

class BaseQueryProcessor:
    """ Query Processor class used to abstract the processing infrastructure from
        the views:

        :param query: Load trapi query.
        :type query: trapi_model.trapi_model.query.Query
    """
    def __init__(self, query=None):
        if query is not None:
            self.query_copy = query.get_copy()

    def setup_query(self, query):
        self.query_copy = query.get_copy()
    
    def _extract_all_curies(self, queries):
        curies = []
        for query in queries:
            query_graph = query.message.query_graph
            for node_id, node in query_graph.nodes.items():
                if node.ids is not None:
                    curies.extend(node.ids)
        return curies

    def _get_most_general_preference(self, possible_preferences):
        unsorted_entities = []
        for curie, category in possible_preferences:
            unsorted_entities.append((len(category.get_ancestors()), curie, category))
        return sorted(unsorted_entities)[0]

    def _get_most_specific_biolink_entity(self, entities):
        unsorted_entities = []
        for entity in entities:
            unsorted_entities.append((len(entity.get_ancestors()), entity.get_curie()))
        most_specific_entity_str = sorted(unsorted_entities, reverse=True)[0][1]
        return get_biolink_entity(most_specific_entity_str)

    def _get_preferred(self, query, node, normalization_dict, meta_knowledge_graph):
        # Extract curie and category
        curie = node.ids[0]
        if node.categories is not None:
            categories = node.categories[0]
        else:
            categories = None
        # Ensure query graph categories and normalization type (categories) are consistent
        curie_types = normalization_dict[curie]["types"]
        curie_prefix = curie.split(':')[0]
        possible_preferences = []
        for curie_type in curie_types:
            if curie_type in meta_knowledge_graph.nodes:
                # Take first entry in id_prefixes of the meta KG
                preferred_prefix = meta_knowledge_graph.nodes[curie_type].id_prefixes[0]
                if curie_prefix != preferred_prefix:
                    for equivalent_id_obj in normalization_dict[curie]["equivalent_identifier"]:
                        equivalent_id = equivalent_id_obj["identifier"]
                        equiv_prefix = equivalent_id.split(':')[0]
                        if equiv_prefix == preferred_prefix:
                            possible_preferences.append(
                                    (equivalent_id, curie_type)
                                    )
                            break
                else:
                    possible_preferences.append(
                            (curie, curie_type)
                            )
        # Go through each possible preference and return the preferred curie that with the most general category
        if len(possible_preferences) == 0:
            query.warning('Could not normalize curie: {}, because no supported curie types where found in the metakg.'.format(curie))
            raise ValueError
        if len(possible_preferences) > 1:
            preferred_curie, preferred_category = self._get_most_general_preference(possible_preferences)
        else:
            preferred_curie, preferred_category = possible_preferences[0]
        return preferred_curie, preferred_category

    def _normalize_query_graphs(self, queries, normalization_dict, meta_knowledge_graph):
        normalization_map = {}
        non_normalized_queries = []
        for query in queries:
            query_graph = query.message.query_graph
            for node_id, node in query_graph.nodes.items():
                if node.ids is None:
                    continue
                # Get preferred curie and category based on meta kg
                try:
                    preferred_curie, preferred_category = self._get_preferred(
                            query,
                            node,
                            normalization_dict, 
                            meta_knowledge_graph,
                            )
                except:
                    non_normalized_queries.append(query)
                    break
                # Check if curie was actually converted
                if node.ids[0] != preferred_curie:
                    query.info('Normalized curie: {} to {}'.format(node.ids[0], preferred_curie))
                    normalization_map[preferred_curie] = node.ids[0]
                    node.ids = [preferred_curie]
                # Check categories alignment
                if node.categories is None:
                    node.categories = [preferred_category]
                    query.info(
                            'Filling in empty category for node {}, with {}'.format(
                                node_id,
                                preferred_category.get_curie(),
                                )
                            )
                elif node.categories[0] != preferred_category:
                    query.warning(
                        'Passed category for {}: {}, did not match our preferred category {} for this curie. Going with our preferred category.'.format(
                                node_id,
                                node.categories[0].get_curie(),
                                preferred_category.get_curie(),
                                )
                            )
                    node.categories = [preferred_category]
        for nnq in non_normalized_queries:
            queries.remove(nnq)
        return queries, normalization_map

    def normalize_to_preferred(self, queries, meta_knowledge_graph=None, with_normalization_map=False):
        # Instantiate client
        node_normalizer_client = SriNodeNormalizerApiClient()
        
        # Get all curies to normalize
        curies_to_normalize = self._extract_all_curies(queries)
        # Get normalized nodes
        try:
            normalization_dict = node_normalizer_client.get_normalized_nodes(curies_to_normalize)
        except SriNodeNormalizerException as ex:
            # Iterate through each query and add a normalization error message
            for query in queries:
                query.error(f'Node Normalization error. Nodes are NOT normalized. {ex.message}')
            return queries, {}
        # Normalize query graph
        queries, normalization_map = self._normalize_query_graphs(queries, normalization_dict, meta_knowledge_graph)
        if with_normalization_map:
            return queries, normalization_map
        return queries

    def conflate_categories(self, queries, conflation_map=None):
        for query in queries:
            query = conflation_map.conflate(query)
        return queries


    def expand_batch_query(self, query):
        # Expand if batch query
        if query.is_batch_query():
            return query.expand_batch_query()
        # Otherwise wrap query in list
        return [query]
    
    def _extract_all_curies_for_ontology_kp(self, queries):
        curies = defaultdict(list)
        curies_to_query = defaultdict(list)
        for query in queries:
            query_graph = query.message.query_graph
            for node_id, node in query_graph.nodes.items():
                if node.ids is not None:
                    try:
                        curies[node.categories[0]].extend(node.ids)
                        curies_to_query[node.ids].append(query)
                    except TypeError:
                        query.error('Node: {} has no categories. Can not ontologically expand a node with no category.'.format(
                            node.ids[0])
                            )
        return dict(curies), dict(curies_to_query)

    def _expand_query_with_supported_ontological_descendants(self, curies_to_query_dict, descendants_map, curies):
        onto_expanded_queries = []
        for biolink_entity, curie_descendants_dict in descendants_map.items():
            if biolink_entity not in curies.curies:
                query.error('{} is not support in the meta knowledge graph'.format(biolink_entity.get_curie()))
                continue
            for curie, descendants in curie_descendants_dict.items():
                for query in curies_to_query_dict[curie]:
                    for descendant in descendants:
                        new_query = query.get_copy()
                        onto_expanded_message = new_query.message.find_and_replace(curie, descendant)
                        if onto_expanded_message.to_dict() != new_query.message.to_dict():
                            new_query.info('Ontologically expanded {} to {}'.format(curie, descendant))
                            new_query.message = onto_expanded_message
                            onto_expanded_queries.append(new_query)
        return onto_expanded_queries

    def expand_supported_ontological_descendants(self, queries, curies_database=None):
        # Intialize queries logger
        queries_logger = Logger()
        # Initialize client
        ontology_kp_client = SriOntologyKpApiClient()

        # Get all curies to expand via the Ontology KP
        curies_to_onto_expand, curies_to_query_dict = self._extract_all_curies_for_ontology_kp(queries)

        descendants_map = {}
        for biolink_entity, curies in curies_to_onto_expand.items():
            try:
                descendants = ontology_kp_client.get_ontology_descendants(curies, biolink_entity)
            except SriOntologyKpException as ex:
                queries_logger.error(str(ex))
                continue
            if len(descendants) > 0:
                curie_map = dict()
                for curie, curie_descendants in descendants.items():
                    supported_descendants = []
                    for curie_descendant in curie_descendants:
                        try:
                            x = curies_database[biolink_entity][curie_descendant]
                            supported_descendants.append(curie_descendant)
                        except:
                            continue
                   if len(supported_descendants) > 0: 
                       curie_map[curie] = supported_descendants
                descendants_map[biolink_entity] = curie_map
        # Expand each query ontologically with all supported descendants
        onto_expanded_queries = self._expand_query_with_supported_ontological_descendants(curies_to_query_dict,
                                                                                          descendants_map,
                                                                                          curies_database)
        for query in queries:
            onto_expanded_queries.append(query)
        # Merge in queries logger to each individual query log
        for query in onto_expanded_queries:
            query.logger.add_logs(queries_logger.to_dict())
        return onto_expanded_queries

    def _expand_categories_with_semantic_operations(self, query, meta_knowledge_graph):
        query_graph = query.message.query_graph
        queries = []
        node_expansion_map = {}
        for node_id, node in query_graph.nodes.items():
            # Greg added base case - if no category we assume Named Thing
            if node.categories is None:
                node.categories = [BiolinkEntity(BIOLINK_NAMED_THING)]

            # Greg commented out, similar to predicate expansion, just because a node category happens to be in our meta-kg
            # does not mean we do not want its descendants and so we should expand. e.g., lets say we had DiseaseOrPhenotypicFeature
            # in our meta-kg, but we also had a relationship for phenotypes in our meta-kg. We would want to expand for both
            # queries and answer them.
            #if node.categories[0] in meta_knowledge_graph.nodes:
            #    continue

            # Else run semantic operations to get descedants
            descendants = node.categories[0].get_descendants()
            supported_descendants = list(
                    set.intersection(
                        *[
                            set(descendants),
                            set(meta_knowledge_graph.nodes),
                            ]
                        )
                    )
            if node.categories[0] in meta_knowledge_graph.nodes:
                supported_descendants.append(node.categories[0])
            if len(supported_descendants) == 0:
                query.warning('Biolink category {} is not inherently supported and could not find any supported descendants,'.format(node.categories[0].get_curie()))
                continue
            node_expansion_map[node_id] = sorted(supported_descendants)
        # Now expand query using supported descendants
        node_id_map = sorted([node_id for node_id in node_expansion_map])
        supported_descendants_map = [node_expansion_map[node_id] for node_id in node_id_map]
        for category_prod in itertools.product(*supported_descendants_map):
            new_query = query.get_copy()
            for node_id, category in zip(node_id_map, category_prod):
                new_query.message.query_graph.nodes[node_id].categories = [category]
                new_query.info('Converted category {} to {} using Biolink semantic operations.'.format(query_graph.nodes[node_id].categories[0].get_curie(), category.get_curie()))
            queries.append(new_query)
        # Check if any category expansions occurred
        if len(queries) == 0:
            return [query]
        return queries

    def _expand_predicates_with_semantic_operations(self, query, supported_edge_predicates):
        query_graph = query.message.query_graph
        queries = []
        edge_expansion_map = {}
        for edge_id, edge in query_graph.edges.items():
            # If predicate is null that substitute with biolink related to.
            if edge.predicates is None:
                edge.predicates = [BIOLINK_RELATED_TO_ENTITY]

            # Greg removed this. A hit for a predicate in our supported edges does not mean it should be skipped. This
            # leads to strange semantic operation expansions. For instance on a gene->gene edge using 'interacts_with'
            # we would expect it to expand to 'genetically_interacts_with', however because 'interacts_with' is a predicate
            # in our meta-kg for gene->drug relationships, we will stop here otherwise and NOT expand on 'interacts_with'.
            # this also means we have to add this term manually to the descendants

            #elif edge.predicates[0] in supported_edge_predicates:
            #    continue


            # Else run semantic operations to get descedants
            descendants = edge.predicates[0].get_descendants()
            supported_descendants = list(
                    set.intersection(
                        *[
                            set(descendants),
                            set(supported_edge_predicates),
                            ]
                        )
                    )
            if edge.predicates[0] in supported_edge_predicates:
                supported_descendants.append(edge.predicates[0])

            if len(supported_descendants) == 0:
                query.warning('Biolink predicate {} is not inherently supported and could not find any supported descendants,'.format(edge.predicates[0].get_curie()))
                continue
            edge_expansion_map[edge_id] = sorted(supported_descendants)
        # Now expand query using supported descendants
        edge_id_map = sorted([edge_id for edge_id in edge_expansion_map])
        supported_descendants_map = [edge_expansion_map[edge_id] for edge_id in edge_id_map]
        for predicate_prod in itertools.product(*supported_descendants_map):
            new_query = query.get_copy()
            for edge_id, predicate in zip(edge_id_map, predicate_prod):
                new_query.message.query_graph.edges[edge_id].predicates = [predicate]
                new_query.info('Converted predicate {} to {} using Biolink semantic operations.'.format(query_graph.edges[edge_id].predicates[0].get_curie(), predicate.get_curie()))
            queries.append(new_query)
        # Check if any predicate expansions occurred
        if len(queries) == 0:
            return [query]
        return queries
 
    def expand_with_semantic_ops(self, queries, meta_knowledge_graph=None):
        supported_edge_predicates = [meta_edge.predicate for meta_edge in meta_knowledge_graph.edges]
        expanded_categories = []
        # Expand categories
        for query in queries:
            expanded_categories.extend(
                    self._expand_categories_with_semantic_operations(query, meta_knowledge_graph)
                    )
        # Expand predicates on already expanded category queries.
        expanded_predicates = []
        for query in expanded_categories:
            # Expand predicates
            expanded_predicates.extend(
                    self._expand_predicates_with_semantic_operations(query, supported_edge_predicates)
                    )
        return expanded_predicates

    def filter_queries_inconsistent_with_meta_knowledge_graph(self, queries, meta_knowledge_graph=None, with_inconsistent_queries=False):
        consistent_queries = []
        inconsistent_queries = []
        meta_knowledge_graph_predicate_map = defaultdict(list)
        for edge in meta_knowledge_graph.edges:
            meta_knowledge_graph_predicate_map[edge.predicate].append(edge)
        for query in queries:
            # Check each edge that it's subject and object are consistent with the meta KG.
            query_graph = query.message.query_graph
            is_consistent_query = True
            for edge_id, edge in query_graph.edges.items():
                if edge.predicates is None:
                    edge.predicates = [BIOLINK_RELATED_TO_ENTITY]
                subject_node = query_graph.nodes[edge.subject]
                object_node = query_graph.nodes[edge.object]
                predicate = edge.predicates[0]
                if predicate in meta_knowledge_graph_predicate_map:
                    found_consistent_edge = False
                    for meta_edge in meta_knowledge_graph_predicate_map[predicate]:
                        if subject_node.categories is not None and object_node.categories is not None:
                            if subject_node.categories[0] == meta_edge.subject and object_node.categories[0] == meta_edge.object:
                                found_consistent_edge = True
                                break
                    if not found_consistent_edge:
                        query.error('Edge predicate subject/object mismatch with meta knowledge graph.')
                        is_consistent_query = False
                        inconsistent_queries.append(query)
                else:
                    query.error(f'Predicate: {predicate.get_curie()} not supported in our meta knowledge graph.')
                    is_consistent_query = False
                    inconsistent_queries.append(query)
                    break
            if is_consistent_query:
                # check that queries aren't duplicates
                is_duplicate = False
                for consistent_query in consistent_queries:
                    is_duplicate = Message.check_messages_are_equal(query.message, consistent_query.message)
                    if is_duplicate:
                        query.error(f'Duplicate query.')
                        inconsistent_queries.append(query)
                        break
                if not is_duplicate:
                    consistent_queries.append(query)
        if with_inconsistent_queries:
            return consistent_queries, inconsistent_queries
        return consistent_queries

    def merge_responses(self, target_query, response_queries):
        response_query = target_query.get_copy()
        for query in response_queries:
            # Update message
            response_query.message.update(
                    query.message.knowledge_graph,
                    query.message.results,
                    )
            # Update Logs
            response_query.logger.add_logs(query.logger.to_dict())
        return response_query

    def undo_normalization(self, response_query, normalization_map):
        for normalized_curie, passed_curie in normalization_map.items():
            response_query.message = response_query.message.find_and_replace(normalized_curie, passed_curie)
        return response_query
    
