import numpy as np
import html
import pandas as pd


def get_classes(path, only_include=None):
    classes = []
    with open(path, 'r') as in_file:
        for index, line in enumerate(in_file):
            #if index > 500000:
            #    break
            parts = line.split("> ")
            if parts[1] == "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
                if only_include is None:
                    classes.append(f'{parts[2]}')
                elif any(ns in parts[2] for ns in only_include):
                    classes.append(f'{parts[2]}')
    return np.unique(classes).tolist()


def get_instances(path, class_url):
    instances = []
    with open(path, 'r') as in_file:
        for index, line in enumerate(in_file):
            #if index > 500000:
            #    break
            parts = line.split("> ")
            if parts[1] == "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type" and parts[2] == class_url:
                instances.append(parts[0])
    return np.unique(instances).tolist()


def get_classes_and_instances(path, only_include=None):
    classes = {}
    with open(path, 'r') as in_file:
        for index, line in enumerate(in_file):
            parts = line.split("> ")
            if parts[1] == "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
                if only_include is None:
                    if parts[2] not in classes:
                        classes[parts[2]] = []
                    classes[parts[2]].append(parts[0])
                elif any(ns in parts[2] for ns in only_include):
                    if parts[2] not in classes:
                        classes[parts[2]] = []
                    classes[parts[2]].append(parts[0])
    result = {}
    for key, value in classes.items():
        result[key] = np.unique(value).tolist()
    return result


def get_properties_and_relations(path, instances):
    properties = []
    relations = []
    with open(path, 'r') as in_file:
        for index, line in enumerate(in_file):
            #if index > 500000:
            #    break
            parts = line.split("> ")
            if parts[0] in instances:
                if parts[1] == "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
                    continue
                predicate = parts[1][parts[1].rfind('/') + 1:]
                if parts[2][0] != '<':  # literal to be added as property
                    properties.append(predicate)
                else:
                    relations.append(predicate)
    return np.unique(properties).tolist(), np.unique(relations).tolist()


def get_content(path: str, instances: list, class_name: str, exceptions: list = None):
    url_id_links = {}
    count = 0
    content = {}
    relations = []
    with open(path, 'r') as in_file:
        for index, line in enumerate(in_file):
            #if index > 500000:
            #    break
            parts = line.split("> ")
            if len(parts) <= 3:  # Sanity check
                continue
            if parts[0] in instances:
                if parts[1] == "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
                    continue
                if '#' in parts[1]:
                    predicate = parts[1][parts[1].rfind('#') + 1:]
                else:
                    predicate = parts[1][parts[1].rfind('/') + 1:]
                if not parts[0] in content:
                    url_id_links[parts[0]] = f'{class_name}{count}'
                    content[parts[0]] = {':ID': url_id_links[parts[0]]}
                    count = count + 1
                if parts[2][0] != '<':  # literal to be added as property
                    content[parts[0]][predicate] = html.unescape(parts[2][1:parts[2].rfind('"^^')])
                elif exceptions is not None and parts[1][1:] in exceptions:
                    content[parts[0]][predicate] = html.unescape(parts[2][1:parts[2].rfind('>')])
                else:
                    relations.append((parts[0], parts[1], parts[2]))
    return content, relations, url_id_links


if __name__ == '__main__':
    path = '/media/jaradeh/HDD/PG/RDF2PG/rdf/part2.nt'
    classes_and_content = get_classes_and_instances(path, ['http://mag.graph', 'http://ma-graph.org'])
    for cls, inst in classes_and_content.items():
        print("Done with the instances")
        content, relations, nodes_temp_ids =\
            get_content(path, inst, cls[cls.rfind('/')+1:],
                        ['http://www.w3.org/2002/07/owl#sameAs',
                         'http://mag.graph/property/grid',
                         'http://xmlns.com/foaf/0.1/homepage',
                         'http://www.w3.org/2000/01/rdf-schema#seeAlso',
                         'dbpedia.org/ontology/location',
                         'http://purl.org/spar/fabio/hasURL'
                         ])
        print("Done with the content")
        df = pd.DataFrame.from_dict(content, orient='index')
        df.to_csv(f'../out/{cls[cls.rfind("/")+1:]}.csv', index=False)
        print(f'done with {cls[cls.rfind("/")+1:]}')
