#Possivelmente obsoleto pois algoritmos de layout de grafico já aplicam este tipo de normalização

from serialization import from_indexed_sparse, to_indexed_sparse
from scipy.sparse import csr_matrix
import os, numpy as np

def log_scale_weights(adjacency_matrix, base=np.e):
    # Ensure all weights are positive by adding a small constant (epsilon)
    adjacency_matrix = adjacency_matrix.toarray().astype(float)
    zero_weight_index = (adjacency_matrix==0)
    epsilon = 1e-9
    adjacency_matrix+=epsilon
    
    # Apply log scaling
    log_scaled_matrix = np.log(adjacency_matrix) / np.log(base)
    log_scaled_matrix[zero_weight_index] = 0
    
    return csr_matrix(log_scaled_matrix)

def main():   
    cooc_files_folder = 'hashtags\\'
    for filename in os.listdir(cooc_files_folder):
        file_path = os.path.join(cooc_files_folder, filename)
        if os.path.isfile(file_path) and filename.endswith('_coocc.npz') and not filename.endswith('_scaled_coocc.npz'):#data generated by collect_hashtags.py and processed by
            # remove_indef_from_cooc_matrix.py (also non-processed versions)
            with open(file_path, 'rb') as smat_file:
                cooc_mat, index, _ = from_indexed_sparse(smat_file)

            scaled_coocc_mat = to_indexed_sparse(log_scale_weights(cooc_mat), index, index)
            scaled_matrix_path = file_path.replace('_coocc.npz', '_scaled_coocc.npz')
            with open(scaled_matrix_path, mode='wb') as isparse_file:
                isparse_file.write(scaled_coocc_mat.getbuffer())

            print(f'Wrote scaled matrix data to {scaled_matrix_path}')

if __name__ == "__main__":
    main()