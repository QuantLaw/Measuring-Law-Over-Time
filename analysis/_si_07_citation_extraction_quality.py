import glob
import multiprocessing
import os
import re
from collections import Counter

import pandas as pd
from lxml import etree

pattern = r'(sect?(ion|\.)s?|parts?|§+)\s+\d'

def get_stats(path):
    tree = etree.parse(path)
    references = list(tree.xpath('//reference'))
    ref_len = len(references)
    
    etree.strip_elements(tree, 'reference', with_tail=False)
    text = etree.tostring(tree, method='text', encoding='utf8')
    other_matches = re.findall(pattern, text.decode('utf8'), flags=re.I)
    other_matches_types = Counter(m[0][0].lower() for m in other_matches)
    res = ref_len, other_matches_types.get('s', 0), other_matches_types.get('§', 0), other_matches_types.get('p', 0)
    cfr_match = re.fullmatch(r'.+cfr(\d+)_(\d+).xml', path)
    if cfr_match:
        return 'cfr', int(cfr_match[2]), int(cfr_match[1]), *res
    else:
        usc_match = re.fullmatch(r'.+/(\d+)0_(\d+).xml', path)
        return 'usc', int(usc_match[2]), int(usc_match[1]), *res

if __name__ == '__main__':
    paths = sorted(glob.glob('../../legal-networks-data/us*/2_xml/*.xml'))
    with multiprocessing.Pool() as p:
        stats = p.map(get_stats, paths, chunksize=1)

    df = pd.DataFrame(stats, columns=['collection', 'year', 'title', 'references', 'other_sections', 'other_symbols', 'other_parts'])
    df.to_csv('../results/reference_extraction_quality_estimation_us.csv', index=False)
