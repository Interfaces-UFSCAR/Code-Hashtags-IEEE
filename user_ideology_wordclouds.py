import pandas as pd, matplotlib.pyplot as plt, os
from wordcloud import WordCloud
from corpus import get_script_path

def get_hashtag_frequency_df(candidate):
    file = f'hashtags_{candidate}.csv'
    path = os.path.join(get_script_path(), 'hashtags', file)
    return pd.read_csv(path, index_col=0)

def get_prelabeled_classification_df(candidate):
    file = f'hashtags_{candidate}_classificado.xlsx'
    path = os.path.join(get_script_path(), 'hashtags', file)
    return pd.read_excel(path, index_col=0)

def get_classification_df(candidate):
    file = f'hashtags_{candidate}_classificado_ls.csv'
    path = os.path.join(get_script_path(), 'hashtags', 'label_spreading', file)
    return pd.read_csv(path, index_col=0)

def remove_prelabeled(classification_df, candidate):
    return classification_df.loc[classification_df.index.difference(get_prelabeled_classification_df(candidate).index)]

def make_wordcloud(series, candidate, category):
    wc = WordCloud(width=800, height=400, background_color='white')
    wordcloud = wc.generate_from_frequencies(series)

    plt.figure(figsize=(10, 5))
    plt.title(f'Ideologia {category}: {candidate.capitalize()}')
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')

    file = f'ideology_{candidate}_{category}_wordcloud.png'
    path = os.path.join(get_script_path(), 'hashtags', 'label_spreading', file)
    plt.savefig(path)
    print(f'Saved wordcloud to: {path}')

remove_prelabeled_hashtags = False

for candidate in ['lula', 'bolsonaro']:
    df = remove_prelabeled(get_classification_df(candidate), candidate) if remove_prelabeled_hashtags else get_classification_df(candidate)
    df['frequency'] = df.index.map(get_hashtag_frequency_df(candidate)['hashtags.1'])
    for category in ['anti', 'pro', 'indef']:
        make_wordcloud(df[category]*df['frequency'], candidate, category)