import sys

src_dir = "./src"
sys.path.append(src_dir)

import pytest
import test_utils


@pytest.fixture
def create_test_resource():
    return test_utils.create_test_resource


@pytest.fixture
def create_test_step():
    return test_utils.create_test_step


@pytest.fixture
def cleanup_temp_files():
    return test_utils.cleanup_temp_files
