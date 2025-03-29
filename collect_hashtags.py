from corpus import aggregate_from_corpus, get_script_path, ensure_path_exists
import pandas as pd, numpy as np
from scipy.sparse import csr_matrix, triu, tril
from scipy.sparse.csgraph import connected_components
from serialization import to_indexed_sparse
from argparse import ArgumentParser
from os.path import join

def collect_tags(path):
    new_hashtags = pd.read_parquet(path, columns=['id', 'hashtags'])
    return new_hashtags[new_hashtags['hashtags'].notnull()]

def generate_co_occurrence_matrix(hashtags_with_groupid, prelabeled_hashtags_file_path=None):
    #prelabeled_hashtags_file will be used to prevent hashtags with category=='Remove' from being part of the co-occurrence matrix

    coocc_mat=hashtags_with_groupid.explode('hashtags')
    coocc_mat=coocc_mat[coocc_mat['hashtags'].str.len()>1].reset_index()

    if prelabeled_hashtags_file_path:
        try:
            with open(prelabeled_hashtags_file_path) as f:
                removal_hashtags = pd.read_excel(prelabeled_hashtags_file_path, index_col=0)['categoria']
                removal_hashtags = removal_hashtags[removal_hashtags=='Remover']
                coocc_mat = coocc_mat[~(coocc_mat['hashtags'].isin(removal_hashtags.index))]
                print(f'Cooc Matrix: Removed {len(removal_hashtags)} hashtags based on the file: {prelabeled_hashtags_file_path}')
        except FileNotFoundError:
            print(f'Cooc Matrix: No prelabeled hashtags file found: Skipping hashtag removal step.')

    i, r = pd.factorize(coocc_mat['hashtags'])
    j, _ = pd.factorize(coocc_mat['index'])

    ij, tups = pd.factorize(list(zip(i, j)))
    coocc_mat = csr_matrix((np.bincount(ij), tuple(zip(*tups))))
    print('Starting matrix operations.')
    coocc_mat = coocc_mat.dot(coocc_mat.transpose())
    coocc_mat[:] = triu(coocc_mat, 1) + tril(coocc_mat, -1)

    _, labels = connected_components(csgraph=coocc_mat, directed=False, return_labels=True)

    largest_component_label = np.argmax(np.bincount(labels))
    node_indices = np.where(labels == largest_component_label)[0]

    # Create the subgraph of the largest connected component
    coocc_mat = coocc_mat[node_indices, :][:, node_indices]
    r = r[node_indices]

    print(f'Done with matrix operations. Generated matrix of size {len(r)}')
    return coocc_mat, r

def collect_hashtags(sub_corpus, hashtags_file_name, prelabeled_file_name, coocc_file_name):
    collected_tags = aggregate_from_corpus(sub_corpus, 
                                    init_func=lambda : [], 
                                    agg_func=lambda collected, file_path: collected+[collect_tags(file_path)], 
                                    filter_func=lambda file_path : file_path.split('\\')[-1].startswith('tweets') and ((not 'retweets' in file_path) or '_fixed' in file_path))
    collected_tags = pd.concat(collected_tags)
    collected_tags.drop_duplicates('id', inplace=True)
    collected_tags.drop('id', axis=1, inplace=True)
    collected_tags['hashtags'] = collected_tags['hashtags'].str.casefold().str.normalize('NFKD')\
        .str.encode('ascii', errors='ignore').str.decode('utf-8').str.split(', ')
    
    frequency_df = collected_tags.explode('hashtags')
    ensure_path_exists(hashtags_file_name)
    frequency_df[frequency_df['hashtags'].str.len()>1].groupby('hashtags')['hashtags']\
        .count().sort_values(ascending=False).to_csv(hashtags_file_name)
    del frequency_df
    print(f'Saved hashtag frequency data to "{hashtags_file_name}"')
    collected_tags=collected_tags[collected_tags['hashtags'].str.len() > 1].reset_index(drop=True)
    coocc_mat, coocc_mat_index = generate_co_occurrence_matrix(collected_tags, prelabeled_file_name)
    ensure_path_exists(coocc_file_name)
    s_coocc_mat = to_indexed_sparse(coocc_mat, coocc_mat_index, coocc_mat_index)
    with open(coocc_file_name, mode='wb') as isparse_file:
        isparse_file.write(s_coocc_mat.getbuffer())
    print(f'Saved hashtag co-occurrence data to "{coocc_file_name}"')

def main():
    parser = ArgumentParser(
      description="A script to collect the hashtags from the runnoffs substet and build a hashtag cooccurrence matrix for each candidate"
    )
    parser.add_argument(
      "corpus_path",
      type=str,
      help="Path to the root folder of the corpus (ITED-br)"
    )
    parser.add_argument(
      "lula_hashtags_output",
      type=str,
      help="Output file path for the lula hashtags (csv)"
    )
    parser.add_argument(
      "bolsonaro_hashtags_output",
      type=str,
      help="Output file path for the bolsonaro hashtags (csv)"
    )
    parser.add_argument(
      "lula_prelabeled",
      type=str,
      help="Input file path for the prelabeled lula hashtags (xlsx)"
    )
    parser.add_argument(
      "bolsonaro_prelabeled",
      type=str,
      help="Input file path for the prelabeled bolsonaro hashtags (xlsx)"
    )
    parser.add_argument(
      "lula_matrix_output",
      type=str,
      help="Output file path for the lula matrix (npz)"
    )
    parser.add_argument(
      "bolsonaro_matrix_output",
      type=str,
      help="Output file path for the bolsonaro matrix (npz)"
    )
    args = parser.parse_args()

    target_folders_lula = []
    target_folders_bolsonaro = []
    corpus = args.corpus_path
    for i in range(3, 31):
        target_folders_lula.append(join(corpus, 'retweets_query_lula\\2022\\10\\{i:02d}\\'))
        target_folders_lula.append(join(corpus, 'query_lula\\2022\\10\\{i:02d}\\'))
        target_folders_bolsonaro.append(corpus, join('retweets_query_bolsonaro\\2022\\10\\{i:02d}\\'))
        target_folders_bolsonaro.append(corpus, join('query_bolsonaro\\2022\\10\\{i:02d}\\'))

    base_path = get_script_path()
    collect_hashtags(
        target_folders_lula, 
        join(base_path, args.lula_hashtags_output), 
        args.lula_prelabeled, 
        join(base_path, args.lula_matrix_output)
    )
    collect_hashtags(
        target_folders_bolsonaro, 
        join(base_path, args.bolsonaro_hashtags_output), 
        args.bolsonaro_prelabeled, 
        join(base_path, args.bolsonaro_matrix_output)
    )

if __name__ == "__main__":
    main()