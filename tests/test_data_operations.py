import pytest

from yfc import _data_operations as dops
from yfc._exceptions import BadTickersFormatError


def test__get_ticker_string_from_list__string__raises():
    with pytest.raises(BadTickersFormatError):
        dops.get_ticker_string_from_list('a string')
