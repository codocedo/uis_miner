import sys
from itertools import chain

from fca.io.transformers import List2PartitionsTransformer
from fca.io.file_models import FileModelFactory
from fca.defs.patterns.hypergraphs import TrimmedPartitionPattern as PartitionPattern
from fca.algorithms.previous_closure import PSPreviousClosure
from lib.minimum_hitting_set import berges_mhs as my_mhs
from fca.io import read_representations
from fca.io.input_models import PatternStructureModel
from fca.io.sorters import PartitionSorter
import csv


from uis_miner_naive import find_uis, print_premises


if __name__ == "__main__":
    filepath = sys.argv[1]
    transposed=True
    fctx = PatternStructureModel(
        filepath=filepath,
#        sorter=PartitionSorter(),
        transformer=List2PartitionsTransformer(transposed),
        transposed=transposed,
        file_manager_params={
            'style': 'tab'
        }
    )

    ondisk_poset = PSPreviousClosure(
        fctx,
        pattern=PartitionPattern,
        ondisk=True,
        ondisk_kwargs={
            'output_path':'/tmp',
            'output_fname':None,
            'write_extent':False
        },
        silent=False
    ).poset
    ctx = []
    fout_name = ondisk_poset.close()
    with open(fout_name , 'r') as fin:
        reader = csv.reader(fin, delimiter='\t')        
        headers = reader.next()
        for row in reader:
            # if row[0] != '-1':
            lst = row[-1]
            lst = lst[lst.find('[')+1:lst.find(']')]
            print row[0], [int(i.strip()) for i in lst.split(',') if ',' in lst]
            ctx.append(set([int(i.strip()) for i in lst.split(',') if ',' in lst]))
    # print ("\t=> Results stored in {}".format(output_path))

    print_premises(find_uis(ctx))
    