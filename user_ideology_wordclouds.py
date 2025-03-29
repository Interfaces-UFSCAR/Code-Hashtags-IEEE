import pandas as pd, matplotlib.pyplot as plt, os
from wordcloud import WordCloud
from corpus import get_script_path, ensure_path_exists
from argparse import ArgumentParser

def remove_prelabeled(classification_df, prelabeled_hashtags_file_name):
    return classification_df.loc[classification_df.index.difference(pd.read_excel(prelabeled_hashtags_file_name, index_col=0).index)]

def make_wordcloud(series, candidate, category, output_file_name):
    wc = WordCloud(width=800, height=400, background_color='white')
    wordcloud = wc.generate_from_frequencies(series)

    plt.figure(figsize=(10, 5))
    plt.title(f'Ideologia {category}: {candidate.capitalize()}')
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')

    path = os.path.join(get_script_path(), output_file_name)
    ensure_path_exists(path)
    plt.savefig(path)
    print(f'Saved wordcloud to: {path}')

def main():
  parser = ArgumentParser(
    description="A script to produce wordclouds representing the presence and classification of the hashtags in the studied corpus subset"
  )
  parser.add_argument(
    "lula_labels",
    type=str,
    help="The labeled hashtags file path regarding the candidate lula (csv)"
  )
  parser.add_argument(
    "bolsonaro_labels",
    type=str,
    help="The labeled hashtags file path regarding the candidate bolsonaro (csv)"
  )
  parser.add_argument(
    "lula_frequency",
    type=str,
    help="The hashtag frequency file path regarding the candidate lula (csv)"
  )
  parser.add_argument(
    "bolsonaro_frequency",
    type=str,
    help="The hashtag frequency file path regarding the candidate bolsonaro (csv)"
  )
  parser.add_argument(
    "lula_outputs",
    nargs=3, 
    metavar=("lula_anti_cloud", "lula_pro_cloud", "lula_indef_cloud"), 
    type=str,
    help="The output paths for the 'pro', 'anti' and 'indef' lula hashtags wordclouds (3 files, all png)"
  )
  parser.add_argument(
    "bolsonaro_outputs",
    nargs=3, 
    metavar=("bolsonaro_anti_cloud", "bolsonaro_pro_cloud", "bolsonaro_indef_cloud"), 
    type=str,
    help="The output paths for the 'pro', 'anti' and 'indef' bolsonaro hashtags wordclouds (3 files, all png)"
  )
  parser.add_argument(
    "--remove_prelabeled",
    nargs=2, 
    type=str,
    metavar=("lula_prelabeled", "bolsonaro_prelabeled"), 
    default=None,
    help="Optional paths to the prelabeled hashtags file for each candidate (2 files, both xlsx). Use if you wish for the resulting clouds to not include the prelabeled hashtags."
  )
  args = parser.parse_args()

  for i, candidate in enumerate(['lula', 'bolsonaro']):
      df = remove_prelabeled(pd.read_csv(args[f'{candidate}_labels'], index_col=0), args.remove_prelabeled[i]) if args.remove_prelabeled else pd.read_csv(args[f'{candidate}_labels'], index_col=0)
      df['frequency'] = df.index.map(pd.read_csv(args[f'{candidate}_frequency'], index_col=0)['hashtags.1'])
      for j, category in enumerate(['anti', 'pro', 'indef']):
          make_wordcloud(df[category]*df['frequency'], candidate, category, args[f'{candidate}_outputs'][j])

if __name__ == "__main__":
    main()