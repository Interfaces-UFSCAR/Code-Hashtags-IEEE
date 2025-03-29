from corpus import ensure_path_exists
from serialization import from_indexed_sparse, s_graph_from_adj_mat, ig_to_json
from argparse import ArgumentParser

def main():   
    parser = ArgumentParser(
      description="A script to serialize the cooccurence matrix pertaining to each runnoff candidate to a json format which can be easily rendered by most graph rendering software"
    )
    parser.add_argument(
      "--candidate",
      nargs=2,
      action="append",
      type=str,
      metavar=("input_path", "output_path"), 
      help="The input cooccurence matrix file path (npz) followed by the output file path (json)"
    )
    args = parser.parse_args()
    for [input_file_name, output_file_name] in args.candidate:
      with open(input_file_name, 'rb') as smat_file:
          cooc_mat, index, _ = from_indexed_sparse(smat_file)
          graph = s_graph_from_adj_mat(cooc_mat, index.tolist())
          ensure_path_exists(output_file_name)
          ig_to_json(graph, output_file_name)
          print(f'Saved serialized graph file to "{output_file_name}"')

if __name__ == "__main__":
    main()
    