import os, sys
from collections.abc import Iterable
from pathlib import Path

def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0])) + '\\'

def ensure_path_exists(path_str):
    path = Path(path_str)

    if path_str.endswith(os.sep) or path_str.endswith("/"):
        path.mkdir(parents=True, exist_ok=True)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)

def resolve_hierarchical_path(path, starting_path_vec=[]):
    paths = []
    for key, value in path.items():
        if isinstance(value, dict):
            paths+=resolve_hierarchical_path(value, starting_path_vec+[key])
        else:
            if not isinstance(value, list):
                value = [value]
            for subpath in value:
                paths.append('\\'.join(starting_path_vec+[key, subpath])+'\\')

    return paths

def map_agregator(init_func, agg_func): 
    collected = init_func()
    while True:
        file_path = yield
        collected = agg_func(collected, file_path)
        yield collected

def aggregate_from_corpus(corpus_folder_roots, init_func, agg_func, filter_func=lambda _ : True):
    if isinstance(corpus_folder_roots, str) or not isinstance(corpus_folder_roots, Iterable):
        folders_to_check = [corpus_folder_roots]
    else:
        folders_to_check = corpus_folder_roots

    folders_checked = 0
    agregator = map_agregator(init_func, agg_func)
    result = None
    with open("collection_log.txt", 'w') as log:
        while folders_checked < len(folders_to_check):
            folderpath = folders_to_check[folders_checked]
            if isinstance(folderpath, dict):
                folderpath = resolve_hierarchical_path(folderpath)
                if len(folderpath) > 1:
                    folders_to_check+=folderpath[1:]
                folderpath = folderpath[0]

            if not os.path.isdir(folderpath):
                folderpath = get_script_path()+folderpath
            for filename in os.listdir(folderpath):
                file_path = os.path.join(folderpath, filename)
                if not os.path.isfile(file_path):
                    folders_to_check.append(file_path)
                else:
                    if filter_func(file_path):
                        next(agregator)
                        result = agregator.send(file_path)
                        log.write(f'Collected from: {file_path}\n')
                        print(f'Collected from: {file_path}')
                        
            folders_checked+=1

    return result

