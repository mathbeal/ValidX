from libc cimport limits
import re

from .. import exc
from . cimport abstract


cdef class Str(abstract.Validator):
    """
    Unicode String Validator


    :param bool nullable:
        accept ``None`` as a valid value.

    :param str encoding:
        try to decode byte-string to ``str/unicode``,
        using specified encoding.

    :param int minlen:
        lower length limit.

    :param int maxlen:
        upper length limit.

    :param str pattern:
        validate string using regular expression.

    :param options:
        explicit enumeration of valid values.
    :type options: list or tuple


    :raises InvalidTypeError:
        * if ``value is None`` and ``not self.nullable``;
        * if ``not isinstance(value, str)`` (Python 3.x)
          or ``not isinstance(value, unicode)`` (Python 2.x).

    :raises StrDecodeError:
        if ``value.decode(self.encoding)`` raises ``UnicodeDecodeError``.

    :raises MinLengthError:
        if ``len(value) < self.minlen``.

    :raises MaxLengthError:
        if ``len(value) > self.maxlen``.

    :raises PatternMatchError:
        if ``value`` does not match ``self.pattern``.

    :raises OptionsError:
        if ``value not in self.options``.

    """

    __slots__ = ("nullable", "encoding", "minlen", "maxlen", "pattern", "options")

    cdef public bint nullable
    cdef public str encoding
    cdef long _minlen
    cdef long _maxlen
    cdef public pattern
    cdef public options

    @property
    def minlen(self):
        return None if self._minlen == 0 else self._minlen

    @minlen.setter
    def minlen(self, value):
        self._minlen = value if value is not None else 0

    @property
    def maxlen(self):
        return None if self._maxlen == limits.LONG_MAX else self._maxlen

    @maxlen.setter
    def maxlen(self, value):
        self._maxlen = value if value is not None else limits.LONG_MAX

    def __call__(self, value):
        if value is None and self.nullable:
            return value
        if not isinstance(value, unicode):
            if isinstance(value, bytes) and self.encoding is not None:
                try:
                    value = value.decode(self.encoding)
                except UnicodeDecodeError:
                    raise exc.StrDecodeError(expected=self.encoding, actual=value)
            else:
                raise exc.InvalidTypeError(expected=unicode, actual=type(value))
        cdef long length = len(value)
        if length < self._minlen:
            raise exc.MinLengthError(expected=self.minlen, actual=length)
        if length > self._maxlen:
            raise exc.MaxLengthError(expected=self.maxlen, actual=length)
        if self.pattern and not re.match(self.pattern, value):
            raise exc.PatternMatchError(expected=self.pattern, actual=value)
        if self.options is not None and value not in self.options:
            raise exc.OptionsError(expected=self.options, actual=value)
        return value


cdef class Bytes(abstract.Validator):
    """
    Byte String Validator


    :param bool nullable:
        accept ``None`` as a valid value.

    :param int minlen:
        lower length limit.

    :param int maxlen:
        upper length limit.


    :raises InvalidTypeError:
        * if ``value is None`` and ``not self.nullable``;
        * if ``not isinstance(value, bytes)``.

    :raises MinLengthError:
        if ``len(value) < self.minlen``.

    :raises MaxLengthError:
        if ``len(value) > self.maxlen``.

    """

    __slots__ = ("nullable", "minlen", "maxlen")

    cdef public nullable
    cdef long _minlen
    cdef long _maxlen

    @property
    def minlen(self):
        return None if self._minlen == 0 else self._minlen

    @minlen.setter
    def minlen(self, value):
        self._minlen = value if value is not None else 0

    @property
    def maxlen(self):
        return None if self._maxlen == limits.LONG_MAX else self._maxlen

    @maxlen.setter
    def maxlen(self, value):
        self._maxlen = value if value is not None else limits.LONG_MAX

    def __call__(self, value):
        if value is None and self.nullable:
            return value
        if not isinstance(value, bytes):
            raise exc.InvalidTypeError(expected=bytes, actual=type(value))
        cdef long length = len(value)
        if length < self._minlen:
            raise exc.MinLengthError(expected=self.minlen, actual=length)
        if length > self._maxlen:
            raise exc.MaxLengthError(expected=self.maxlen, actual=length)
        return value