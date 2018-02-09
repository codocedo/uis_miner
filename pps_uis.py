import sys
from itertools import chain

from fca.io.transformers import List2PartitionsTransformer
from fca.io.file_models import FileModelFactory
from fca.defs.patterns.hypergraphs import TrimmedPartitionPattern as PartitionPattern
from lib.minimum_hitting_set import berges_mhs as my_mhs

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
    