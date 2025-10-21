#!/usr/bin/env python3

from os import listdir
from os.path import isdir, isfile, join
from shutil import rmtree

import pytest

from static_aid import config, make_pages, utils

@pytest.fixture
def setup_dirs():
    utils.remove_file_or_dir(config.STAGING_DIR)
    yield
    # utils.remove_file_or_dir(config.STAGING_DIR)


def test_make_pages(setup_dirs):
    make_pages.main()
    assert isdir(config.STAGING_DIR), "{} must exist".format(config.STAGING_DIR)
    assert isfile(join(config.STAGING_DIR, '_config.yml')), "{} must exist".format(join(config.STAGING_DIR, '_config.yml'))
    assert isfile(join(config.STAGING_DIR, config.sitemap)), "{} must exist".format(join(config.STAGING_DIR, config.sitemap))
    for k, v in config.destinations.items():
        if k not in ['breadcrumbs', 'subjects', 'trees']:
            assert isdir(join(config.STAGING_DIR, k)), "{} must exist".format(join(config.STAGING_DIR, k))        
            assert len(listdir(join(config.STAGING_DIR, k))) == len(listdir(join(config.DATA_DIR, v))) + 1, "The correct number of files should be generated"