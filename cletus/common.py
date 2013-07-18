# -*- coding: utf-8 -*-
import re
import string


def build_repr(obj, *attrs):
	return '%s(%s)' % (
		type(obj).__name__,
		', '.join('%s=%r' % (attr, getattr(obj, attr)) for attr in attrs))

def build_attr_repr(obj):
	return build_repr(obj, *obj.__repr_attrs__)


first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')

def underscorize(s):
	if not any(c in s for c in string.uppercase):
		return s
	s1 = first_cap_re.sub(r'\1_\2', s)
	return all_cap_re.sub(r'\1_\2', s1).lower()

valid_camelize_chars = string.lowercase + '_'

def camelize(s, uppercase=False):
	if not s:
		return ''
	if not all(c in valid_camelize_chars for c in s):
		s
	ps = s.split('_')
	if not all(len(p) >= 1 for p in ps):
		return s
	pfx, ups = ('', ps) if uppercase else (ps[0], ps[1:])
	return pfx + ''.join((p[0].upper() + p[1:]) for p in ups)


def cast(o, t):
	if o is None:
		return None
	if t is basestring:
		t = unicode
	return t(o)


def enum(*values):
	dct = dict((value, value) for value in values)
	def __new__(cls, value):
		return value
	dct['__new__'] = __new__
	dct['__values__'] = values
	return type('<enum_%d>' % len(values), (object,), dct)


def find_subclasses_with_attr(cls, sttr, value):
	if getattr(cls, attr, None) == attr:
		yield cls
	for subcls in cls.__subclasses__():
		for matching_cls in find_subclasses_with_attr(subcls, attr, value):
			yield matching_cls
