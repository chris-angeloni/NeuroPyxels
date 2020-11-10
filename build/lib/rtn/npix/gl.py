# -*- coding: utf-8 -*-
"""
2018-07-20

@author: Maxime Beau, Neural Computations Lab, University College London

Dataset: Neuropixels dataset -> dp is phy directory (kilosort or spyking circus output)
"""
import os
from rtn.utils import npa
import os.path as op
from pathlib import Path

from ast import literal_eval as ale

import numpy as np
import pandas as pd

def assert_multidatasets(dp):
    'Returns unpacked merged_clusters_spikes.npz if it exists in dp, None otherwise.'
    if op.exists(Path(dp, 'merged_clusters_spikes.npz')):
        mcs=np.load(Path(dp, 'merged_clusters_spikes.npz'))
        return mcs[list(mcs.keys())[0]]


def load_units_qualities(dp):
    f1='cluster_group.tsv'
    f2='cluster_groups.csv'
    if os.path.isfile(Path(dp, f1)):
        qualities = pd.read_csv(Path(dp, f1),delimiter='	')
    elif os.path.isfile(Path(dp, 'merged_'+f1)):
        qualities = pd.read_csv(Path(dp, 'merged_'+f1), delimiter='	', index_col='dataset_i')
    elif os.path.isfile(f2):
        qualities = pd.read_csv(Path(dp, f2), delimiter=',')
    elif os.path.isfile(f2):
        qualities = pd.read_csv(Path(dp, 'merged_'+f2), delimiter=',', index_col='dataset_i')
    else:
        print('cluster groups table not found in provided data path. Exiting.')
        return
    return qualities

def get_units(dp, quality='all'):
    assert quality in ['all', 'good', 'mua', 'noise']
    
    cl_grp = load_units_qualities(dp)
    units=[]
    if cl_grp.index.name=='dataset_i':
        if quality=='all':
            for ds_i in cl_grp.index.unique():
                ds_table=pd.read_csv(Path(dp, 'datasets_table.csv'), index_col='dataset_i')
                ds_dp=ds_table['dp'][ds_i]
                assert op.exists(ds_dp), "WARNING you have instanciated this prophyler merged dataset from paths of which one doesn't exist anymore:{}!n\ \
                Please add the new path of dataset {} in the csv file {}.".format(ds_dp, ds_table['dataset_name'][ds_i], Path(dp, 'datasets_table.csv'))
                ds_units=np.unique(np.load(Path(ds_dp, 'spike_clusters.npy')))
                units += ['{}_{}'.format(ds_i, u) for u in ds_units]
        else:
            for ds_i in cl_grp.index.unique():
                # np.all(cl_grp.loc[ds_i, 'group'][cl_grp.loc[ds_i, 'cluster_id']==u]==quality)
                units += ['{}_{}'.format(ds_i, u) for u in cl_grp.loc[(cl_grp['group']==quality)&(cl_grp.index==ds_i), 'cluster_id']]
        return units
        
    else:
        try:
            np.all(np.isnan(cl_grp['group'])) # Units have not been given a class yet
            units=[]
        except:
            if quality=='all':
                units = np.unique(np.load(Path(dp, 'spike_clusters.npy')))
            else:
                units = cl_grp.loc[np.nonzero(npa(cl_grp['group']==quality))[0], 'cluster_id']
        return np.array(units, dtype=np.int64)

def get_good_units(dp):
    return get_units(dp, quality='good')

def get_prophyler_source(dp_pro, u):
    '''If dp is a prophyler datapath, returns datapath from source dataset and unit as integer.
       Else, returns dp and u as they are.
    '''
    if op.basename(dp_pro)[:9]=='prophyler':
        ds_i, u = u.split('_'); ds_i, u = ale(ds_i), ale(u)
        ds_table=pd.read_csv(Path(dp_pro, 'datasets_table.csv'), index_col='dataset_i')
        ds_dp=ds_table['dp'][ds_i]
        assert op.exists(ds_dp), "WARNING you have instanciated this prophyler merged dataset from paths of which one doesn't exist anymore:{}!n\ \
        Please add the new path of dataset {} in the csv file {}.".format(ds_dp, ds_table['dataset_name'][ds_i], Path(dp_pro, 'datasets_table.csv'))
        dp_pro=ds_dp
    return dp_pro, u