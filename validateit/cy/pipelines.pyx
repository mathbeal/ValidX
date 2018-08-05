from .. import exc
from . cimport abstract


cdef class AllOf(abstract.Validator):
    """
    AND-style Pipeline Validator

    All steps must be succeeded.
    The last step returns result.


    :param Validator \*steps:
        nested validators.

    :raises ValidationError:
        raised by the first failed step.

    :note:
        it uses :class:`validateit.exc.Step` marker to indicate,
        which step is failed.

    """

    __slots__ = ("steps",)

    cdef public steps

    def __init__(self, *steps, **kw):
        assert steps, "At least one validation step has to be provided"
        super(AllOf, self).__init__(steps=list(steps), **kw)

    def __call__(self, value):
        cdef bint validated = False
        for num, step in enumerate(self.steps):
            validated = True
            try:
                value = step(value)
            except exc.ValidationError as e:
                raise e.add_context(exc.Step(num))
        assert validated, "At least one validation step has to be passed"
        return value


cdef class OneOf(abstract.Validator):
    """
    OR-style Pipeline Validator

    The first succeeded step returns result.


    :param Validator \*steps:
        nested validators.

    :raises SchemaError:
        if all steps are failed,
        so it contains all errors,
        raised by each step.

    :note:
        it uses :class:`validateit.exc.Step` marker to indicate,
        which step is failed.

    """

    __slots__ = ("steps",)

    cdef public steps

    def __init__(self, *steps, **kw):
        assert steps, "At least one validation step has to be provided"
        super(OneOf, self).__init__(steps=list(steps), **kw)

    def __call__(self, value):
        errors = []
        for num, step in enumerate(self.steps):
            try:
                return step(value)
            except exc.ValidationError as e:
                errors.extend(ne.add_context(exc.Step(num)) for ne in e)
        if errors:
            raise exc.SchemaError(errors)
        assert False, "At least one validation step has to be passed"
