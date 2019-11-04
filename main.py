from Graph import Graph
from writers.RDFWriter import RDFWriter
from writers.ORKGWriter import ORKGWriter
from utils.random_utils import get_random_name, get_random_text

if __name__ == "__main__":
    g = Graph()
    g.add_statement("ORKG a system walkthrough", "is a", "Paper")
    g.add_statement("___0", "has abstract", get_random_text(), True)
    g.add_statement("___0", "has author", get_random_name())
    g.serialize([RDFWriter("./test.nt"), ORKGWriter("./")])
    g.debug()
