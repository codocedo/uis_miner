import sys
from itertools import chain

from fca.io.transformers import List2PartitionsTransformer
from fca.io.file_models import FileModelFactory
from fca.defs.patterns.hypergraphs import TrimmedPartitionPattern as PartitionPattern
# from fca.defs.patterns.hypergraphs import PartitionPattern
from fca.algorithms.previous_closure import PSPreviousClosure
from lib.minimum_hitting_set import berges_mhs as my_mhs
from fca.io import read_representations
from fca.io.input_models import PatternStructureModel
from fca.io.sorters import PartitionSorter
import csv

from uis_miner_naive import find_uis, print_premises

if __name__ == "__main__":

    filepath = sys.argv[1]

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
    print "{} concepts in the representation context".format(len(ctx))
    print '{}'.format(fout_name)