import trapi_model
from chp_utils.semantic_operations.semantic_processor import SemanticProcessor
from trapi_model.query_graph import QueryGraph

qg = QueryGraph.load(trapi_version='1.1', biolink_version=None, query_graph={ "nodes": {
        "n0": {
          "ids": ["ENSEMBL:ENSG00000008853"],
          "categories":["biolink:Gene"]
        },
        "n1": {
          "categories": ["biolink:Drug"]
                }
      },
      "edges": {
        "e01": {
          "predicates": ["biolink:related_to"],
          "subject": "n1",
          "object": "n0"
        }
      }})

sp = SemanticProcessor()
print(sp.process( query_graph=qg))
