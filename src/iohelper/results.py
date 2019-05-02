import os
import pickle


def store(collection_name, name, result):
    cdir = get_collection_dir(collection_name)
    with open(os.path.join(cdir, name), 'wb') as f:
        pickle.dump(result, f)


def load(collection_name, file_name):
    cdir = get_collection_dir(collection_name)
    with open(os.path.join(cdir, file_name), 'rb') as f:
        return pickle.load(f)
    
    
def load_all(collection_name):
    cdir = get_collection_dir(collection_name)
    for f in os.listdir(cdir):
        yield load(collection_name, f)


def get_collection_dir(collection_name):
    dir_path = os.path.abspath(os.path.join('output', collection_name))
    os.makedirs(dir_path, exist_ok=True)
    return dir_path
