import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors


def create_plot(data: pd.DataFrame, title: str, path: str, candidate: str):

    fig = plt.figure(figsize=(10, 9))

    sns.set_theme(style="whitegrid")
    sns.set_color_codes("pastel")

    ax = sns.histplot(data, 
                    x= 'ideology_score', 
                    binwidth=.05)


    norm = mcolors.Normalize(vmin=-1, vmax=1)
    cmap = mcolors.LinearSegmentedColormap.from_list("meu_cmap", ["#B90DDC", "#AAAAAA", "#2C4695"])

    patches = ax.patches
    for p in patches:
        bin_center = p.get_x() + p.get_width() / 2  
        p.set_facecolor(cmap(norm(bin_center)))


    if patches: 
        primeiro = patches[0] 
        middle = patches[len(patches)//2]
        ultimo = patches[-1] 

        ax.text(primeiro.get_x() - 0.01,  
                50,  
                f"Against {candidate}",  
                ha='right',  
                va='bottom',  
                fontsize=24,  
                fontweight='bold',  
                color='#B90DDC', rotation= 90)

        ax.text(middle.get_x() + middle.get_width() - 0.02,  
                middle.get_height() + 150,
                "Neutral",  
                ha='center',  
                va='center',  
                fontsize=24,  
                fontweight='bold',  
                color='#AAAAAA')

        ax.text(ultimo.get_x() + ultimo.get_width() + 0.02,  
                50,  
                f"Pro {candidate}",  
                ha='left',  
                va='bottom',  
                fontsize=24,  
                fontweight='bold',  
                color='#2C4695', rotation= 90)


    plt.title(title,
            fontsize=24, 
            fontweight='bold')
    plt.ylabel('Frequency', 
            fontsize=24, 
            fontweight='bold')
    plt.xlabel('User Ideology Scores', 
            fontsize=24, 
            fontweight='bold')

    plt.tick_params(axis='x', labelsize=18)  
    plt.tick_params(axis='y', labelsize=18)
    plt.savefig(path, format='png')

def main():
    bolsonaro_scores = pd.read_csv('./usuarios_bolsonaro_classificados.csv')
    lula_scores = pd.read_csv('./usuarios_lula_classificados.csv')

    create_plot(title = 'Distribution of Users Ideology Score(Query Bolsonaro)',
                data = bolsonaro_scores,
                path = "./bolsonaro_users_scores.png",
                candidate = 'Bolsonaro')
    
    create_plot(title = 'Distribution of Users Ideology Score(Query Lula)', 
                data = lula_scores, 
                path = "./lula_users_scores.png", 
                candidate = 'Lula')
        
main()