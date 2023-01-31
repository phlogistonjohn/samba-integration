#!/usr/bin/python3
import os
import subprocess

import pytest
import testhelper
import yaml


_smbtorture_exec = "/bin/smbtorture"


def _read_torture_tests(filename=None, env_name="TORTURE_TESTS"):
    if filename is None:
        filename = os.environ.get(env_name)
    if not filename:
        raise ValueError(f"no {env_name} environment variable set")
    with open(filename) as f:
        smbtorture_info = yaml.safe_load(f)
    return smbtorture_info


def _read_test_info(filename=None, env_name="TEST_INFO"):
    if filename is None:
        filename = os.environ.get(env_name)
    if not filename:
        raise ValueError(f"no {env_name} environment variable set")
    test_info = testhelper.read_yaml(filename)
    return test_info


def _smbtorture(mount_params, test, output):
    username = mount_params["username"]
    password = mount_params["password"]
    host = mount_params["host"]
    share = mount_params["share"]
    cmd = [
        _smbtorture_exec,
        "--fullname",
        "--option=torture:progress=no",
        "--option=torture:sharedelay=100000",
        "--option=torture:writetimeupdatedelay=500000",
        "--format=subunit",
        "--target=samba3",
        f"--user={username}%{password}",
        f"//{host}/{share}",
        test,
    ]
    print(cmd)
    with open(output, "w") as fh:
        subprocess.run(cmd, check=True, stdout=fh, stderr=fh)


@pytest.fixture(scope="module")
def smb_settings(request):
    yield _read_test_info()


def pytest_generate_tests(metafunc):
    if "sharenum" in metafunc.fixturenames:
        test_info = _read_test_info()
        metafunc.parametrize(
            "sharenum", range(testhelper.get_num_shares(test_info))
        )
    if "tt" in metafunc.fixturenames:
        ttests = _read_torture_tests()
        metafunc.parametrize("tt", ttests)


def test_foo():
    assert 1 == 1


def test_smb_torture(smb_settings, tmp_path, sharenum, tt):
    mount_params = testhelper.get_default_mount_params(smb_settings)
    mount_params["share"] = testhelper.get_share(smb_settings, sharenum)
    _smbtorture(mount_params, tt, tmp_path / "out")
