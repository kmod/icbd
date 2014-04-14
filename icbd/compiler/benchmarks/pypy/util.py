import os.path

root = os.path.abspath(os.path.join(__file__, '..', '..'))
util_py = os.path.join(root, 'unladen_swallow', 'performance', 'util.py')
execfile(util_py)
