import trapi_model
from chp_utils.semantic_operations.semantic_processor import SemanticProcessor
from trapi_model.query_graph import QueryGraph

qg = QueryGraph.load(trapi_version='1.1', biolink_version=None, query_graph={"nodes": {
        "n0": {
          "ids": None,
          "categories": [
            "biolink:Gene"
          ],
          "constraints": []
        },
        "n1": {
          "ids": [
            "MONDO:0005301"
          ],
          "categories": [
            "biolink:Disease"
          ],
          "constraints": []
        }
      },
      "edges": {
        "e0": {
          "predicates": [
            "biolink:related_to"
          ],
          "relation": None,
          "subject": "n1",
          "object": "n0",
          "constraints": []
        }
      }})

sp = SemanticProcessor()
print(sp.process( query_graph=qg))
