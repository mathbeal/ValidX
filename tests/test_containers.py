import pickle
from collections import OrderedDict, defaultdict, deque

import pytest

from webob.multidict import MultiDict as WebObMultiDict  # noqa
from werkzeug.datastructures import MultiDict as WerkzeugMultiDict  # noqa

try:
    from multidict import MultiDict  # noqa
except ImportError:
    pass

from validx import exc
from validx.compat.types import string
from validx.compat.colabc import Sequence, Mapping


NoneType = type(None)


@pytest.fixture(
    params=[
        classname
        for classname in ("WebObMultiDict", "WerkzeugMultiDict", "MultiDict")
        if classname in globals()
    ]
)
def multidict_class(request):
    return globals()[request.param]


class CustomSequence(Sequence):
    def __init__(self, *items):
        self.items = items

    def __getitem__(self, index):
        return self.items[index]

    def __len__(self):
        return len(self.items)


class CustomMapping(Mapping):
    def __init__(self, content):
        self.content = content

    def __getitem__(self, key):
        return self.content[key]

    def __iter__(self):
        return iter(self.content)

    def __len__(self):
        return len(self.content)


# =============================================================================


def test_list(module):
    v = module.List(module.Int())
    assert v([1, 2, 3]) == [1, 2, 3]
    assert v((1, 2, 3)) == [1, 2, 3]
    assert v(CustomSequence(1, 2, 3)) == [1, 2, 3]
    assert v.clone() == v
    assert pickle.loads(pickle.dumps(v)) == v

    with pytest.raises(exc.InvalidTypeError) as info:
        v(u"1, 2, 3")
    assert info.value.expected == Sequence
    assert info.value.actual == string

    with pytest.raises(exc.SchemaError) as info:
        v([1, u"2", 3, None])
    assert len(info.value) == 2

    assert isinstance(info.value[0], exc.InvalidTypeError)
    assert info.value[0].context == deque([1])
    assert info.value[0].expected == int
    assert info.value[0].actual == string

    assert isinstance(info.value[1], exc.InvalidTypeError)
    assert info.value[1].context == deque([3])
    assert info.value[1].expected == int
    assert info.value[1].actual == NoneType


@pytest.mark.parametrize("nullable", [None, False, True])
def test_list_nullable(module, nullable):
    v = module.List(module.Int(), nullable=nullable)
    assert v([1, 2, 3]) == [1, 2, 3]
    assert v((1, 2, 3)) == [1, 2, 3]
    assert v(CustomSequence(1, 2, 3)) == [1, 2, 3]
    assert v.clone() == v
    assert pickle.loads(pickle.dumps(v)) == v

    if nullable:
        assert v(None) is None
    else:
        with pytest.raises(exc.InvalidTypeError) as info:
            v(None)
        assert info.value.expected == Sequence
        assert info.value.actual == NoneType


@pytest.mark.parametrize("minlen", [None, 2])
@pytest.mark.parametrize("maxlen", [None, 5])
def test_list_minlen_maxlen(module, minlen, maxlen):
    v = module.List(module.Int(), minlen=minlen, maxlen=maxlen)
    assert v([1, 2, 3]) == [1, 2, 3]
    assert v((1, 2, 3)) == [1, 2, 3]
    assert v(CustomSequence(1, 2, 3)) == [1, 2, 3]
    assert v.clone() == v
    assert pickle.loads(pickle.dumps(v)) == v

    if minlen is None:
        assert v([1]) == [1]
    else:
        with pytest.raises(exc.MinLengthError) as info:
            v([1])
        assert info.value.expected == minlen
        assert info.value.actual == 1

        # First item doesn't pass validation, so the result length is 1.
        # However, it should not raise MinLengthError, but SchemaError instead.
        with pytest.raises(exc.SchemaError) as info:
            v(["1", 2])
        assert len(info.value) == 1

    if maxlen is None:
        assert v([1, 2, 3, 4, 5, 6]) == [1, 2, 3, 4, 5, 6]
    else:
        with pytest.raises(exc.MaxLengthError) as info:
            v([1, 2, 3, 4, 5, 6])
        assert info.value.expected == maxlen
        assert info.value.actual == 6


def test_list_minlen_maxlen_unique(module):
    v = module.List(module.Int(), minlen=2, maxlen=5, unique=True)
    assert v([1, 2, 3]) == [1, 2, 3]
    assert v((1, 2, 3)) == [1, 2, 3]
    assert v(CustomSequence(1, 2, 3)) == [1, 2, 3]
    assert v.clone() == v
    assert pickle.loads(pickle.dumps(v)) == v

    assert v([1, 1, 1, 2, 2, 2, 3, 3, 3]) == [1, 2, 3]

    with pytest.raises(exc.MinLengthError) as info:
        v([1, 1, 1])
    assert info.value.expected == 2
    assert info.value.actual == 1

    with pytest.raises(exc.MaxLengthError) as info:
        v([1, 1, 1, 2, 3, 4, 5, 6])
    assert info.value.expected == 5
    assert info.value.actual == 6


@pytest.mark.parametrize("unique", [None, False, True])
def test_list_unique(module, unique):
    v = module.List(module.Int(), unique=unique)
    assert v([1, 2, 3]) == [1, 2, 3]
    assert v((1, 2, 3)) == [1, 2, 3]
    assert v(CustomSequence(1, 2, 3)) == [1, 2, 3]
    assert v.clone() == v
    assert pickle.loads(pickle.dumps(v)) == v

    if unique:
        assert v([1, 2, 3, 3, 2, 1]) == [1, 2, 3]
    else:
        assert v([1, 2, 3, 3, 2, 1]) == [1, 2, 3, 3, 2, 1]


def test_list_context(module):
    class MarkContext(module.Validator):
        def __call__(self, value, __context=None):
            __context["marked"] = True
            return value

    v = module.List(MarkContext())
    context = {}
    v([None], context)
    assert context["marked"]


# =============================================================================


def test_tuple(module):
    v = module.Tuple(module.Int(), module.Int())
    assert v([1, 2]) == (1, 2)
    assert v((1, 2)) == (1, 2)
    assert v(CustomSequence(1, 2)) == (1, 2)
    assert v.clone() == v
    assert pickle.loads(pickle.dumps(v)) == v

    with pytest.raises(exc.InvalidTypeError) as info:
        v(u"1, 2")
    assert info.value.expected == Sequence
    assert info.value.actual == string

    with pytest.raises(exc.TupleLengthError) as info:
        v([1, 2, 3])
    assert info.value.expected == 2
    assert info.value.actual == 3

    with pytest.raises(exc.SchemaError) as info:
        v([u"1", None])
    assert len(info.value) == 2

    assert isinstance(info.value[0], exc.InvalidTypeError)
    assert info.value[0].context == deque([0])
    assert info.value[0].expected == int
    assert info.value[0].actual == string

    assert isinstance(info.value[1], exc.InvalidTypeError)
    assert info.value[1].context == deque([1])
    assert info.value[1].expected == int
    assert info.value[1].actual == NoneType


@pytest.mark.parametrize("nullable", [None, False, True])
def test_tuple_nullable(module, nullable):
    v = module.Tuple(module.Int(), module.Int(), nullable=nullable)
    assert v([1, 2]) == (1, 2)
    assert v((1, 2)) == (1, 2)
    assert v(CustomSequence(1, 2)) == (1, 2)
    assert v.clone() == v
    assert pickle.loads(pickle.dumps(v)) == v

    if nullable:
        assert v(None) is None
    else:
        with pytest.raises(exc.InvalidTypeError) as info:
            v(None)
        assert info.value.expected == Sequence
        assert info.value.actual == NoneType


def test_tuple_context(module):
    class MarkContext(module.Validator):
        def __call__(self, value, __context=None):
            __context["marked"] = True
            return value

    v = module.Tuple(MarkContext())
    context = {}
    v((None,), context)
    assert context["marked"]


# =============================================================================


def test_dict(module):
    v = module.Dict({u"x": module.Int(), u"y": module.Int()})
    assert v({u"x": 1, u"y": 2}) == {u"x": 1, u"y": 2}
    assert v(OrderedDict({u"x": 1, u"y": 2})) == {u"x": 1, u"y": 2}
    assert v(defaultdict(None, {u"x": 1, u"y": 2})) == {u"x": 1, u"y": 2}
    assert v(CustomMapping({u"x": 1, u"y": 2})) == {u"x": 1, u"y": 2}
    assert v.clone() == v
    assert pickle.loads(pickle.dumps(v)) == v

    with pytest.raises(exc.InvalidTypeError) as info:
        v([(u"x", 1), (u"y", 2)])
    assert info.value.expected == Mapping
    assert info.value.actual == list

    with pytest.raises(exc.SchemaError) as info:
        v({u"x": u"1", u"y": None})
    assert len(info.value) == 2

    info.value.sort()

    assert isinstance(info.value[0], exc.InvalidTypeError)
    assert info.value[0].context == deque([u"x"])
    assert info.value[0].expected == int
    assert info.value[0].actual == string

    assert isinstance(info.value[1], exc.InvalidTypeError)
    assert info.value[1].context == deque([u"y"])
    assert info.value[1].expected == int
    assert info.value[1].actual == NoneType


@pytest.mark.parametrize("nullable", [None, False, True])
def test_dict_nullable(module, nullable):
    v = module.Dict({u"x": module.Int(), u"y": module.Int()}, nullable=nullable)
    assert v({u"x": 1, u"y": 2}) == {u"x": 1, u"y": 2}
    assert v(OrderedDict({u"x": 1, u"y": 2})) == {u"x": 1, u"y": 2}
    assert v(defaultdict(None, {u"x": 1, u"y": 2})) == {u"x": 1, u"y": 2}
    assert v(CustomMapping({u"x": 1, u"y": 2})) == {u"x": 1, u"y": 2}
    assert v.clone() == v
    assert pickle.loads(pickle.dumps(v)) == v

    if nullable:
        assert v(None) is None
    else:
        with pytest.raises(exc.InvalidTypeError) as info:
            v(None)
        assert info.value.expected == Mapping
        assert info.value.actual == NoneType


@pytest.mark.parametrize("minlen", [None, 2])
@pytest.mark.parametrize("maxlen", [None, 3])
def test_dict_minlen_maxlen(module, minlen, maxlen):
    v = module.Dict(extra=(module.Str(), module.Int()), minlen=minlen, maxlen=maxlen)
    assert v({u"x": 1, u"y": 2}) == {u"x": 1, u"y": 2}
    assert v(OrderedDict({u"x": 1, u"y": 2})) == {u"x": 1, u"y": 2}
    assert v(defaultdict(None, {u"x": 1, u"y": 2})) == {u"x": 1, u"y": 2}
    assert v(CustomMapping({u"x": 1, u"y": 2})) == {u"x": 1, u"y": 2}
    assert v.clone() == v
    assert pickle.loads(pickle.dumps(v)) == v

    if minlen is None:
        assert v({u"x": 1}) == {u"x": 1}
    else:
        with pytest.raises(exc.MinLengthError) as info:
            v({u"x": 1})
        assert info.value.expected == minlen
        assert info.value.actual == 1

        # First key doesn't pass validation, so the result length is 1.
        # However, it should not raise MinLengthError, but SchemaError instead.
        with pytest.raises(exc.SchemaError) as info:
            v({u"x": "1", u"y": 2})
        assert len(info.value) == 1

    if maxlen is None:
        assert v({u"x": 1, u"y": 2, u"z": 3, u"a": 4}) == {
            u"x": 1,
            u"y": 2,
            u"z": 3,
            u"a": 4,
        }
    else:
        with pytest.raises(exc.MaxLengthError) as info:
            v({u"x": 1, u"y": 2, u"z": 3, u"a": 4})
        assert info.value.expected == maxlen
        assert info.value.actual == 4


def default_x():
    """ Pickable version of callable default value """
    return 0


@pytest.mark.parametrize("defaults", [None, {u"x": 0}, {u"x": default_x}])
@pytest.mark.parametrize("optional", [None, [u"x"]])
def test_dict_defaults_and_optional(module, defaults, optional):
    v = module.Dict(
        {u"x": module.Int(), u"y": module.Int()}, defaults=defaults, optional=optional
    )
    assert v({u"x": 1, u"y": 2}) == {u"x": 1, u"y": 2}
    assert v(OrderedDict({u"x": 1, u"y": 2})) == {u"x": 1, u"y": 2}
    assert v(defaultdict(None, {u"x": 1, u"y": 2})) == {u"x": 1, u"y": 2}
    assert v(CustomMapping({u"x": 1, u"y": 2})) == {u"x": 1, u"y": 2}
    assert v.clone() == v
    assert pickle.loads(pickle.dumps(v)) == v

    with pytest.raises(exc.SchemaError) as info:
        v({u"x": 1})
    assert len(info.value) == 1
    assert isinstance(info.value[0], exc.MissingKeyError)
    assert info.value[0].context == deque([u"y"])

    if defaults:
        assert v({u"y": 2}) == {u"x": 0, u"y": 2}
    elif optional:
        assert v({u"y": 2}) == {u"y": 2}
    else:
        with pytest.raises(exc.SchemaError) as info:
            v({u"y": 2})
        assert len(info.value) == 1
        assert isinstance(info.value[0], exc.MissingKeyError)
        assert info.value[0].context == deque([u"x"])


def test_dict_defaults_validation(module):
    v = module.Dict(
        {u"x": module.Dict({u"y": module.Int()}, defaults={u"y": 1})},
        defaults={u"x": {}},
    )
    assert v.clone() == v
    assert pickle.loads(pickle.dumps(v)) == v
    assert v({}) == {u"x": {u"y": 1}}

    v = module.Dict(
        {u"x": module.Dict({u"y": module.Int()}, defaults={u"y": 1})},
        defaults={"x": []},
    )
    with pytest.raises(exc.SchemaError) as info:
        v({})
    assert len(info.value) == 1
    assert isinstance(info.value[0], exc.InvalidTypeError)
    assert info.value[0].context == deque([u"x"])
    assert info.value[0].expected == Mapping
    assert info.value[0].actual == list


def test_dict_defaults_and_minlen_maxlen(module):
    v = module.Dict(
        {u"x": module.Int()},
        defaults={u"x": 1},
        extra=(module.Str(), module.Int()),
        minlen=2,
        maxlen=3,
    )
    assert v.clone() == v
    assert pickle.loads(pickle.dumps(v)) == v
    assert v({u"y": 2, u"z": 3}) == {u"x": 1, u"y": 2, u"z": 3}

    with pytest.raises(exc.MinLengthError) as info:
        v({})
    assert info.value.expected == 2
    assert info.value.actual == 1

    with pytest.raises(exc.MaxLengthError) as info:
        v({u"y": 2, u"z": 3, u"too_much": 4})
    assert info.value.expected == 3
    assert info.value.actual == 4


@pytest.mark.parametrize("extra", [None, True])
def test_dict_extra(module, extra):
    if extra:
        extra = (module.Str(), module.Int())
    v = module.Dict({u"x": module.Int(), u"y": module.Int()}, extra=extra)
    assert v({u"x": 1, u"y": 2}) == {u"x": 1, u"y": 2}
    assert v(OrderedDict({u"x": 1, u"y": 2})) == {u"x": 1, u"y": 2}
    assert v(defaultdict(None, {u"x": 1, u"y": 2})) == {u"x": 1, u"y": 2}
    assert v(CustomMapping({u"x": 1, u"y": 2})) == {u"x": 1, u"y": 2}
    assert v.clone() == v
    assert pickle.loads(pickle.dumps(v)) == v

    if extra:
        assert v({u"x": 1, u"y": 2, u"z": 3}) == {u"x": 1, u"y": 2, u"z": 3}

        with pytest.raises(exc.SchemaError) as info:
            v({u"x": 1, u"y": 2, 3: None})
        assert len(info.value) == 2

        info.value.sort()

        assert isinstance(info.value[0], exc.InvalidTypeError)
        assert info.value[0].context == deque([3, exc.EXTRA_KEY])
        assert info.value[0].expected == string
        assert info.value[0].actual == int

        assert isinstance(info.value[1], exc.InvalidTypeError)
        assert info.value[1].context == deque([3, exc.EXTRA_VALUE])
        assert info.value[1].expected == int
        assert info.value[1].actual == NoneType
    else:
        with pytest.raises(exc.SchemaError) as info:
            v({u"x": 1, u"y": 2, u"z": 3})
        assert len(info.value) == 1
        assert isinstance(info.value[0], exc.ForbiddenKeyError)
        assert info.value[0].context == deque([u"z"])


@pytest.mark.parametrize("dispose", [None, [u"z"]])
def test_dict_dispose(module, dispose):
    v = module.Dict({u"x": module.Int(), u"y": module.Int()}, dispose=dispose)
    assert v({u"x": 1, u"y": 2}) == {u"x": 1, u"y": 2}
    assert v(OrderedDict({u"x": 1, u"y": 2})) == {u"x": 1, u"y": 2}
    assert v(defaultdict(None, {u"x": 1, u"y": 2})) == {u"x": 1, u"y": 2}
    assert v(CustomMapping({u"x": 1, u"y": 2})) == {u"x": 1, u"y": 2}
    assert v.clone() == v
    assert pickle.loads(pickle.dumps(v)) == v

    if dispose:
        assert v({u"x": 1, u"y": 2, u"z": 3}) == {u"x": 1, u"y": 2}
    else:
        with pytest.raises(exc.SchemaError) as info:
            v({u"x": 1, u"y": 2, u"z": 3})
        assert len(info.value) == 1
        assert isinstance(info.value[0], exc.ForbiddenKeyError)
        assert info.value[0].context == deque([u"z"])


def test_dict_multikeys(module, multidict_class):
    v1 = module.Dict({u"x": module.Int(), u"y": module.Int()})
    v2 = module.Dict(
        {u"x": module.Int(), u"y": module.List(module.Int())}, multikeys=[u"y"]
    )
    data = multidict_class([(u"x", 1), (u"y", 2), (u"y", 3)])

    assert v1(data) == {u"x": 1, u"y": 3} or v1(data) == {u"x": 1, u"y": 2}
    assert v2(data) == {u"x": 1, u"y": [2, 3]}
    assert v1.clone() == v1
    assert v2.clone() == v2


def test_dict_context(module):
    class MarkContext(module.Validator):
        def __call__(self, value, __context=None):
            __context["marked"] = True
            return value

    v = module.Dict({u"x": MarkContext()})
    context = {}
    v({u"x": None}, context)
    assert context["marked"]

    v = module.Dict({u"x": MarkContext()}, defaults={u"x": None})
    context = {}
    v({}, context)
    assert context["marked"]

    v = module.Dict(extra=(module.Str(), MarkContext()))
    context = {}
    v({u"x": None}, context)
    assert context["marked"]

    v = module.Dict(extra=(MarkContext(), module.Any()))
    context = {}
    v({u"x": None}, context)
    assert context["marked"]
