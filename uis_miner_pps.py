import sys
import time

from itertools import chain

from fca.io.transformers import List2PartitionsTransformer
from fca.io.file_models import FileModelFactory
from fca.defs.patterns.hypergraphs import TrimmedPartitionPattern
from fca.algorithms.previous_closure import PSPreviousClosure
from lib.minimum_hitting_set import berges_mhs as my_mhs
from fca.io import read_representations
from fca.io.input_models import PatternStructureModel
from fca.io.sorters import PartitionSorter
import csv

from lib.uis_miner import find_uis, print_premises



class StrippedPartitions(TrimmedPartitionPattern):
    '''
    Same as stripped partitions buy with a much more clever intersection.
    Algorithm defined in
    [1] Huhtala - TANE: An Efficient Algoritm for Functional and Approximate Dependencies
    '''    
    @classmethod
    def intersection(cls, desc1, desc2):
        '''
        Procedure STRIPPED_PRODUCT defined in [1]
        '''
        new_desc = []
        T = {}
        S = {}
        for i, k in enumerate(desc1):
            for t in k:
                T[t] = i
            S[i] = set([])
        for i, k in enumerate(desc2):
            for t in k:
                if T.get(t, None) is not None:
                    S[T[t]].add(t)
            for t in k:
                if T.get(t, None) is not None:
                    if len(S[T[t]]) > 1:
                        new_desc.append(S[T[t]])
                    S[T[t]] = set([])
        return new_desc

if __name__ == "__main__":

    filepath = sys.argv[1]
    t0 = time.time()
    transposed = True

    fctx = PatternStructureModel(
        filepath=filepath,
        sorter=PartitionSorter(),
        transformer=List2PartitionsTransformer(transposed),
        transposed=transposed,
        file_manager_params={
            'style': 'tab'
        }
    )

    if fctx.sorter is not None:
        fctx.transformer.attribute_index = {i:j for i, j in enumerate(fctx.sorter.processing_order)}

    ondisk_poset = PSPreviousClosure(
        fctx,
        pattern=StrippedPartitions,
        ondisk=True,
        ondisk_kwargs={
            'output_path':'/tmp',
            'output_fname':None,
            'write_extent':False
        },
        silent=True
    ).poset

    ctx = []
    attribute_index = {}

    fout_name = ondisk_poset.close()
    with open(fout_name , 'r') as fin:
        reader = csv.reader(fin, delimiter='\t')
        headers = reader.next()
        for row in reader:
            lst = row[-1]
            lst = lst[lst.find('[')+1:lst.find(']')]
            representation = [attribute_index.get(int(i.strip()), int(i.strip())) for i in lst.split(',') if ',' in lst]
            ctx.append(set([int(i.strip()) for i in lst.split(',') if ',' in lst]))

    print_premises(find_uis(ctx))
    print ("\t=> Execution Time: {} seconds".format(time.time()-t0))
    print "\t=> {} concepts in the representation context".format(len(ctx))
    print '\t=> Partition Pattern Concepts Written in: {}'.format(fout_name)