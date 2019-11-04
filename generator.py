import json
from Graph import Graph
from writers.RDFWriter import RDFWriter
from writers.ORKGWriter import ORKGWriter
from utils.random_utils import get_random_title, get_random_text, get_random_name
import random
import copy
import os
import time


class PaperGenerator:
    count = 0
    graph = None
    path = ''
    writers = []
    resources = {}
    naming_counts = {}

    def __init__(self, count, dir_path='./', *writers):
        if not os.path.isdir(dir_path):
            raise ValueError("Path should be a path of a directory not a file")
        if not isinstance(count, list):
            self.count = [count]
        else:
            self.count = count
        self.count = sorted(self.count)
        self.path = dir_path
        self.graph = Graph()
        self.writers = writers
        self.naming_counts = {}

    def generate_needed(self):
        fields = set([])
        # generate research field node and random research fields
        with open('./data/fields.json') as in_file:
            research_fields = json.load(in_file)
            flag = False
            for field in research_fields:
                if not flag:
                    s, _, o = self.graph.add_statement("Research field", 'has subfield', field['name'])
                    flag = True
                else:
                    _, _, o = self.graph.add_statement(s, 'has subfield', field['name'])
                    fields.add(o)
                if "subfields" in field:
                    for subfield in field['subfields']:
                        s2, _, o2 = self.graph.add_statement(o, 'has subfield', subfield['name'])
                        fields.add(o2)
                        if "subfields" in subfield:
                            for subfield2 in subfield['subfields']:
                                _, _, o3 = self.graph.add_statement(o2, 'has subfield', subfield2['name'])
                                fields.add(o3)
        return list(fields)

    def get_value(self, option, prop, key):
        if prop <= 0:
            if key not in self.resources:
                return None
            return random.sample(self.resources[key], 1)[0]
        if option == 'T':
            return get_random_title()
        if option == 'N':
            return get_random_name()
        if isinstance(option, list):
            return option[random.randrange(len(option))]
        elif "%d" in option:
            if key not in self.naming_counts:
                self.naming_counts[key] = 0
            value = option.replace("%d", str(self.naming_counts[key]))
            self.naming_counts[key] = self.naming_counts[key] + 1
            return value
        else:
            return option

    def add_to_resources(self, pred, value):
        if pred not in self.resources:
            self.resources[pred] = set([])
        self.resources[pred].add(value)

    def run(self):
        fields = self.generate_needed()
        implementation_structure = {
            'Has programing language': ('R', 'Programming Language %d', 0.8, 0.6, 4),
            'Uses library': ('R', 'Library %d', 0.6, 0.32, 3),
            'Uses framework': ('R', 'Framework %d', 0.7, 0.3, 2),
            'Operating System': ('R', 'Operating System %d', 0.2, 0.1, 1)
        }
        result_structure = {
            'Has Metric': ('R', 'Metric %d', 1, 0.3, 1),
            'Has value': ('L', 'Value %d', 1, 0, 1)
        }
        evaluation_structure = {
            'On Dataset': ('R', 'Dataset %d', 0.7, 0.6, 2),
            'Using model': ('R', 'Model %d', 0.6, 0.32, 2),
            'Has Result': ('R', 'Result %d', 0.7, 0, 5, result_structure),
        }
        approach_structure = {
            'Methodology': ('L', 'Methodology %d', 0.75, 0.4, 1),
            'Has Method': ('R', 'Method %d', 0.5, 0.32, 2),
            'Uses Materials': ('R', 'Material %d', 0.8, 0.3, 2)
        }
        contribution_structure = {
            'Has research problem': ('R', 'Research Problem %d', 1, 0.4, 2),
            'Has Implementation': ('R', 'Implementation  %d', 0.6, 0.08, 1, implementation_structure),
            'Has Evaluation': ('R', 'Evaluation %d', 0.6, 0.1, 1, evaluation_structure),
            'Has Approach': ('R', 'Approach %d', 0.5, 0.05, 1, approach_structure),
        }
        structure = {
            'Has DOI': ('L', 'DOI %d', .65, 0, 1),
            'Has Author': ('R', 'Author %d', 1, .3, 5),
            'Has Research field': ('R', fields, 1, .4, 1),
            'Has contribution': ('R', 'Contribution %d', 1, 0.1, 2, contribution_structure)
        }
        start = 0
        for end in self.count:
            for i in range(start, end):
                start = end
                if i == 0:
                    sub, _, paper = self.graph.add_statement(f'Scientific Paper {i}', 'is a', "Paper")
                else:
                    sub, _, _ = self.graph.add_statement(f'Scientific Paper {i}', 'is a', paper)
                prob = random.random()
                if isinstance(structure, list):
                    template = random.randrange(len(structure))
                    self.process_structure(prob, template, sub)
                else:
                    self.process_structure(prob, structure, sub)
            self.graph.serialize(copy.deepcopy(self.writers), self.path, end)
            #  self.graph.debug()
        #  self.graph.serialize(self.writers)

    def process_structure(self, prob, structure, sub):
        for key, value in structure.items():
            for _ in range(random.randint(1, value[4])):
                if prob - value[2] <= 0:
                    obj = self.get_value(value[1], prob - value[3], key)
                    if obj is None:
                        obj = self.get_value(value[1], 10, key)
                    s, _, o = self.graph.add_statement(sub, key, obj, literal=value[0] == "L")
                    self.add_to_resources(key, s)
                    if not value[0] == "L":
                        self.add_to_resources(key, o)
                    if len(value) == 6:
                        self.process_structure(prob, value[5], o)


if __name__ == '__main__':
    start = time.time()
    gen = PaperGenerator(10, './out/',  RDFWriter(provenance=True), ORKGWriter(provenance=True))
    gen.run()
    end = time.time()
    print(f'Done in {end-start}ms')
