import os
import pickle

from qutip import Qobj


def qu_load(name: str) -> Qobj:
    try:
        with open(os.path.join('input', name + '.qu'), 'rb') as f:
            bytes = f.read()

        return pickle.loads(bytes, encoding='latin1')
    except:
        return qu_load_with_fix(name)


def qu_load_with_fix(name: str) -> Qobj:
    """
    Load .qu from input folder.
    Sometimes \r\n is used in .qu files that causes errors when loading. We replace \r\n to \n to resolve this issue.
    """

    with open(os.path.join('input', name + '.qu'), 'rb') as f:
        bytes = f.read()
        bytes = bytes.replace(b'\r\n', b'\n')

    return pickle.loads(bytes, encoding='latin1')


def qu_save(name: str, obj: Qobj):
    with open(os.path.join('output', name + '.qu'), 'wb') as f:
        pickle.dump(obj, f)
