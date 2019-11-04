from writers.BaseWriter import BaseWriter
from utils.random_utils import get_random_name, get_random_datetime
import os


class RDFWriter(BaseWriter):
    reification_type = None
    ns = "http://orkg.org/vocab/"
    id_seed = 1111111
    triple_count = 2211111
    done = set({})
    # a dictionary of pre-defined namespace with predicates can be added

    def __init__(self, provenance, reification_type=None, namespace=None):
        BaseWriter.__init__(self, provenance)
        if (reification_type is not None) and (reification_type not in ['Std', 'SP', 'NG']):
            raise ValueError("Not a correct reification type!")
        self.reification_type = reification_type
        if namespace is not None:
            self.ns = namespace
        self.id_seed = 1111111
        self.triple_count = 2211111

    def write(self, path, nodes, edges, literals, statements, prov_info):
        ids = {}
        ###############################################
        if not os.path.exists(path):
            os.makedirs(path)
        ###############################################
        with open(os.path.join(path, "dump.nt"), 'w') as out:
            for sub, pred, obj in statements:
                if sub not in ids:
                    ids[sub] = self.id_seed
                    self.id_seed = self.id_seed + 1
                subject_nt = f'<{self.ns}entity/{ids[sub]}>'
                if pred == 'is a':
                    predicates_nt = '<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>'
                    object_nt = f'<{self.ns}class/{nodes[obj].strip().replace(" ", "_")}>'
                else:
                    predicates_nt = f'<{self.ns}property/{pred.strip().replace(" ", "_")}>'
                    if obj.startswith("___l_"):
                        clean_object = literals[obj].strip().replace("\"", "")
                        object_nt = f'"{clean_object}"^^<http://www.w3.org/2001/XMLSchema#string>'
                    else:
                        if obj not in ids:
                            ids[obj] = self.id_seed
                            self.id_seed = self.id_seed + 1
                        object_nt = f'<{self.ns}entity/{ids[obj]}>'
                out.write(f'{subject_nt} {predicates_nt} {object_nt} .\n')
                if sub not in self.done:
                    self.done.add(sub)
                    if self.provenance:
                        out.write(
                            f'{subject_nt} <http://purl.org/dc/terms/created> "{prov_info[sub][1]}"^^<http://www.w3.org/2001/XMLSchema#dateTime> .\n')
                        out.write(
                            f'{subject_nt} <http://purl.org/dc/elements/1.1/creator> "{prov_info[sub][0]}"^^<http://www.w3.org/2001/XMLSchema#string> .\n')
                    out.write(f'{subject_nt} <http://www.w3.org/2000/01/rdf-schema#label> "{nodes[sub]}"^^<http://www.w3.org/2001/XMLSchema#string> .\n')
                if not obj.startswith("___l_") and obj not in self.done:
                    self.done.add(obj)
                    if self.provenance:
                        out.write(
                            f'{object_nt} <http://purl.org/dc/terms/created> "{prov_info[obj][1]}"^^<http://www.w3.org/2001/XMLSchema#dateTime> .\n')
                        out.write(
                            f'{object_nt} <http://purl.org/dc/elements/1.1/creator> "{prov_info[obj][0]}"^^<http://www.w3.org/2001/XMLSchema#string> .\n')
                    out.write(f'{object_nt} <http://www.w3.org/2000/01/rdf-schema#label> "{nodes[obj]}"^^<http://www.w3.org/2001/XMLSchema#string> .\n')
                if self.provenance:
                    out.write(
                        f'<{self.ns}triple/{self.triple_count}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/1999/02/22-rdf-syntax-ns#Statement> .\n')
                    out.write(
                        f'<{self.ns}triple/{self.triple_count}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#subject> {subject_nt} .\n')
                    out.write(
                        f'<{self.ns}triple/{self.triple_count}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#predicate> {predicates_nt} .\n')
                    out.write(
                        f'<{self.ns}triple/{self.triple_count}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#object> {object_nt} .\n')
                    out.write(
                        f'<{self.ns}triple/{self.triple_count}> <http://purl.org/dc/terms/created> "{prov_info[(sub, pred, obj)][1]}"^^<http://www.w3.org/2001/XMLSchema#dateTime> .\n')
                    out.write(
                        f'<{self.ns}triple/{self.triple_count}> <http://purl.org/dc/elements/1.1/creator> "{prov_info[(sub, pred, obj)][0]}"^^<http://www.w3.org/2001/XMLSchema#string> .\n')
                    self.triple_count = self.triple_count + 1
            out.flush()
        print("Done baby")