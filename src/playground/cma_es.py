import cma
import sys

def s(d):
    return sum(d)

def noop(*args, **kwargs):
    pass

es = cma.CMAEvolutionStrategy([0] * 8, 0.5, {'verbose': -5, 'verb_log': 0, 'verb_plot': 0})
es.disp_annotation = noop
es.disp = noop
q = es.optimize(s, iterations=100)
print(es.result.xbest)
