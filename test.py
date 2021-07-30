import trapi_model
from chp_utils.semantic_operations.semantic_processor import SemanticProcessor
from trapi_model.query_graph import QueryGraph

qg = QueryGraph.load(trapi_version='1.1', biolink_version=None, query_graph={"nodes": {
                "n0": {
                    "ids": [
                        "MONDO:0007254"
                    ],
                    "categories": [
                        "biolink:DiseaseOrPhenotypicFeature"
                    ]
                },
                "n1": {
                 "categories":[
                         "biolink:Drug"
                        ]
                }
            },
            "edges": {
                "e0": {
                    "subject": "n0",
                    "object": "n1",
                    "predicates":["biolink:treated_by"]
 
                }
            }})

sp = SemanticProcessor()
print(sp.process( query_graph=qg))
