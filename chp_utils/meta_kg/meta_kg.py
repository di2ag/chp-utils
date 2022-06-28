import json

class MetaKg:
    def __init__(self) -> None:
        self.meta_kg_file = open('../schemas/meta-kg.json', 'r')
        self.meta_kg_data = json.load(self.meta_kg_file)
        self._load()

    def _load(self) -> None:
        nodes_data = self.meta_kg_data["nodes"]
        self.nodes_obj = Nodes._load(nodes_data)
        
        edges_data = self.meta_kg_data["edges"]
        self.edges_obj = Edges._load(edges_data)

    def to_dict(self) -> None:
        pass
class Nodes:
    def __init__(self) -> None:
        nodeCategories = {}
        pass
    def _load(node_data) -> None:
        pass
    def to_dict(self)-> dict: 
        pass
class Node:
    def __init__(self) -> None:
        self.id_prefixes = None
    
    def _load(self, category_data) -> None:
        pass

    def to_dict(self) -> None:
        pass

class Edges:
    def __init__(self, edge_data) -> None:
        self.edge_definitions = []
        self.edge_definitions_by_subject = {}
        self.edge_definitions_by_predicate = {}
        self.edge_definitions_object = {}

    def _load(self, edge_data) -> None:
        for edge_definition in edge_data:
            subject = edge_definition["subject"]
            predicate = edge_definition["predicate"]
            object = edge_definition["object"]
            edge_definition_obj = EdgeDefinition(subject, predicate, object)
            self.edge_definitions.append(edge_definition_obj)

            if self.edge_definitions_by_subject.get(subject) == None:
                self.edge_definitions_by_subject.update({subject:[edge_definition_obj]})
            else:
                definition_list = self.edge_definitions_by_subject.get(subject)
                definition_list.append(edge_definition_obj)
                self.edge_definitions_by_subject.update({subject:definition_list})

            if self.edge_definitions_by_predicate(predicate) == None:
                self.edge_definitions_by_predicate.update({predicate:[edge_definition_obj]})
            else:
                definition_list = self.edge_definitions_by_predicate.get(predicate)
                definition_list.append(edge_definition_obj)
                self.edge_definitions_by_predicate.update({definition_list})
    def to_dict(self)-> None:
        pass

class EdgeDefinition():
    def __init__(self, subject: str, predicate: str, object: str) -> None:
        self.subject = subject
        self.predicate = predicate
        self.object = object

if __name__ == "__main__":
    mkg = MetaKg()
    mkg._load()