import pandas as pd, os
from corpus import get_script_path

def main():
    folderpath = get_script_path() + '\\hashtags\\'
    for filename in os.listdir(folderpath):
        file_path = os.path.join(folderpath, filename)
        if os.path.isfile(file_path) and filename.endswith('_classificado.xlsx'):
            tags_classificado = pd.read_excel(file_path, index_col=0)
            tags_teste = pd.read_csv(file_path.replace('_classificado.xlsx', '.csv'), index_col=0)
            tags_teste = tags_teste.loc[tags_teste.index.difference(tags_classificado.index)]
            tags_teste = pd.concat([tags_teste.iloc[:99], tags_teste[tags_teste['hashtags.1'] >= 20].sample(400, random_state=51)])
            test_sample_file = file_path.replace('_classificado.xlsx', '_teste.csv')
            tags_teste.reset_index().to_csv(test_sample_file, columns=['hashtags'], index=False)
            print(f'Saved test sample to {test_sample_file}')

if __name__ == "__main__":
    main()