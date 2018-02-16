"""Test Git-JSON-Tree library."""

from string import printable

import hypothesis.strategies as st
import pytest
from dulwich.repo import Repo
from hypothesis import assume, given, settings

from git_json_tree import decode, encode


@pytest.fixture()
def repo(tmpdir):
    """Create a repo."""
    yield Repo.init_bare(str(tmpdir))


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
        max_leaves=500,
    )


@given(data=json_data())
@settings(max_examples=1000, deadline=10000)
def test_encode_decode(data, repo):
    """Test (d)encoding."""
    assume(isinstance(data, (dict, list)))
    assert decode(repo, encode(repo, data)) == data
