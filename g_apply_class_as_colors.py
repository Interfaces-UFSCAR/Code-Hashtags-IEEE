import os, json, pandas as pd
from corpus import get_script_path

def main():
    folderpath = get_script_path() + '\\hashtags\\'

    for filename in os.listdir(folderpath):
        file_path = os.path.join(folderpath, filename)
        if os.path.isfile(file_path) and filename.endswith('_g.json') and not filename.endswith('_color_g.json') and not filename.endswith('_size_g.json'):
            with open(file_path) as graph_file:
                graph = json.load(graph_file)
                try:
                    node_cats = pd.read_json(f'hashtags\\label_spreading\\hashtags_{filename.split("hashtags_", 1)[1].rsplit("_coocc_g.json", 1)[0]}_classificado_ls_cat.json', 
                                    orient='index')
                except FileNotFoundError:
                    node_cats = pd.read_json(f'hashtags\\label_spreading\\hashtags_{filename.split("hashtags_", 1)[1].rsplit("_scaled_coocc_g.json", 1)[0]}_classificado_ls_cat.json', 
                                    orient='index')

            for node in graph['nodes']:
                try:
                    cat = node_cats.loc[node['attributes']['label']]['categoria']
                except KeyError as e:
                    cat = None

                if cat == 'indef':
                    node['attributes']['color'] = 'rgb(170,170,170)'
                elif cat == 'anti':
                    node['attributes']['color'] = 'rgb(185, 13, 220)'
                elif cat == 'pro':
                    node['attributes']['color'] = 'rgb(44, 70, 149)'

            colorized_graph_output_path = file_path.replace('_g.json', '_color_g.json')
            with open(colorized_graph_output_path, 'w') as colored_graph_file:
                json.dump(graph, colored_graph_file)

            print(f'Saved colorized graph file to "{colorized_graph_output_path}"')

if __name__ == "__main__":
    main()