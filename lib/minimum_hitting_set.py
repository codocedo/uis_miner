import sys
from itertools import chain, product

def next_to_remove(sets, new_sets, start=None):
    
    all_keys = sorted(reduce(set.union, sets))
    # print '**', start, all_keys,
    # if start is not None:
    #     all_keys = [k for k in all_keys if k >= start]
    # print all_keys, [k >= start for k in all_keys], type(start), start
    for m in all_keys:
        del new_sets[:]
        is_next = True
        for s in sets:
            new_sets.append(s-set([m]))
            if not bool(new_sets[-1]):
                is_next = False
                break
        if is_next:
            yield m
    yield None

def my_mhs(sets, mhs=None, start=None, depth=0):
    if mhs is None:
        mhs = set(chain(*sets))
        # print '==>',mhs
    # print '\t'*depth,'=>',sets,'::', mhs
    if all([len(s) == 1 for s in sets]):
        yield mhs
    else:
        new_sets = []
        iterator = next_to_remove(sets, new_sets, start)
        m = iterator.next()
        if m is None:
            yield mhs
        while m is not None and m < start:
            m = iterator.next()
        while m is not None:
            # print '\t'*depth,'\t->', m
            new_mhs = mhs-set([m])
            # new_sets = [s.intersection(new_mhs) for s in sets]
            for s in my_mhs(new_sets, new_mhs, m, depth+1):
                yield s
            m = iterator.next()


def berges_mhs(sets):
    """
    Berge's algorithm for minimal hitting set enumeration
    As described in [2]
    sets: list of sets
    return list of sets
    """
    T = [set([i]) for i in sets[0]]
    for s in sets[1:]:
        T = sorted([i.union([j]) for i,j in product(T, s)], key=len)
        todel = []
        for i in range(len(T)-1, 0, -1):
            for j in range(i-1 , -1, -1):
                if T[j].issubset(T[i]):
                    del T[i]
                    break
    return T


if __name__ == "__main__":
    sets = map(set, sys.argv[1:])
    # sets = map(set, [[1], [1,2], [3,4]])
    for s in my_mhs(sets):
        print '->',sorted(s)

        
