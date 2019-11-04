class BaseWriter:
    provenance = False

    def __init__(self, provenance):
        self.provenance = provenance

    def write(self, path, nodes, edges, literals, statements, prov_info):
        print("Base")