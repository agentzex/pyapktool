import subprocess
import os
import pytest
import shutil
from src.pyapktool.pyapktool import init



def change_cwd_to_tmp_dir(tmp_dir):
    # Change the current working directory to setup_test_files
    os.chdir(tmp_dir)
    print(f"Current working directory: {os.getcwd()}")


@pytest.fixture(scope="module")
def setup_test_files(tmp_path_factory):
    # Fixture to copy test files to a temporary directory.

    temp_test_dir = tmp_path_factory.mktemp("test_files")
    local_test_files_dir = "test_files"

    # Copy pre-existing test files
    shutil.copytree(local_test_files_dir, temp_test_dir, dirs_exist_ok=True)
    return temp_test_dir


def test_no_args():
    # Test that the help message is displayed correctly.
    result = subprocess.run(["pyapktool"], capture_output=True, text=True)
    assert result.returncode == 2
    assert "usage" in result.stderr.lower()  # Check for 'usage' in help message


def test_input_hello_world_apk(setup_test_files):
    change_cwd_to_tmp_dir(setup_test_files)
    tested_apk = "hello_world.apk"

    temp_test_dir = setup_test_files
    test_file = temp_test_dir / tested_apk
    assert test_file.exists()

    ret = init(test_file)  # this should return unpack_apk func when giving a .apk file as input
    assert "unpack_apk" in str(ret)


def test_unpack_hello_world_apk(setup_test_files):
    change_cwd_to_tmp_dir(setup_test_files)

    apk_name = "hello_world.apk"
    apk_dir = "hello_world"

    temp_test_dir = setup_test_files
    tested_apk = temp_test_dir / apk_name
    assert tested_apk.is_file()

    result = subprocess.run(["pyapktool", tested_apk], capture_output=True, text=True) # should unpack
    assert result.returncode == 0

    expected_unpacked_apk_dir = temp_test_dir / apk_dir
    assert expected_unpacked_apk_dir.is_dir()

    # if unpacking was successful, expect to have files like AndroidManifest.xml in the unpacked dir
    manifest_file = expected_unpacked_apk_dir / "AndroidManifest.xml"
    assert manifest_file.is_file()


def test_pack_and_sign_hello_world_apk(setup_test_files):
    # This tests expects test_unpack_hello_world_apk() test to run before it, and uses its output

    change_cwd_to_tmp_dir(setup_test_files)
    apk_dir = "hello_world"

    temp_test_dir = setup_test_files
    expected_unpacked_apk_dir = temp_test_dir / apk_dir
    assert expected_unpacked_apk_dir.is_dir()

    result = subprocess.run(["pyapktool", expected_unpacked_apk_dir], capture_output=True, text=True) # should pack and sign
    print(f"stdout: {result.stdout}")
    print(f"stderr: {result.stderr}")

    assert result.returncode == 0

    signed_apk_name = "hello_world-signed.apk"
    tested_signed_apk = temp_test_dir / signed_apk_name

    assert tested_signed_apk.is_file()
