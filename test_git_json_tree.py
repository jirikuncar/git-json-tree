"""Test Git-JSON-Tree library."""

import json
import os
from string import printable

import hypothesis.strategies as st
import pytest
from click.testing import CliRunner
from dulwich.repo import Repo
from hypothesis import assume, given, settings

from git_json_tree import cli, decode, encode


@pytest.fixture()
def repo(tmpdir):
    """Create a repo."""
    curdir = os.getcwd()
    try:
        os.chdir(str(tmpdir))
        yield Repo.init_bare(str(tmpdir))
    finally:
        os.chdir(curdir)


@pytest.fixture()
def runner(repo):
    """Define a click runner."""
    yield CliRunner()


def json_data():
    """Generate JSON data."""
    return st.recursive(
        st.none() |
        st.booleans() |
        st.integers() |
        st.floats(allow_nan=False) |
        st.text(printable),
        lambda children:
            st.lists(children) |
            st.dictionaries(
                st.text(
                    set(printable) - set('/'),
                    min_size=1,
                ),
                children,
            ),
        max_leaves=50,
    )


@given(data=json_data())
@settings(max_examples=1000, deadline=10000)
def test_encode_decode(data, repo):
    """Test (d)encoding."""
    assume(isinstance(data, (dict, list)))
    assert decode(repo, encode(repo, data)) == data


@given(data=json_data())
@settings(max_examples=100, deadline=10000)
def test_cli_encoder(data, runner):
    """Test cli encoder."""
    assume(isinstance(data, (dict, list)) and data)
    encoded = runner.invoke(cli, ['encode'], input=json.dumps(data))
    assert encoded.exit_code == 0
    decoded = runner.invoke(cli, ['decode', encoded.output.strip()])
    assert decoded.exit_code == 0
    assert json.loads(decoded.output_bytes.decode('utf-8')) == data


@given(data=json_data())
@settings(max_examples=100, deadline=10000)
def test_smudge_clean(data, runner):
    """Test Git integration."""
    assume(isinstance(data, (dict, list)) and data)
    cleaned = runner.invoke(cli, ['clean'], input=json.dumps(data))
    assert cleaned.exit_code == 0
    smudged = runner.invoke(cli, ['smudge'], input=cleaned.output)
    assert smudged.exit_code == 0
    assert json.loads(smudged.output_bytes.decode('utf-8')) == data
