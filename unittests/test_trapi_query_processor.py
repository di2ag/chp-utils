import unittest
import logging
import json
import sys
from copy import deepcopy

import trapi_model
trapi_model.set_biolink_debug_mode(False)
from trapi_model.query import Query
from trapi_model.meta_knowledge_graph import MetaKnowledgeGraph
from trapi_model.biolink.constants import *

from chp_utils.trapi_query_processor import BaseQueryProcessor
from chp_utils.conflation import ConflationMap
from chp_utils.curie_database import CurieDatabase

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)

logger_root = logging.getLogger()
logger_root.setLevel(logging.INFO)

class TestTrapiQueryProcessor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestTrapiQueryProcessor, cls).setUpClass()
        # Load in Sample queries
        with open('query_samples/standard_batch_onehop_queries.json') as f_:
            cls.queries = json.load(f_)
        # Load in Test Meta KG
        cls.meta_knowledge_graph = MetaKnowledgeGraph.load('1.1', None, filename='test_meta_knowledge_graph.json')
        # Load in test conflation map
        cls.conflation_map = ConflationMap(conflation_map_filename='test_conflation.json')
        # Load in test curies data file
        cls.curies = CurieDatabase(curies_filename='test_curies.json')
        #TODO: Load in approved answers
    
    def save_test_case(self, filepath, json_obj):
        with open(filepath, 'w') as f_:
            json.dump(json_obj, f_, indent=2)

    def load_test_answers(self, filepath):
        with open(filepath) as f_:
            return json.load(f_)
    
    def run_test(self, answers_filepath, test_queries):
        correct_queries = self.load_test_answers(answers_filepath)
        for test_query_list, correct_query_list in zip(test_queries, correct_queries):
            for test_query, correct_query in zip(test_query_list, correct_query_list):
                # Pop out logs and pk
                test_query.pop("pk")
                test_query.pop("logs")
                correct_query.pop("pk")
                correct_query.pop("logs")
                # Assert
                self.assertEqual(test_query, correct_query)

    def generate_answers(
            self, 
            method_name=None,
            save_path=None,
            past_queries=None,
            debug=False,
            answers_to_dict=True,
            **kwargs):
        if debug:
            print('Testing: {}'.format(method_name))
        # Always make copy of test queries
        queries = deepcopy(self.queries)
        answers = []
        if past_queries is None:
            for json_query in queries:
                query = Query.load(json_query["trapi_version"], None, query=json_query)
                if debug:
                    print(query.json())
                    input('<<<<< Ready?')
                query_processor = BaseQueryProcessor(query)
                expanded_queries = query_processor.expand_batch_query(query)
                if method_name is None:
                    answer_queries = expanded_queries
                else:
                    query_processor_method = getattr(query_processor, method_name)
                    answer_queries = query_processor_method(expanded_queries, **kwargs)
                answer_dict = [ans_query.to_dict() for ans_query in answer_queries]
                if debug:
                    print(json.dumps(answer_dict, indent=2))
                    input('>>>>> Continue?')
                if answers_to_dict:
                    answers.append(answer_dict)
                else:
                    answers.append(answer_queries)

        else:
            for json_query, past_queries_list in zip(queries, past_queries):
                query = Query.load(json_query["trapi_version"], None, query=json_query)
                if debug:
                    print(query.json())
                    input('<<<<< Ready?')
                query_processor = BaseQueryProcessor(query)
                query_processor_method = getattr(query_processor, method_name)
                answer_queries = query_processor_method(past_queries_list, **kwargs)
                answer_dict = [ans_query.to_dict() for ans_query in answer_queries]
                if debug:
                    print(json.dumps(answer_dict, indent=2))
                    input('>>>>> Continue?')
                if answers_to_dict:
                    answers.append(answer_dict)
                else:
                    answers.append(answer_queries)
        
        if save_path is not None:
            self.save_test_case(
                    save_path, 
                    answers,
                    )
        return answers

    def generate_expand_batch_answers(self, save_path=None):
        return self.generate_answers(save_path=save_path)

    def generate_normalize_to_preferred_answers(self, save_path=None):
        return self.generate_answers(
                method_name='normalize_to_preferred',
                save_path=save_path,
                meta_knowledge_graph=self.meta_knowledge_graph,
                )
    
    def generate_conflate_categories_answers(self, save_path=None):
        return self.generate_answers(
                method_name='conflate_categories',
                save_path=save_path,
                conflation_map=self.conflation_map,
                )

    def generate_expand_supported_ontological_descendants_answers(self, save_path=None):
        return self.generate_answers(
                method_name='expand_supported_ontological_descendants',
                save_path=save_path,
                curies_database=self.curies,
                )

    def generate_expand_with_semantic_ops_answers(self, save_path=None):
        return self.generate_answers(
                method_name='expand_with_semantic_ops',
                save_path=save_path,
                meta_knowledge_graph=self.meta_knowledge_graph,
                )

    def generate_filter_queries_inconsistent_with_meta_knowledge_graph_answers(self, save_path=None):
        return self.generate_answers(
                method_name='filter_queries_inconsistent_with_meta_knowledge_graph',
                save_path=save_path,
                meta_knowledge_graph=self.meta_knowledge_graph,
                )

    def generate_normalization_workflow_answers(self, save_path=None):
        # Expand
        expand_queries = self.generate_answers(
                answers_to_dict=False,
                )
        # Normalize to Preferred Curies
        normalize_queries = self.generate_answers(
                method_name='normalize_to_preferred',
                past_queries=expand_queries,
                answers_to_dict=False,
                meta_knowledge_graph=self.meta_knowledge_graph,
                )
        # Conflate
        conflate_queries = self.generate_answers(
                method_name='conflate_categories',
                past_queries=normalize_queries,
                answers_to_dict=False,
                conflation_map=self.conflation_map,
                )
        # Onto Expand
        onto_queries = self.generate_answers(
                method_name='expand_supported_ontological_descendants',
                past_queries=conflate_queries,
                answers_to_dict=False,
                curies_database=self.curies,
                )
        # Semantic Ops Expand
        semops_queries = self.generate_answers(
                method_name='expand_with_semantic_ops',
                past_queries=onto_queries,
                answers_to_dict=False,
                meta_knowledge_graph=self.meta_knowledge_graph,
                )
        # Filter out inconsistent queries
        consistent_queries = self.generate_answers(
                method_name='filter_queries_inconsistent_with_meta_knowledge_graph',
                save_path=save_path,
                past_queries=semops_queries,
                answers_to_dict=True,
                meta_knowledge_graph=self.meta_knowledge_graph,
                )
        return consistent_queries

    def test_expand_batch(self):
        expanded_batch_queries = self.generate_expand_batch_answers()
        self.run_test(
                'json_responses/test_expand_batch_answers.json',
                expanded_batch_queries,
                )

    def test_normalize_to_preferred(self):
        expanded_normalized_queries = self.generate_normalize_to_preferred_answers()
        self.run_test(
                'json_responses/test_normalized_to_preferred_answers.json',
                expanded_normalized_queries,
                )

    def test_conflate_categories(self):
        expanded_conflated_queries = self.generate_conflate_categories_answers()
        self.run_test(
                'json_responses/test_conflate_categories_answers.json',
                expanded_conflated_queries,
                )

    def test_expand_supported_ontological_descendants(self):
        expanded_onto_queries = self.generate_expand_supported_ontological_descendants_answers()
        self.run_test(
                'json_responses/test_expand_supported_ontological_descendants_answers.json',
                expanded_onto_queries,
                )
    
    def test_filter_queries_inconsistent_with_meta_knowledge_graph(self):
        expanded_filtered_queries = self.generate_filter_queries_inconsistent_with_meta_knowledge_graph_answers()
        self.run_test(
                'json_responses/test_expand_and_filter_with_meta_kg_answers.json',
                expanded_filtered_queries,
                )

    def test_normalization_workflow(self):
        workflow_queries = self.generate_normalization_workflow_answers()
        self.run_test(
                'json_responses/test_normalization_workflow_answers.json',
                workflow_queries,
                )

if __name__ == '__main__':
    test_case = TestTrapiQueryProcessor()
    test_case.setUpClass()
    test_case.generate_expand_batch_answers(
            'json_responses/test_expand_batch_answers.json',
            )
    test_case.generate_normalize_to_preferred_answers(
            'json_responses/test_normalized_to_preferred_answers.json',
            )
    test_case.generate_conflate_categories_answers(
            'json_responses/test_conflate_categories_answers.json',
            )
    test_case.generate_expand_supported_ontological_descendants_answers(
            'json_responses/test_expand_supported_ontological_descendants_answers.json',
            )
    test_case.generate_expand_with_semantic_ops_answers(
            'json_responses/test_expand_with_semantic_ops_answers.json',
            )
    test_case.generate_filter_queries_inconsistent_with_meta_knowledge_graph_answers(
            'json_responses/test_expand_and_filter_with_meta_kg_answers.json',
            )
    test_case.generate_normalization_workflow_answers(
            'json_responses/test_normalization_workflow_answers.json',
            )
    '''
    test_case.generate_expand_batch_answers()
    test_case.generate_normalize_to_preferred_answers()
    test_case.generate_conflate_categories_answers()
    test_case.generate_expand_supported_ontological_descendants_answers()
    test_case.generate_expand_with_semantic_ops_answers()
    test_case.generate_filter_queries_inconsistent_with_meta_knowledge_graph_answers()
    test_case.generate_normalization_workflow_answers()
    '''
