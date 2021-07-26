from semantic_operations.semantic_processor import SemanticProcessor
from trapi_model.query_graph import QueryGraph

sp = SemanticProcessor()

#standard query
query_graph = QueryGraph.load(trapi_version = '1.1', biolink_version = None, query_graph={
            "nodes": {
                "n0": {
                    "ids": [
                        "CHEMBL:CHEMBL1201583"
                    ],
                    "categories": [
                        "biolink:NamedThing"
                    ],
                    "constraints": []
                },
                "n1": {
                    "ids": [
                        "MONDO:0007254"
                    ],
                    "categories": [
                        "biolink:NamedThing"
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
                    "subject": "n0",
                    "object": "n1",
                    "constraints": [
                        {
                            "name": "predicate_proxy",
                            "id": "CHP:PredicateProxy",
                            "operator": "==",
                            "value": [
                                "EFO:0000714"
                            ],
                            "unit_id": None,
                            "unit_name": None,
                            "not": False
                        },
                        {
                            "name": "EFO:0000714",
                            "id": "EFO:0000714",
                            "operator": ">",
                            "value": 1186,
                            "unit_id": None,
                            "unit_name": None,
                            "not": False
                        }
                    ]
                }
            }
})
query_graph = sp.process(query_graph)

#gene wildcard to disease proxy
query_graph = QueryGraph.load(trapi_version = '1.1', biolink_version = None, query_graph={
            "nodes": {
                    "n0": {
                        "ids": None,
                        "categories": [
                            "biolink:GenomicEntity"
                        ],
                        "constraints": []
                    },
                    "n1": {
                        "ids": [
                            "MONDO:0007254"
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
                    "subject": "n0",
                    "object": "n1",
                    "constraints": [
                        {
                            "name": "predicate_proxy",
                            "id": "CHP:PredicateProxy",
                            "operator": "==",
                            "value": [
                                "EFO:0000714"
                            ],
                            "unit_id": None,
                            "unit_name": None,
                            "not": False
                        },
                        {
                            "name": "EFO:0000714",
                            "id": "EFO:0000714",
                            "operator": ">",
                            "value": 1186,
                            "unit_id": None,
                            "unit_name": None,
                            "not": False
                        }
                    ]
                }
            }
})

query_graph = sp.process(query_graph)

#drug wildcard to disease proxy
query_graph = QueryGraph.load(trapi_version = '1.1', biolink_version = None, query_graph={
    "nodes": {
                "n0": {
                    "ids": None,
                    "categories": [
                        "biolink:Drug"
                    ],
                    "constraints": []
                },
                "n1": {
                    "ids": [
                        "MONDO:0007254"
                    ],
                    "categories": [
                        "biolink:NamedThing"
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
                    "subject": "n0",
                    "object": "n1",
                    "constraints": [
                        {
                            "name": "predicate_proxy",
                            "id": "CHP:PredicateProxy",
                            "operator": "==",
                            "value": [
                                "EFO:0000714"
                            ],
                            "unit_id": None,
                            "unit_name": None,
                            "not": False
                        },
                        {
                            "name": "EFO:0000714",
                            "id": "EFO:0000714",
                            "operator": ">",
                            "value": 687,
                            "unit_id": None,
                            "unit_name": None,
                            "not": False
                        }
                    ]
                }
            }
})

query_graph = sp.process(query_graph)

query_graph = QueryGraph.load(trapi_version= '1.1', biolink_version= None, query_graph={
    "nodes": {
                "n0": {
                    "ids": [
                        "MONDO:0007254"
                    ],
                    "categories": [
                        "biolink:NamedThing"
                    ],
                    "constraints": []
                },
                "n1": {
                    "ids": [
                        "ENSEMBL:ENSG00000187889"
                    ],
                    "categories": [
                        "biolink:NamedThing"
                    ],
                    "constraints": []
                },
                "n2": {
                    "ids": [
                        "EFO:0000714"
                    ],
                    "categories": [
                        "biolink:NamedThing"
                    ],
                    "constraints": []
                },
                "n3": {
                    "ids": None,
                    "categories": [
                        "biolink:NamedThing"
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
                },
                "e1": {
                    "predicates": [
                        "biolink:related_to"
                    ],
                    "relation": None,
                    "subject": "n0",
                    "object": "n2",
                    "constraints": [
                        {
                            "name": "survival_time",
                            "id": "EFO:0000714",
                            "operator": ">",
                            "value": 3446,
                            "unit_id": None,
                            "unit_name": None,
                            "not": False
                        }
                    ]
                },
                "e2": {
                    "predicates": [
                        "biolink:related_to"
                    ],
                    "relation": None,
                    "subject": "n3",
                    "object": "n0",
                    "constraints": []
                }
            }
        })
#query_graph = sp.process(query_graph)
#print(query_graph)

#gene to gene
query_graph = QueryGraph.load(trapi_version= '1.1', biolink_version= None, query_graph={
      "nodes": {
        "n0": {
          "ids": None,
          "categories": [
            "biolink:Gene"
          ],
          "constraints": []
        },
        "n1": {
          "ids": [
            "ENSEMBL:ENSG00000184368"
          ],
          "categories": [
            "biolink:NamedThing"
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
          "subject": "n0",
          "object": "n1",
          "constraints": []
        }
      }
    }
  
)
query_graph = sp.process(query_graph)
print(query_graph)