#!/usr/bin/env python

import os
from mountaintools import client as mt
from load_study_set_from_md import load_study_set_from_md

# mt.login()
upload_to = 'spikeforest.kbucket'
upload_public_to = 'spikeforest.public'

# The base directory used below
# basedir = 'kbucket://15734439d8cf/groundtruth'
basedir = os.getenv('GROUNDTRUTH_PATH', '/mnt/home/jjun/ceph/groundtruth')

group_name = 'synth_mearec_neuronexus'


def prepare_synth_mearec_neuronexus_studies(*, basedir):
    study_sets = [
        load_study_set_from_md('descriptions/spf_synth_mearec_neuronexus.md')
    ]
    study_set_name = study_sets[0]['name']

    study_set_dir0 = basedir + '/mearec_synth/neuronexus'
    study_set_dir = mt.createSnapshot(study_set_dir0, upload_to=upload_to, upload_recursive=False, download_recursive=False)
    mt.createSnapshot(study_set_dir0, upload_to=upload_public_to, upload_recursive=False, download_recursive=False)
    if not study_set_dir:
        raise Exception('Failed to create snapshot of study set directory: ' + study_set_dir0)
    study_set_dir = study_set_dir + '.synth_mearec_neuronexus'
    print('Using study set dir: ' + study_set_dir)
    studies = []
    recordings = []
    names = []
    names = names + ['noise10_K10_C32', 'noise10_K20_C32', 'noise10_K40_C32']
    names = names + ['noise20_K10_C32', 'noise20_K20_C32', 'noise20_K40_C32']
    for name in names:
        study_name = 'synth_mearec_neuronexus_' + name
        print('PREPARING: ' + study_name)
        study_dir = study_set_dir + '/datasets_' + name
        study0 = dict(
            name=study_name,
            study_set=study_set_name,
            directory=study_dir,
            description=''
        )
        studies.append(study0)
        dd = mt.readDir(study_dir)
        dirnames = sorted(list(dd['dirs'].keys()))
        for i, dsname in enumerate(dirnames):
            dsdir = '{}/{}'.format(study_dir, dsname)
            recordings.append(dict(
                name=dsname,
                study=study_name,
                directory=dsdir,
                firings_true=dsdir + '/firings_true.mda',
                index_within_study=i,
                description='One of the recordings in the {} study'.format(
                    study_name)
            ))
    return studies, recordings, study_sets


# Prepare the studies
studies, recordings, study_sets = prepare_synth_mearec_neuronexus_studies(basedir=basedir)

print('Uploading files to kachery...')
for rec in recordings:
    mt.createSnapshot(rec['directory'], upload_to=upload_to, upload_recursive=True)
    if rec['index_within_study'] == 0:
        mt.createSnapshot(rec['directory'], upload_to=upload_public_to, upload_recursive=True)
        rec['public'] = True
    mt.createSnapshot(rec['directory'] + '/geom.csv', upload_to=upload_public_to)
    mt.createSnapshot(rec['directory'] + '/params.json', upload_to=upload_public_to)

print('Saving object...')
for ut in [upload_to, upload_public_to]:
    address = mt.saveObject(
        object=dict(
            studies=studies,
            recordings=recordings,
            study_sets=study_sets
        ),
        key=dict(name='spikeforest_recording_group', group_name=group_name),
        upload_to=ut
    )
    if not address:
        raise Exception('Problem uploading object to {}'.format(ut))

output_fname = 'key://pairio/spikeforest/spikeforest_recording_group.{}.json'.format(group_name)
print('Saving output to {}'.format(output_fname))
mt.createSnapshot(path=address, dest_path=output_fname)

print('Done.')
