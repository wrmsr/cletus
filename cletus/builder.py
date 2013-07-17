import abc
import sys

from .common import build_attr_repr
from .common import camelize
from .common import cast
from .common import underscorize
from .xcontent import SimpleXContentBuilder
from .xcontent import ToXContent
from .xcontent import WriteXContent


builder_items_attr = '__builder_items__'


class no_default(object):
	def __init__(self):
		raise NotImplementedError()


class BuilderItem(object):
	__metaclass__ = abc.ABCMeta

	def __init__(
		self,
		name,
		camel_name=None,
		underscore_name=None,
		attr_name=None,
		field_name=None,
		default=no_default,
		silent=False,
		formatter=None
	):
		super(BuilderItem, self).__init__()
		self._name = name
		self._camel_name = camel_name if camel_name is not None else camelize(self.name)
		self._underscore_name = underscore_name if underscore_name is not None else underscorize(self.name)
		self._attr_name = attr_name if attr_name is not None else ('_' + self.underscore_name)
		self._field_name = field_name if field_name is not None else self.name
		self._default = default
		self._silent = silent
		self._formatter = formatter

	name = property(lambda self: self._name)
	camel_name = property(lambda self: self._camel_name)
	underscore_name = property(lambda self: self._underscore_name)
	attr_name = property(lambda self: self._attr_name)
	field_name = property(lambda self: self._field_name)
	default = property(lambda self: self._default)
	silent = property(lambda self: self._silent)
	formatter = property(lambda self: self._formatter)

	__repr__ = build_attr_repr
	__repr_attrs__ = property(lambda self: (
		'name',
		'camel_name',
		'underscore_name',
		'attr_name',
		'field_name',
		'default',
		'silent',
		'formatter',
	))

	def get(self, obj, value):
		return getattr(obj, self.attr_name, value)

	@abc.abstractmethod
	def set(self, obj, *args, **kwargs):
		raise NotImplementedError()

	@abc.abstractmethod
	def write(self, obj, builder, params=None):
		raise NotImplementedError()

	def install(self, cls_dct):
		cls_builder_items = cls_dct.setdefault(builder_items_attr, [])
		if self in cls_builder_items:
			raise ValueError(self)
		for name in (self.name, self.camel_name, self.underscore_name, self.attr_name):
			if name in cls_dct:
				raise NameError(name)
		if self.default is not no_default:
			cls_dct[self.attr_name] = self.default
		cls_dct[self.name] = cls_dct[self.camel_name] = cls_dct[self.underscore_name] = \
			lambda *args, **kwargs: self.set(*args, **kwargs)
		cls_builder_items.append(self)

	@classmethod
	def new(cls, name, **kwargs):
		type = kwargs.pop('type', None)
		if type is not None:
			if isinstance(type, list):
				[item_type] = type or [None]
				if item_type is not None and issubclass(item_type, Builder):
					return ChildrenBuilderItem(name, builder_type=type, **kwargs)
				return ListBuilderItem(name, item_type=item_type, **kwargs)
			if isinstance(type, dict):
				[[key_type, value_type]] = (type or {None: None}).items()
				return DictBuilderItem(name, key_type=key_type, value_type=value_type, **kwargs)
			if issubclass(type, Builder):
				return ChildBuilderItem(name, builder_type=type, **kwargs)
		return SimpleBuilderItem(name, type=type, **kwargs)


class SimpleBuilderItem(BuilderItem):

	def __init__(self, name, type=None, **kwargs):
		super(SimpleBuilderItem, self).__init__(name, **kwargs)
		self._type = type

	type = property(lambda self: self._type)

	__repr_attrs__ = property(lambda self: super(SimpleBuilderItem, self).__repr_attrs__ + (
		'type',
	))

	def set(self, obj, value):
		if self.type is not None and not isinstance(value, self.type):
			value = cast(value, self.type)
		setattr(obj, self.attr_name, value)
		return obj

	def write(self, obj, builder, params=None):
		if hasattr(obj, self.attr_name):
			value = getattr(obj, self.attr_name)
			if self.formatter is not None:
				value = self.formatter(value)
			builder.field(self.field_name, value)


class ListBuilderItem(BuilderItem):

	def __init__(self, name, item_type=None, **kwargs):
		super(ListBuilderItem, self).__init__(name, **kwargs)
		self._item_type = item_type

	item_type = property(lambda self: self._item_type)

	__repr_attrs__ = property(lambda self: super(ListBuilderItem, self).__repr_attrs__ + (
		'item_type',
	))

	def set(self, obj, value):
		lst = []
		for item in value:
			if self.item_type is not None and not isinstance(item, self.item_type):
				item = cast(item, self.item_type)
			lst.append(item)
		setattr(obj, self.attr_name, lst)
		return obj

	def write(self, obj, builder, params=None):
		if hasattr(obj, self.attr_name):
			builder.start_array(self.field_name)
			for item in getattr(obj, self.attr_name):
				builder.value(item)
			builder.end_array()


class DictBuilderItem(BuilderItem):

	def __init__(self, name, key_type=None, value_type=None, **kwargs):
		super(DictBuilderItem, self).__init__(name, **kwargs)
		self._key_type = key_type
		self._value_type = value_type

	key_type = property(lambda self: self._key_type)
	value_type = property(lambda self: self._value_type)

	__repr_attrs__ = property(lambda self: super(DictBuilderItem, self).__repr_attrs__ + (
		'key_type',
		'value_type',
	))

	def set(self, obj, value):
		dct = {}
		for k, v in value.iteritems():
			if self.key_type is not None and not isinstance(k, self.key_type):
				k = cast(k, self.key_type)
			if self.value_type is not None and not isinstance(k, self.value_type):
				v = cast(v, self.value_type)
			dct[k] = v
		setattr(obj, self.attr_name, dct)
		return obj

	def write(self, obj, builder, params=None):
		if hasattr(obj, self.attr_name):
			builder.start_object(self.field_name)
			for k, v in getattr(obj, self.attr_name).iteritems():
				builder.field(k, v)
			builder.end_object()


class ChildBuilderItem(BuilderItem):

	def __init__(self, name, builder_type=None, auto_create=False, **kwargs):
		if builder_type is None:
			raise ValueError(builder_type)
		super(ChildBuilderItem, self).__init__(name, **kwargs)
		self._builder_type = builder_type
		self._auto_create = auto_create

	builder_type = property(lambda self: self._builder_type)
	auto_create = property(lambda self: self._auto_create)

	__repr_attrs__ = property(lambda self: super(ChildBuilderItem, self).__repr_attrs__ + (
		'builder_type',
		'auto_create',
	))

	def set(self, obj, *args):
		if not args:
			if not hasattr(obj, self.attr_name) and self.auto_create:
				setattr(obj, self.attr_name, self.builder_type())
		else:
			[value] = args
			setattr(obj, self.attr_name, value)
		return getattr(obj, self.attr_name)

	def write(self, obj, builder, params=None):
		if hasattr(obj, self.attr_name):
			builder.start_object(self.field_name)
			getattr(obj, self.attr_name).write_xcontent(builder, params)
			builder.end_object()


class ChildrenBuilderItem(BuilderItem):

	def __init__(self, name, builder_type=None, **kwargs):
		if builder_type is None:
			raise ValueError(builder_type)
		super(ChildrenBuilderItem, self).__init__(name, **kwargs)
		self._builder_type = builder_type

	builder_type = property(lambda self: self._builder_type)

	__repr_attrs__ = property(lambda self: super(ChildrenBuilderItem, self).__repr_attrs__ + (
		'builder_type',
	))

	def set(self, obj, value):
		setattr(obj, self.attr_name, list(value))
		return obj

	def write(self, obj, builder, params=None):
		if hasattr(obj, self.attr_name):
			builder.start_array(self.field_name)
			for item in getattr(obj, self.attr_name):
				builder.start_object()
				item.write_xcontent(builder, params)
				builder.end_object()
			builder.end_array()


def def_builder_item(name, **kwargs):
	cls_dct = kwargs.pop('cls_dct', None)
	if cls_dct is None:
		cls_dct = sys._getframe(1).f_locals
	builder_item = BuilderItem.new(name, **kwargs)
	builder_item.install(cls_dct)
	return builder_item

def def_builder_items(*names, **kwargs):
	cls_dct = kwargs.pop('cls_dct', None)
	if cls_dct is None:
		cls_dct = sys._getframe(1).f_locals
	for name in names:
		def_builder_item(name, cls_dct=cls_dct, **kwargs)

def write_builder_items(obj, builder, params=None):
	for cls in type(obj).__mro__:
		builder_items = cls.__dict__.get(builder_items_attr, [])
		for builder_item in builder_items:
			if not builder_item.silent:
				builder_item.write(obj, builder, params)
	return builder


class Builder(WriteXContent, ToXContent):

	def write_xcontent(self, builder, params=None):
		write_builder_items(self, builder, params)

	def to_xcontent(self, builder, params=None):
		builder.start_object()
		self.write_xcontent(builder, params)
		builder.end_object()
		return builder

	def to_simple(self, params=None):
		return self.to_xcontent(SimpleXContentBuilder()).build()

class NamedBuilder(Builder):

	NAME = None

	def write_body(self, builder, params=None):
		pass

	def write_xcontent(self, builder, params=None):
		if self.NAME is None:
			raise NameError(self.NAME)
		builder.start_object(self.NAME)
		self.write_body(builder, params)
		write_builder_items(self, builder, params)
		builder.end_object()
