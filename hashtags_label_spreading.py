import pandas as pd
from graphlearning.ssl import laplace
from serialization import from_indexed_sparse, df_to_json
from argparse import ArgumentParser
from corpus import ensure_path_exists

def main():
    parser = ArgumentParser(
      description="A script to perform a label spreading algorithm based on cooccurrence matrices and prelabeled hashtags of each runnoff candidate"
    )
    parser.add_argument(
      "--candidate",
      nargs=4,
      action="append",
      type=str,
      metavar=("matrix", "prelabeled", "csv_output", "json_output"), 
      help="A quadruple of file paths, the matrix file (npz) path followed by the prelabeled hashtags file path (xlsx), for a candidate, ended with the output paths for the labeling process (csv and json variants, respectively)"
    )
    args = parser.parse_args()
    for [matrix_file_name, prelabeled_file_name, csv_output, json_output] in args.candidate:
        try:
            with open(matrix_file_name, 'rb') as smat_buffer:
                s_cooc_mat, index, _ = from_indexed_sparse(smat_buffer)
            cat_df = pd.read_excel(prelabeled_file_name, index_col=0)
            cat_df = cat_df[cat_df['categoria']!='Remover']
            print(f'Starting classification process with data from files: "{matrix_file_name}", "{prelabeled_file_name}"')
            model = laplace(s_cooc_mat)
            present_tags = index.intersection(cat_df.index)
            if len(cat_df['categoria'].unique()) > 2:
                apoio_map = {'Pró-Lula':2, 'Pró-Bolsonaro':2, 'Indefinido':1, 
                            'Indefinido*':1, 'Anti-Lula':0, 'Anti-Bolsonaro':0}
                reverse_apoio_map = {0:'anti', 1:'indef', 2:'pro'}
            else:
                apoio_map = {'Pró-Lula':1, 'Pró-Bolsonaro':1, 
                            'Anti-Lula':0, 'Anti-Bolsonaro':0}
                reverse_apoio_map = {0:'anti', 1:'pro'}
            prob = model.fit(index.get_indexer(present_tags),
                            cat_df.loc[present_tags]['categoria']\
                                .map(apoio_map).dropna()
                            )
            prob_df = pd.DataFrame(prob, columns=list(reverse_apoio_map.values()), index=index)
            del s_cooc_mat, cat_df
            classified = prob_df.any(axis=1)
            prob_df['categoria'] = model.predict()
            prob_df['categoria'] = prob_df['categoria'].map(reverse_apoio_map)
            print(f'Classification done for file {matrix_file_name}, with the following results: ')
            print(f'Classified {(classified.sum() / len(prob_df)):.0%} of datapoints')
            prob_df = prob_df.loc[classified]
            print(f'Classification distribution of the {len(prob_df)} datapoints: ')
            print(prob_df['categoria'].value_counts(normalize=True).apply(lambda x:f'{x:.0%}'))
            ensure_path_exists(csv_output)
            prob_df.to_csv(csv_output)
            ensure_path_exists(json_output)
            cat_json = df_to_json(prob_df[['categoria']])
            with open(json_output, mode='w') as json_file:
                print(cat_json.getvalue(), file=json_file)

        except Exception as e:
            print(f'The following exception occurred while processing data from the following files: "{matrix_file_name}", "{prelabeled_file_name}"')
            raise e

if __name__ == "__main__":
    main()