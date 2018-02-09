import sys
from itertools import chain
# import numpy as np

from fca.io.transformers import List2PartitionsTransformer
from fca.io.file_models import FileModelFactory
from fca.defs.patterns.hypergraphs import TrimmedPartitionPattern as PartitionPattern
# from fca.defs.patterns.hypergraphs import PartitionPattern
from lib.minimum_hitting_set import berges_mhs as my_mhs


def read_csv(path):
    ctx = []
    with open(path, 'r') as fin:
        for line in fin:
            
            # ctx.append(map(int, line.replace('\n', '').split(',')))
            ctx.append(line.replace('\n', '').split(','))
    ctx = np.array(ctx)
    for i, row in enumerate(ctx.T):
        hashes = {}
        for j, value in enumerate(row):
            hashes.setdefault(value, set([])).add(j)
        yield hashes.values()
    

def read_db(path):
    ctx = []
    with open(path, 'r') as fin:
        for line in fin:
            ctx.append(set(line.replace('\n', '').split()))
    return ctx

def g_darrow_m(m, ctx):
    result = []
    for g, gprime in enumerate(ctx):
        if m not in gprime:
            insert = True
            for hi, h in enumerate(result):
                hprime = ctx[h]
                if hprime <= gprime:
                    result[hi] = g
                    insert = False
                    break
                elif gprime <= hprime:
                    insert = False
                    break
            if insert:
                result.append(g)
    return result

def d_darrow_m2(x, ctx, M):
    
    delta_x = ctx[x]
    # print '\t',M[x], delta_x
    result = []
    result2 = []
    for y, delta_y in enumerate(ctx):
        if y != x:
            # print '\t\t->', M[y], delta_y, PartitionPattern.leq(delta_y, delta_x)
            if not PartitionPattern.leq(delta_y, delta_x):
                add = True
                for z, delta_z in enumerate(ctx):
                    # print '\t\t\t',z
                    if z != y and z != x and z > y:
                        print '\t\t\t->', M[z], delta_z, PartitionPattern.intersection(delta_z, delta_y), PartitionPattern.leq(PartitionPattern.intersection(delta_z, delta_y), delta_x)
                        if not PartitionPattern.leq(PartitionPattern.intersection(delta_z, delta_y), delta_x):
                            result.append(PartitionPattern.intersection(delta_z, delta_y))
                            result2.append((y, z))
                            add = False
                            # break
                if add:
                    result.append(delta_y)
                    result2.append((y))
    print result2
    return result

def d_darrow_m(x, ctx, start=None, current_delta=None, depth=0):
    delta_x = ctx[x]
    # print '\t'*depth,'->', start
    # print '\t'*depth, 'DARROW=>', x, delta_x, "START:",start, "CURRENT DELTA:", current_delta
    # print '\t'*depth, 'DARROW=>', x, "START:",start, "CURRENT DELTA:"
    current_delta = PartitionPattern.top() if current_delta is None else current_delta
    # print current_delta
    start = 0 if start is None else start
    yield_this = True
    results = []
    for y, delta_y in enumerate(ctx):
        # print '\t'*depth, '\t-> Y:', y, delta_y, y != x , y >= start
        # print '\t'*depth, '\t-> Y:', y, y != x , y >= start
        if y != x and y >= start:
            # print current_delta, delta_y, PartitionPattern.intersection(current_delta, delta_y)
            delta = PartitionPattern.intersection(current_delta, delta_y)
            go_on = True
            for other_result in results:
                if PartitionPattern.leq(other_result, delta):
                    go_on=False
                    break
                    
            # print '\t'*depth, '\t\t-> DELTA', delta, '<=', delta_x, PartitionPattern.leq(delta, delta_x), "GO ON:", go_on
            # print '\t'*depth, '\t\t-> DELTA', '<=', PartitionPattern.leq(delta, delta_x), "GO ON:", go_on
            if not PartitionPattern.leq(delta, delta_x):
                for r in d_darrow_m(x, ctx, start=y+1, current_delta=delta, depth=depth+1):
                    if all(not PartitionPattern.leq(i, r) for i in results):
                        results.append(r)
                        # print results
                        yield r
                    # else:
                    #     print "Rejected"
                yield_this = False
                

    if yield_this:
        # print "******************************** YIELD", d_prime(current_delta, ctx) #, current_delta
        yield current_delta

def d_darrow_m_v2(x, ctx, start=None, current_delta=None, depth=0):
    delta_x = ctx[x]
    # print '\t'*depth,'->', start
    # print '\t'*depth, 'DARROW=>', x, delta_x, "START:",start, "CURRENT DELTA:", current_delta
    # print '\t'*depth, 'DARROW=>', x, "START:",start, "CURRENT DELTA:"
    # current_delta = PartitionPattern.top() if current_delta is None else current_delta
    # print current_delta
    # start = 0 if start is None else start
    yield_this = True
    results = []
    for y, delta_y in enumerate(ctx):
        # print '\t'*depth, '\t-> Y:', y, delta_y, y != x , y >= start
        # print '\t'*depth, '\t-> Y:', y, y != x , y >= start
        if y != x and y >= start:
            # print current_delta, delta_y, PartitionPattern.intersection(current_delta, delta_y)
            delta = PartitionPattern.intersection(current_delta, delta_y)
            go_on = True
            for other_result in results:
                if PartitionPattern.leq(other_result, delta):
                    go_on=False
                    break
                    
            # print '\t'*depth, '\t\t-> DELTA', delta, '<=', delta_x, PartitionPattern.leq(delta, delta_x), "GO ON:", go_on
            # print '\t'*depth, '\t\t-> DELTA', '<=', PartitionPattern.leq(delta, delta_x), "GO ON:", go_on
            if not PartitionPattern.leq(delta, delta_x):
                for r in d_darrow_m_v2(x, ctx, start=y+1, current_delta=delta, depth=depth+1):
                    if all(not PartitionPattern.leq(i, r) for i in results):
                        results.append(r)
                        # print results
                        yield r
                    # else:
                    #     print "Rejected"
                yield_this = False
                

    if yield_this:
        # print "******************************** YIELD", d_prime(current_delta, ctx) #, current_delta
        yield current_delta
                

            
def d_prime(delta, ctx):
    # print ''
    result = set([])
    for x, delta_x in enumerate(ctx):
        # print '\t=>', x, delta, delta_x, PartitionPattern.leq(delta, delta_x)
        if PartitionPattern.leq(delta, delta_x):
            result.add(x)
    return result
                    
            

if __name__ == "__main__":
    fmgr = FileModelFactory(sys.argv[1], style='tab').file_manager
    ctx = map(PartitionPattern.fix_desc, map(List2PartitionsTransformer(transposed=False).transform, fmgr.entries_transposed()))

    M = set(range(len(ctx)))
    all_elements = set([])
    map(all_elements.update, chain(*ctx))
    PartitionPattern.top([all_elements])
    # print PartitionPattern.top()
    premises = {}
    for i, m in enumerate(M):
        print '\n PRocessing', i, m
        res = d_darrow_m(i, ctx, start=0, current_delta=PartitionPattern.top())
        res = list(res)
        print 'RESULT:', len(res)
        # res2 = [d_prime(i, ctx) for i in res]

        transversal = [i for i in [M - d_prime(d, ctx) - set([m]) for d in res] if bool(i)]
        print 'RESULT:', 'x'
        # print "TRANSVERSAL:", transversal
        if not bool(transversal):
            continue
        
        
        if any([len(i) == 0 for i in transversal]):
            continue
        for premise in list(my_mhs(transversal)):
            premises.setdefault(tuple(premise), set([])).add(m)
    i = 0
    alpha = lambda s: ','.join(tuple([chr(65+i) for i in s])).lower()# lambda x: chr(67+x)+','
    for premise, consequences in premises.items():
        if not bool(premise):
            continue
        print '{} => {}'.format(alpha(premise), alpha(consequences))
        i+=len(consequences)
    print i, 'rules'
    print "END"
    # print M
    