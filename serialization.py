import igraph as ig, pandas as pd, numpy as np, os, json
from io import StringIO, BytesIO
from scipy.sparse import save_npz, load_npz

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

def ig_to_json(graph, path):
    assert isinstance(graph, ig.Graph)
    nodes = []
    edges = []

    if not 'layout' in graph.attributes():
        graph['layout'] = graph.layout_fruchterman_reingold(weights='weight', start_temp=3, grid='nogrid', niter=2000)

    for v, coords in zip(graph.vs, graph['layout']):
        v_id = str(v.index)
        v_attributes = v.attributes()
        v_label = v_attributes.pop('label', None)
        if not v_label:
            v_label = v_id
        v_size = v_attributes.pop('size', None)
        if v_size:
            v_size = float(v_size)
        v_x = coords[0]
        v_y = coords[1]
        node = dict(key=v_id, attributes={**v_attributes,
            **dict(label=v_label, size=v_size, x=v_x, y=v_y)})
        nodes.append(node)

    for e in graph.es:
        e_id = str(e.index)
        e_source = str(e.source)
        e_target = str(e.target)
        e_attributes = e.attributes()
        e_size = e_attributes.pop('size', None)
        if e_size:
            e_size = float(e_size)
        edge = dict(key=e_id, source=e_source, target=e_target, attributes={**e_attributes,
            **dict(size=e_size)})
        edges.append(edge)

    data = dict(nodes=nodes, edges=edges)
    with open(path, 'w') as f:
        json.dump(data, f, ensure_ascii=False, cls=NpEncoder)
    return os.path.exists(path)

def s_graph_from_adj_mat(adj_mat, labels=None):
    graph = ig.Graph.Weighted_Adjacency(adj_mat, loops=False)
    if labels:
        graph.vs['label'] = labels
    return graph

def df_to_json(df):
    json_buffer = StringIO()
    df.to_json(json_buffer, orient='index')
    json_buffer.seek(0)
    return json_buffer

def to_indexed_sparse(csr_mat, index, columns):
    file_buffer = BytesIO()
    file_buffer.writelines([(', '.join(index.to_list())+'\n').encode(), (', '.join(columns.to_list())+'\n').encode()])
    save_npz(file_buffer, csr_mat)
    file_buffer.seek(0)
    return file_buffer

def from_indexed_sparse(file_buffer):
    index = pd.Index(file_buffer.readline().decode('utf-8')[:-1].split(', '))
    columns = pd.Index(file_buffer.readline().decode('utf-8')[:-1].split(', '))
    csr_mat = load_npz(file_buffer)
    return csr_mat, index, columns