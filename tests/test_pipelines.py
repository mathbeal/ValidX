try:
    import typing as t  # noqa
except ImportError:
    pass

import pytest  # type: ignore

from validateit import py, cy
from validateit import exc


all_classes = [py.All, cy.All]
any_classes = [py.Any, cy.Any]


@pytest.mark.parametrize("class_", all_classes)
def test_all(class_):
    # type: (t.Type[py.All]) -> None
    v = class_(py.Int(min=0), py.Int(max=10))
    assert v(1) == 1

    with pytest.raises(exc.MinValueError) as info:
        v(-1)
    assert info.value.context == [exc.StepNo(0)]
    assert info.value.expected == 0
    assert info.value.actual == -1

    with pytest.raises(exc.MaxValueError) as info:
        v(11)
    assert info.value.context == [exc.StepNo(1)]
    assert info.value.expected == 10
    assert info.value.actual == 11


@pytest.mark.parametrize("class_", any_classes)
def test_any(class_):
    # type: (t.Type[py.Any]) -> None
    v = class_(py.Int(options=[1, 2, 3]), py.Int(min=10))
    assert v(1) == 1
    assert v(2) == 2
    assert v(3) == 3
    assert v(10) == 10

    with pytest.raises(exc.SchemaError) as info:
        v(9)
    assert len(info.value.errors) == 2

    ne_1, ne_2 = info.value.errors

    assert isinstance(ne_1, exc.OptionsError)
    assert ne_1.context == [exc.StepNo(0)]
    assert ne_1.expected == [1, 2, 3]
    assert ne_1.actual == 9

    assert isinstance(ne_2, exc.MinValueError)
    assert ne_2.context == [exc.StepNo(1)]
    assert ne_2.expected == 10
    assert ne_2.actual == 9
