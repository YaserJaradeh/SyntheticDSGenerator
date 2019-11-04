from writers.BaseWriter import BaseWriter
from utils.random_utils import get_random_name, get_random_datetime
import os
import csv


class ORKGWriter(BaseWriter):
    predefined_predicates = {}
    predefined_resources = {}

    def __init__(self, provenance, predefined_predicates=None, predefined_resources=None):
        if predefined_predicates is None:
            self.predefined_predicates = {
                "Has DOI": "P26",
                "Has Author": "P27",
                "Has publication month": "P28",
                "Has publication year": "P29",
                "Has Research field": "P30",
                "Has contribution": "P31",
                "Has research problem": "P32"
            }
        if predefined_resources is None:
            self.predefined_resources = {"Research field": "R11"}
        BaseWriter.__init__(self, provenance)

    def write_2_writer(self, writer, row, prov_info, key=None, header=False):
        if not self.provenance:
            writer.writerow(row)
        else:
            if header:
                writer.writerow(row + ["createdAt", 'createdBy'])
            else:
                writer.writerow(row + [prov_info[key][1], prov_info[key][0]])

    def write(self, path, nodes, edges, literals, statements, prov_info):
        resource_nodes = {}
        literal_nodes = {}
        predicate_nodes = {}
        index = 1
        literal_count = 0
        predicate_ids = {}
        ###############################################
        if not os.path.exists(path):
            os.makedirs(path)
        ###############################################
        with open(os.path.join(path, 'Literals_header.csv'), 'w') as out:
            writer = csv.writer(out)
            header = [":ID", "label", "literal_id", ":LABEL"]
            self.write_2_writer(writer, header, prov_info, header=True)
        with open(os.path.join(path, 'Literals.csv'), 'w') as out:
            writer = csv.writer(out)
            for key, value in literals.items():
                if key not in literal_nodes:
                    literal_nodes[key] = f'literal{index}'
                    index = index + 1
                self.write_2_writer(writer, [literal_nodes[key], value, f'L{literal_count}', 'Literal'], prov_info, key=key)
                literal_count = literal_count + 1
        print("Done writing literals")
        ##############################################
        predicate_count = 100
        with open(os.path.join(path, 'Predicates_header.csv'), 'w') as out:
            writer = csv.writer(out)
            header = [":ID", "label", "predicate_id", ":LABEL"]
            self.write_2_writer(writer, header, prov_info, header=True)
        with open(os.path.join(path, 'Predicates.csv'), 'w') as out:
            writer = csv.writer(out)
            for pred in edges:
                if pred not in predicate_nodes:
                    predicate_nodes[pred] = f'predicate{predicate_count}'
                if pred in self.predefined_predicates:
                    self.write_2_writer(writer, [predicate_nodes[pred], pred, self.predefined_predicates[pred], 'Predicate'], prov_info, key=pred)
                    predicate_ids[pred] = self.predefined_predicates[pred]
                else:
                    self.write_2_writer(writer, [predicate_nodes[pred], pred, f'P{predicate_count}', 'Predicate'], prov_info, key=pred)
                    predicate_ids[pred] = f'P{predicate_count}'
                predicate_count = predicate_count + 1
        print("Done writing predicates")
        ##############################################
        resources = {}
        with open(os.path.join(path, 'Resources_header.csv'), 'w') as out:
            writer = csv.writer(out)
            header = [":ID", "label", "resource_id", ":LABEL"]
            self.write_2_writer(writer, header, prov_info, header=True)
        with open(os.path.join(path, 'Resources.csv'), 'w') as out:
            writer = csv.writer(out)
            index = 1
            resource_count = 100
            for key, value in nodes.items():
                if key not in resource_nodes:
                    resource_nodes[key] = f'resource{index}'
                    index = index + 1
                if value in self.predefined_resources:
                    row = [resource_nodes[key], value, self.predefined_resources[value], 'Resource']
                else:
                    row = [resource_nodes[key], value, f'R{resource_count}', 'Resource']
                    resource_count = resource_count + 1
                resources[key] = row
            #################################
            classes_nodes = set({})
            class_count = 1
            for sub, pred, obj in statements:
                if pred == 'is a':
                    row = resources[sub]
                    row[3] = f'{row[3]};{nodes[obj].strip().replace(" ", "_")}'
                    classes_nodes.add((nodes[obj], obj))
            with open(os.path.join(path, 'Classes_header.csv'), 'w') as inner_out:
                writer2 = csv.writer(inner_out)
                header = [":ID", "label", "class_id", ":LABEL"]
                self.write_2_writer(writer2, header, prov_info, header=True)
            with open(os.path.join(path, 'Classes.csv'), 'w') as inner_out:
                writer2 = csv.writer(inner_out)
                for value, key in classes_nodes:
                    self.write_2_writer(writer2, [f'class{class_count}', value, value.strip().replace(" ", "_"), 'Class'], prov_info, key=key)
                    class_count = class_count + 1
            print("Done writing classes")
            for key, value in resources.items():
                self.write_2_writer(writer, value, prov_info, key=key)
            print("Done writing resources")
        ##############################################
        statement_count = 0
        with open(os.path.join(path, 'Relations_header.csv'), 'w') as out:
            writer = csv.writer(out)
            header = [":START_ID", ":END_ID", ":TYPE", "predicate_id", "statement_id"]
            self.write_2_writer(writer, header, prov_info, header=True)
        with open(os.path.join(path, 'Relations.csv'), 'w') as out:
            writer = csv.writer(out)
            for sub, pred, obj in statements:
                if pred == 'is a':
                    continue
                subject_id = resource_nodes[sub]
                predicate_id = predicate_ids[pred]
                if obj.startswith("___l_"):
                    object_id = literal_nodes[obj]
                    relation_type = "HAS_VALUE_OF"
                else:
                    object_id = resource_nodes[obj]
                    relation_type = "RELATES_TO"
                self.write_2_writer(writer, [subject_id, object_id, relation_type, predicate_id, f'S{statement_count}'], prov_info, key=(sub, pred, obj))
                statement_count = statement_count + 1
        print("Done writing statements")
