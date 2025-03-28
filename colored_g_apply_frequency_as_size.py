import pandas as pd, numpy as np, json
from corpus import get_script_path
from os.path import join

hashtags_folder = join(get_script_path(), 'hashtags')

def combine_node_attributes(row):
    return row[['label', 'size', 'x', 'y', 'color']].to_dict()

def combine_edge_attributes(row):
    return row[['weight', 'size', 'color']].to_dict()

def disproportionate_normalize_series(series, new_min, new_max):
    old_min = series.min()
    old_max = series.max()
    
    # Normalize to [0, 1]
    normalized = (series - old_min) / (old_max - old_min)
    
    # Apply a non-linear transformation to push more values towards new_min
    transformed = np.power(normalized, 15)  # Adjust the exponent to control the disproportionate effect
    
    # Scale to [new_min, new_max]
    scaled = transformed * (new_max - new_min) + new_min
    
    return scaled

for candidate in ['lula', 'bolsonaro']:
    frequency_df = pd.read_csv(join(hashtags_folder, f'hashtags_{candidate}.csv'), index_col=0)
    frequency_df['hashtags.1'] = np.log10(frequency_df['hashtags.1']+1e-10)
    graph_file_path = join(hashtags_folder, f'hashtags_{candidate}_coocc_color_g.json')
    with open(graph_file_path) as graph_file:
        graph = json.load(graph_file)
    
    nodes_df = pd.DataFrame.from_records(graph['nodes'], index='key')
    nodes_df = nodes_df.drop('attributes', axis=1).join(pd.json_normalize(nodes_df['attributes']).set_index(nodes_df.index))
    nodes_df['size'] = nodes_df['label'].map(frequency_df['hashtags.1'].to_dict())
    
    graph['nodes'] = nodes_df.assign(attributes=nodes_df.apply(combine_node_attributes, axis=1)).drop(['label', 'size', 'x', 'y', 'color'], axis=1).reset_index(names='key').to_dict(orient='records')

    edges_df = pd.DataFrame.from_records(graph['edges'], index='key')
    edges_df = edges_df.drop('attributes', axis=1).join(pd.json_normalize(edges_df['attributes']).set_index(edges_df.index))
    edges_df['size'] = ((nodes_df.loc[edges_df['source']]['size'].reset_index(drop=True) + nodes_df.loc[edges_df['target']]['size'].reset_index(drop=True)) / 70).to_list()
    edges_df['color'] = disproportionate_normalize_series(edges_df['size'], 0.03, 0.5).apply(lambda x: f'rgba(7, 3, 0, {x})')

    graph['edges'] = edges_df.assign(attributes=edges_df.apply(combine_edge_attributes, axis=1)).drop(['weight', 'size', 'color'], axis=1).reset_index(names='key').to_dict(orient='records')
    
    sized_graph_output_path = graph_file_path.replace('_color_g.json', '_color_size_g.json')
    with open(sized_graph_output_path, 'w') as colored_graph_file:
        json.dump(graph, colored_graph_file)

    print(f'Saved sized graph file to "{sized_graph_output_path}"')

