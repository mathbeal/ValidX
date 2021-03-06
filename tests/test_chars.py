# coding: utf-8

import pickle

import pytest

from validx import exc
from validx.compat.types import string


NoneType = type(None)


def test_str(module):
    v = module.Str()
    assert v(u"abc") == u"abc"
    assert v.clone() == v
    assert pickle.loads(pickle.dumps(v)) == v


@pytest.mark.parametrize("nullable", [None, False, True])
def test_str_nullable(module, nullable):
    v = module.Str(nullable=nullable)
    assert v(u"abc") == u"abc"
    assert v.clone() == v
    assert pickle.loads(pickle.dumps(v)) == v

    if nullable:
        assert v(None) is None
    else:
        with pytest.raises(exc.InvalidTypeError) as info:
            v(None)
        assert info.value.expected == string
        assert info.value.actual == NoneType


@pytest.mark.parametrize("encoding", [None, "utf-8"])
def test_str_encoding(module, encoding):
    v = module.Str(encoding=encoding)
    assert v(u"abc") == u"abc"
    assert v.clone() == v
    assert pickle.loads(pickle.dumps(v)) == v

    if encoding:
        assert v(b"abc") == u"abc"

        error = u"café".encode("latin-1")
        with pytest.raises(exc.StrDecodeError) as info:
            v(error)
        assert info.value.expected == encoding
        assert info.value.actual == error
    else:
        with pytest.raises(exc.InvalidTypeError) as info:
            v(b"abc")
        assert info.value.expected == string
        assert info.value.actual == bytes


@pytest.mark.parametrize("minlen", [None, 2])
@pytest.mark.parametrize("maxlen", [None, 5])
def test_str_minlen_maxlen(module, minlen, maxlen):
    v = module.Str(minlen=minlen, maxlen=maxlen)
    assert v(u"abc") == u"abc"
    assert v.clone() == v
    assert pickle.loads(pickle.dumps(v)) == v

    if minlen is None:
        assert v(u"a") == u"a"
    else:
        with pytest.raises(exc.MinLengthError) as info:
            v(u"a")
        assert info.value.expected == minlen
        assert info.value.actual == 1

    if maxlen is None:
        assert v(u"abcdef") == u"abcdef"
    else:
        with pytest.raises(exc.MaxLengthError) as info:
            v(u"abcdef")
        assert info.value.expected == maxlen
        assert info.value.actual == 6


@pytest.mark.parametrize("pattern", [None, u"(?i)^[a-z]+$"])
def test_str_pattern(module, pattern):
    v = module.Str(pattern=pattern)
    assert v(u"abc") == u"abc"
    assert v(u"ABC") == u"ABC"
    assert v.clone() == v
    assert pickle.loads(pickle.dumps(v)) == v

    if pattern is None:
        assert v(u"123") == u"123"
    else:
        with pytest.raises(exc.PatternMatchError) as info:
            v(u"123")
        assert info.value.expected == pattern
        assert info.value.actual == u"123"


@pytest.mark.parametrize("options", [None, [u"abc", u"xyz"]])
def test_str_options(module, options):
    v = module.Str(options=options)
    assert v(u"abc") == u"abc"
    assert v(u"xyz") == u"xyz"
    assert v.clone() == v
    assert pickle.loads(pickle.dumps(v)) == v

    if options is None:
        assert v(u"123") == u"123"
    else:
        with pytest.raises(exc.OptionsError) as info:
            v(u"123")
        assert info.value.expected == frozenset(options)
        assert info.value.actual == u"123"


# =============================================================================


def test_bytes(module):
    v = module.Bytes()
    assert v(b"abc") == b"abc"
    assert v.clone() == v
    assert pickle.loads(pickle.dumps(v)) == v


@pytest.mark.parametrize("nullable", [None, False, True])
def test_bytes_nullable(module, nullable):
    v = module.Bytes(nullable=nullable)
    assert v(b"abc") == b"abc"
    assert v.clone() == v
    assert pickle.loads(pickle.dumps(v)) == v

    if nullable:
        assert v(None) is None
    else:
        with pytest.raises(exc.InvalidTypeError) as info:
            v(None)
        assert info.value.expected == bytes
        assert info.value.actual == NoneType


@pytest.mark.parametrize("minlen", [None, 2])
@pytest.mark.parametrize("maxlen", [None, 5])
def test_bytes_minlen_maxlen(module, minlen, maxlen):
    v = module.Bytes(minlen=minlen, maxlen=maxlen)
    assert v(b"abc") == b"abc"
    assert v.clone() == v
    assert pickle.loads(pickle.dumps(v)) == v

    if minlen is None:
        assert v(b"a") == b"a"
    else:
        with pytest.raises(exc.MinLengthError) as info:
            v(b"a")
        assert info.value.expected == minlen
        assert info.value.actual == 1

    if maxlen is None:
        assert v(b"abcdef") == b"abcdef"
    else:
        with pytest.raises(exc.MaxLengthError) as info:
            v(b"abcdef")
        assert info.value.expected == maxlen
        assert info.value.actual == 6
