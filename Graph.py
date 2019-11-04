import os
import random
from utils.random_utils import get_random_datetime

class Graph:
    edges = set({})
    nodes = dict({})
    literals = dict({})
    statements = []
    count = 0
    provenance_info = dict({})

    def __init__(self, edges=None, literals=None, nodes=None):
        self.edges = set({})
        if edges is not None:
            self.edges = edges
        self.literals = dict({})
        if literals is not None:
            self.literals = literals
        self.nodes = dict({})
        self.count = 0
        if nodes is not None:
            self.nodes = nodes
            self.count = len(self.nodes)
        self.statements = []
        self.provenance_info = dict({})

    def __create_id(self, literal=False):
        lit = ""
        if literal:
            lit = "l_"
        internal_id = f'___{lit}{self.count}'
        self.count = self.count + 1
        return internal_id

    def add_statement(self, sub, pred, obj, literal=False):
        # add predicate to the set
        self.edges.add(pred)
        if pred not in self.provenance_info:
            self.provenance_info[pred] = (f'User {random.randint(1, 1000)}', get_random_datetime())
        # check if subject is an ID
        m_subject = None
        if sub.startswith("___"):
            if sub not in self.nodes:
                raise LookupError("Id not in internal dictionary of nodes")
            m_subject = sub
        else:
            m_subject = self.__create_id()
            self.nodes[m_subject] = sub
            if m_subject not in self.provenance_info:
                self.provenance_info[m_subject] = (f'User {random.randint(1, 100)}', get_random_datetime())
        # check if object is an ID
        m_object = None
        if literal:
            if obj.startswith("___l_"):
                if obj not in self.literals:
                    raise LookupError("Id not in internal dictionary of literals")
                m_object = obj
            else:
                m_object = self.__create_id(True)
                self.literals[m_object] = obj
                if m_object not in self.provenance_info:
                    self.provenance_info[m_object] = (f'User {random.randint(1, 100)}', get_random_datetime())
        else:
            if obj.startswith("___"):
                if obj not in self.nodes:
                    raise LookupError("Id not in internal dictionary of nodes")
                m_object = obj
            else:
                m_object = self.__create_id()
                self.nodes[m_object] = obj
                if m_object not in self.provenance_info:
                    self.provenance_info[m_object] = (f'User {random.randint(1, 100)}', get_random_datetime())
        # add the statement
        self.statements.append((m_subject, pred, m_object))
        # add statement provenance info
        if (m_subject, pred, m_object) not in self.provenance_info:
            self.provenance_info[(m_subject, pred, m_object)] = (f'User {random.randint(1, 100)}', get_random_datetime())
        # return the ids for reuse
        return m_subject, pred, m_object

    def serialize(self, writers, path, count):
        # serialize the graph using the passed writers
        for writer in writers:
            writer.write(os.path.join(path, str(count)), self.nodes, self.edges, self.literals, self.statements, self.provenance_info)

    def debug(self):
        print("=" * 20 + " Edges " + "=" * 20)
        print(self.edges)
        print("=" * 20 + " Nodes " + "=" * 20)
        print(self.nodes)
        print("=" * 20 + " Literals " + "=" * 20)
        print(self.literals)
        print("=" * 20 + " Statements " + "=" * 20)
        print(self.statements)