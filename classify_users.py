from corpus import aggregate_from_corpus, get_script_path
import pandas as pd

def collect_tags(path):
    new_hashtags = pd.read_parquet(path, columns=['hashtags', 'author_id', 'id'])
    return new_hashtags[new_hashtags['hashtags'].notnull()]

def classify_users_by_hashtags(sub_corpus, input_classification_file_name, output_classification_file_name):
    collected_tags = aggregate_from_corpus(sub_corpus, 
                                    init_func=lambda : [], 
                                    agg_func=lambda collected, file_path: collected+[collect_tags(file_path)], 
                                    filter_func=lambda file_path : file_path.split('\\')[-1].startswith('tweets') and ((not 'retweets' in file_path) or '_fixed' in file_path))
    collected_tags = pd.concat(collected_tags)

    tweet_counts = collected_tags.drop_duplicates('id')['author_id'].value_counts()
    collected_tags = collected_tags.set_index('author_id').loc[tweet_counts>=10].drop('id', axis=1).reset_index(names='author_id')
    
    collected_tags['hashtags'] = collected_tags['hashtags'].str.casefold().str.normalize('NFKD')\
        .str.encode('ascii', errors='ignore').str.decode('utf-8').str.split(', ')
    collected_tags = collected_tags.explode('hashtags').groupby('author_id')['hashtags'].value_counts().reset_index()

    classification = pd.read_csv(input_classification_file_name, index_col=0, usecols=[0, 4])
    classification['categoria'] = classification['categoria'].map({'pro' : 1, 'anti' : -1, 'indef' : 0})
    collected_tags['categoria'] = collected_tags['hashtags'].map(classification['categoria'])
    print(f'Ignoring {(collected_tags['categoria'].isna()*collected_tags['count']).sum()} instances of unrecognized hashtags')
    collected_tags.dropna(subset=['categoria'], inplace=True)
    collected_tags['weight'] = collected_tags['count']*collected_tags['categoria']
    collected_tags.drop('categoria', axis=1, inplace=True)
    collected_tags=(collected_tags[['author_id', 'weight']].groupby('author_id').sum()['weight']/collected_tags[['author_id', 'count']].groupby('author_id').sum()['count'])

    pd.concat({'ideology_score': collected_tags, 'tweet_count': tweet_counts}, axis=1, join='inner').to_csv(output_classification_file_name)
    print(f'Saved user classification data to "{output_classification_file_name}"')

def main():
    target_folders_lula = []
    target_folders_bolsonaro = []
    for i in range(3, 31):
        target_folders_lula.append(f'corpus\\query_lula\\2022\\10\\{i:02d}\\')
        #target_folders_lula.append(f'corpus\\retweets_query_lula\\2022\\10\\{i:02d}\\')
        target_folders_bolsonaro.append(f'corpus\\query_bolsonaro\\2022\\10\\{i:02d}\\')
        #target_folders_bolsonaro.append(f'corpus\\retweets_query_bolsonaro\\2022\\10\\{i:02d}\\')

    base_path = get_script_path()
    classify_users_by_hashtags(target_folders_lula, base_path+'hashtags\\label_spreading\\hashtags_lula_classificado_ls.csv', 
                        base_path+'\\usuarios\\usuarios_classificados\\usuarios_lula_classificados.csv')
    classify_users_by_hashtags(target_folders_bolsonaro, base_path+'hashtags\\label_spreading\\hashtags_bolsonaro_classificado_ls.csv', 
                        base_path+'\\usuarios\\usuarios_classificados\\usuarios_bolsonaro_classificados.csv')

if __name__ == "__main__":
    main()