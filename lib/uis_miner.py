"""
UIS Miner - Unit Implication System Miner
Very naive algorithm exploiting the arrow relation between objects and attributes
Based on the algorithm of [1]

References:
[1] Ryssel et al. - Fast algorithms for implication bases and attribute
exploration using proper premises
[2] Gainer-Dewar et al. The minimal hitting set generation problem: algorithms and computation

g \downarrow m \iff (g,m) \notin I and \forall h \in G and g' \subset h' then (h,m) \in I

This algorithm uses an also naive hitting set enumerator algorithm created for this project
"""
from time import time
import sys
from itertools import chain, product
from lib.minimum_hitting_set import berges_mhs



def read_db(path):
    """
    Read Database into a context
    path: str path to a csv 
    return list of lists of attirubtes
    """
    ctx = []
    with open(path, 'r') as fin:
        for line in fin:
            ctx.append(set(line.replace('\n', '').split()))
    return ctx


def g_downarrow_m(m, ctx):
    """
    Calculates objects in arrow relation with attribute m
    QUITE IMPROVABLE, SINCE IT DOES IT FOR EACH SINGLE ATTRIBUTE IT CALCULATES
    SEVERAL REDUNDANT INTERSECTIONS

    m: attribute
    ctx: list of lists of attributes
    return generator of objects
    """
    gnot = [g for g, gprime in enumerate(ctx) if m not in gprime]
    for g in gnot:
        gprime = ctx[g]
        is_good = True
        for h, hprime in enumerate(ctx):
            if hprime != gprime and gprime.issubset(hprime) and m not in hprime:
                is_good = False
                break
        if is_good:
            yield g

def all_g_downarrow_m(ctx, M):
    """
    Calculates objects in arrow relation with attribute m

    m: attribute
    ctx: list of lists of attributes
    return generator of objects
    """
    mdarrowd = {}
    count_subsets = 0
    for g, gprime in enumerate(ctx):
        # print g,
        candidates = [m for m in M if m not in gprime]
        # print candidates
        for h, hprime in enumerate(ctx):
            count_subsets+=1
            if len(gprime) < len(hprime) and gprime.issubset(hprime):
                # print '\t->', h
                for i in range(len(candidates)-1, -1, -1):
                    # print '\t\t->', candidates[i]
                    if candidates[i] not in hprime:
                        del candidates[i]
            if not bool(candidates):
                break
        # gdarrowm[g] = candidates
        map (lambda c: mdarrowd.setdefault(c, set([])).add(g), candidates)
    #print "COUNT SUBSETS", count_subsets
    return mdarrowd

def find_uis(ctx):
    """
    based on algorithm 1 of [1]
    Prints rules and number of them
    ctx: list of lists of attributes
    return void
    """
    M = set(chain(*ctx))
    # print (all_g_downarrow_m(ctx, M))
    # exit()

    premises = {}


    # FOR EACH ATTRIBUTE WE MINE FOR PROPER PREMISES
    for m, res in all_g_downarrow_m(ctx, M).items():
        
        # Obtain the attribute in arrow relation with m
        # res = g_downarrow_m(m, ctx)
        # Build the hypergraph
        # print '\r.',
        # sys.stdout.flush()
        transversal = [M - ctx[g] - set([m]) for g in res]
        # print '.',
        # sys.stdout.flush()
        # Calculate the hitting set which is actually the hypergraph transversal
        # Each element of the hypergraph transversal is a proper premise of m
        # print ',',
        if not bool(transversal):
            continue
        # print transversal
        hypergraph = berges_mhs(transversal)
        # print 'BERG',hypergraph,'\n\n', my_mhs(transversal)
        
        # hypergraph = list(my_mhs(transversal))
        # print ',',
        # sys.stdout.flush()
        for premise in hypergraph:
            # premises.setdefault(tuple(premise), set([])).add(m)
            if bool(premise):
                yield (premise, m)

def print_premises(premise_iterator):
    """
    Print premises in a nice way
    """
    alpha = lambda s: ''.join(tuple(sorted([chr(65+int(i)) for i in s]))).lower()# lambda x: chr(67+x)+','
    # i = 0
    rules = []
    for premise, consequence in premise_iterator: #sorted(premises.items(), key=lambda s: sorted((len(s[0]),s[0]))):
        rules.append('{} -> {}'.format(alpha(premise), alpha([consequence])).strip())
    #for rule in sorted(rules, key=lambda s: (len(s), s)):
    #    print(rule)
    print '\t=>',len(rules), 'rules found'

def main():
    print_premises(find_uis(read_db(sys.argv[1])))

if __name__ == "__main__":
    main()



##############################
# DEPRECATED##################
##############################
# def count_without(end, without):
#     i = 0
#     j = 0
#     while i < len(without):
#         for k in range(j, without[i]):
#             yield k
#         j = without[i]+1
#         i += 1
#     for k in range(j, end):
#         yield k

# def all_g_downarrow_m_v2(ctx, M):
#     """
#     Calculates objects in arrow relation with attribute m

#     m: attribute
#     ctx: list of lists of attributes
#     return generator of objects
#     """
#     mdarrowd = {}

#     ctx_inv = {m:[] for m in M}
#     ban_objs = {}
#     ban = set([])
#     for g, gprime in enumerate(ctx):
#         ban_objs[g] = set([])
#         for m in gprime:
#             ctx_inv[m].append(g)
#     count_subsets = 0
    
#     for g, gprime in enumerate(ctx):
#         # print g,

#         candidates = [m for m in M if m not in gprime]
        
#         ban.clear()
#         # print candidates
#         # paired = []
#         for m in candidates:
#             if m in ban:
#                 # print 'missed'
#                 continue
#             add = True

#             # def no_m(m):
#             #     for u, uprime in enumerate(ctx):
#             #         if m not in uprime:
#             #             yield u
#             for h in count_without(len(ctx), sorted(ban_objs[g].union(ctx_inv[m]))):# [i for i in range(len(ctx)) if i not in ctx_inv[m]]:
                
#                 # if (h,m) in paired:
#                 # if any(i==h for i,j in paired):
#                 #     print m, g, gprime, h, hprime, len(gprime) != len(hprime)
#                 #     print candidates
#                 #     print ban
#                 #     print paired
#                 #     exit()
#                 # paired.append((h,m))
#                 hprime = ctx[h]
#                 count_subsets += 1
#                 if gprime.issubset(hprime) and len(gprime) != len(hprime) :
#                     # WE HAVE AN OPENING, LET'S USE IT
#                     # print '\t->', g,h
#                     ban.update( set(candidates)-hprime)
#                     add=False
#                     if h > g:
#                         ban_objs[h].add(g)
#                     break
#                 else:
#                     ban_objs[g].add(h)
#                     if h > g and len(gprime) <= len(hprime):
#                         ban_objs[h].add(g)
#             if add:
#                 mdarrowd.setdefault(m, set([])).add(g)
#         del ban_objs[g]
        
#     print "COUNT SUBSETS", count_subsets
#     return mdarrowd
