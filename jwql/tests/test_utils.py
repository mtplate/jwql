#!/usr/bin/env python
"""Tests for the ``utils`` module.

Authors
-------

    - Lauren Chambers
    - Matthew Bourque

Use
---

    These tests can be run via the command line (omit the -s to
    suppress verbose output to stdout):

    ::

        pytest -s test_utils.py
"""

import os

import pytest

from jwql.utils.utils import get_config, filename_parser


FILENAME_PARSER_TEST_DATA = [

    # Test full path
    ('/test/dir/to/the/file/jw90002/jw90002001001_02102_00001_nis_rateints.fits',
     {'activity': '02',
      'detector': 'nis',
      'exposure_id': '00001',
      'filename_type': 'stage_1_and_2',
      'instrument': 'niriss',
      'observation': '001',
      'parallel_seq_id': '1',
      'program_id': '90002',
      'suffix': 'rateints',
      'visit': '001',
      'visit_group': '02'}),

    # Test full stage 1 and 2 filename
    ('jw00327001001_02101_00002_nrca1_rate.fits',
     {'activity': '01',
      'detector': 'nrca1',
      'exposure_id': '00002',
      'filename_type': 'stage_1_and_2',
      'instrument': 'nircam',
      'observation': '001',
      'parallel_seq_id': '1',
      'program_id': '00327',
      'suffix': 'rate',
      'visit': '001',
      'visit_group': '02'}),

    # Test root stage 1 and 2 filename
    ('jw00327001001_02101_00002_nrca1',
     {'activity': '01',
      'detector': 'nrca1',
      'exposure_id': '00002',
      'filename_type': 'stage_1_and_2',
      'instrument': 'nircam',
      'observation': '001',
      'parallel_seq_id': '1',
      'program_id': '00327',
      'visit': '001',
      'visit_group': '02'}),

    # Test full stage 2c filename
    ('jw94015002002_02108_00001_mirimage_o002_crf.fits',
     {'ac_id': 'o002',
      'activity': '08',
      'detector': 'mirimage',
      'exposure_id': '00001',
      'filename_type': 'stage_2c',
      'instrument': 'miri',
      'observation': '002',
      'parallel_seq_id': '1',
      'program_id': '94015',
      'suffix': 'crf',
      'visit': '002',
      'visit_group': '02'}),

    # Test root stage 2c filename
    ('jw90001001003_02101_00001_nis_o001',
     {'ac_id': 'o001',
      'activity': '01',
      'detector': 'nis',
      'exposure_id': '00001',
      'filename_type': 'stage_2c',
      'instrument': 'niriss',
      'observation': '001',
      'parallel_seq_id': '1',
      'program_id': '90001',
      'visit': '003',
      'visit_group': '02'}),

    # Test full stage 3 filename with target_id
    ('jw80600-o009_t001_miri_f1130w_i2d.fits',
     {'ac_id': 'o009',
      'filename_type': 'stage_3_target_id',
      'instrument': 'miri',
      'optical_elements': 'f1130w',
      'program_id': '80600',
      'suffix': 'i2d',
      'target_id': 't001'}),

    # Test full stage 3 filename with target_id and different ac_id
    ('jw80600-c0001_t001_miri_f1130w_i2d.fits',
     {'ac_id': 'c0001',
      'filename_type': 'stage_3_target_id',
      'instrument': 'miri',
      'optical_elements': 'f1130w',
      'program_id': '80600',
      'suffix': 'i2d',
      'target_id': 't001'}),

    # Test full stage 3 filename with source_id
    ('jw80600-o009_s00001_miri_f1130w_i2d.fits',
     {'ac_id': 'o009',
      'filename_type': 'stage_3_source_id',
      'instrument': 'miri',
      'optical_elements': 'f1130w',
      'program_id': '80600',
      'source_id': 's00001',
      'suffix': 'i2d'}),

    # Test stage 3 filename with target_id and epoch
    ('jw80600-o009_t001-epoch1_miri_f1130w_i2d.fits',
     {'ac_id': 'o009',
      'filename_type': 'stage_3_target_id_epoch',
      'instrument': 'miri',
      'epoch': '1',
      'optical_elements': 'f1130w',
      'program_id': '80600',
      'suffix': 'i2d',
      'target_id': 't001'}),

    # Test stage 3 filename with source_id and epoch
    ('jw80600-o009_s00001-epoch1_miri_f1130w_i2d.fits',
     {'ac_id': 'o009',
      'filename_type': 'stage_3_source_id_epoch',
      'instrument': 'miri',
      'epoch': '1',
      'optical_elements': 'f1130w',
      'program_id': '80600',
      'source_id': 's00001',
      'suffix': 'i2d'}),

    # Test root stage 3 filename with target_id
    ('jw80600-o009_t001_miri_f1130w',
     {'ac_id': 'o009',
      'filename_type': 'stage_3_target_id',
      'instrument': 'miri',
      'optical_elements': 'f1130w',
      'program_id': '80600',
      'target_id': 't001'}),

    # Test root stage 3 filename with source_id
    ('jw80600-o009_s00001_miri_f1130w',
     {'ac_id': 'o009',
      'filename_type': 'stage_3_source_id',
      'instrument': 'miri',
      'optical_elements': 'f1130w',
      'program_id': '80600',
      'source_id': 's00001'}),

    # Test full time series filename
    ('jw00733003001_02101_00002-seg001_nrs1_rate.fits',
     {'activity': '01',
      'detector': 'nrs1',
      'exposure_id': '00002',
      'filename_type': 'time_series',
      'instrument': 'nirspec',
      'observation': '003',
      'parallel_seq_id': '1',
      'program_id': '00733',
      'segment': '001',
      'suffix': 'rate',
      'visit': '001',
      'visit_group': '02'}),

    # Test root time series filename
    ('jw00733003001_02101_00002-seg001_nrs1',
     {'activity': '01',
      'detector': 'nrs1',
      'exposure_id': '00002',
      'filename_type': 'time_series',
      'instrument': 'nirspec',
      'observation': '003',
      'parallel_seq_id': '1',
      'program_id': '00733',
      'segment': '001',
      'visit': '001',
      'visit_group': '02'}),

    # Test full guider ID filename
    ('jw00729011001_gs-id_1_image_cal.fits',
     {'date_time': None,
      'filename_type': 'guider',
      'guide_star_attempt_id': '1',
      'guider_mode': 'id',
      'instrument': 'fgs',
      'observation': '011',
      'program_id': '00729',
      'suffix': 'image_cal',
      'visit': '001'}),

    # Test root guider ID filename
    ('jw00327001001_gs-id_2',
     {'date_time': None,
      'filename_type': 'guider',
      'guide_star_attempt_id': '2',
      'guider_mode': 'id',
      'instrument': 'fgs',
      'observation': '001',
      'program_id': '00327',
      'visit': '001'}),

    # Test full guider non-ID filename
    ('jw86600048001_gs-fg_2016018175411_stream.fits',
     {'date_time': '2016018175411',
      'filename_type': 'guider',
      'guide_star_attempt_id': None,
      'guider_mode': 'fg',
      'instrument': 'fgs',
      'observation': '048',
      'program_id': '86600',
      'suffix': 'stream',
      'visit': '001'}),

    # Test root guider non-ID filename
    ('jw00729011001_gs-acq2_2019155024808',
     {'date_time': '2019155024808',
      'filename_type': 'guider',
      'guide_star_attempt_id': None,
      'guider_mode': 'acq2',
      'instrument': 'fgs',
      'observation': '011',
      'program_id': '00729',
      'visit': '001'})

]


@pytest.mark.xfail(raises=FileNotFoundError,
                   reason='User must manually supply config file.')
def test_get_config():
    """Assert that the ``get_config`` function successfully creates a
    dictionary.
    """
    settings = get_config()
    assert isinstance(settings, dict)


@pytest.mark.parametrize('filename, solution', FILENAME_PARSER_TEST_DATA)
def test_filename_parser(filename, solution):
    """Generate a dictionary with parameters from a JWST filename.
    Assert that the dictionary matches what is expected.

    Parameters
    ----------
    filename : str
        The filename to test (e.g. ``jw00327001001_02101_00002_nrca1_rate.fits``)
    solution : dict
        A dictionary of the expected result
    """

    assert filename_parser(filename) == solution


@pytest.mark.xfail(raises=(FileNotFoundError, ValueError), 
                   reason='Known non-compliant files in filesystem; User must manually supply config file.')
def test_filename_parser_whole_filesystem():
    """Test the filename_parser on all files currently in the filesystem.
    """
    # Get all files
    filesystem_dir = get_config()['filesystem']
    all_files = []
    for dir_name, _, file_list in os.walk(filesystem_dir):
        for file in file_list:
            if file.endswith('.fits'):
                all_files.append(os.path.join(dir_name, file))

    # Run the filename_parser on all files
    bad_filenames = []
    for filepath in all_files:
        try:
            filename_parser(filepath)
        except ValueError:
            bad_filenames.append(os.path.basename(filepath))

    # Determine if the test failed
    fail = bad_filenames != []
    failure_msg = '{} files could not be successfully parsed: \n - {}'.\
        format(len(bad_filenames), '\n - '.join(bad_filenames))

    # Check which ones failed
    assert not fail, failure_msg


def test_filename_parser_nonJWST():
    """Attempt to generate a file parameter dictionary from a file
    that is not formatted in the JWST naming convention. Ensure the
    appropriate error is raised.
    """
    with pytest.raises(ValueError):
        filename = 'not_a_jwst_file.fits'
        filename_parser(filename)
