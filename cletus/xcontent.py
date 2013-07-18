# -*- coding: utf-8 -*-
import abc


class ToXContent(object):
	__metaclass__ = abc.ABCMeta

	@abc.abstractmethod
	def to_xcontent(self, builder, params=None):
		raise NotImplementedError()


class WriteXContent(object):
	__metaclass__ = abc.ABCMeta

	@abc.abstractmethod
	def write_xcontent(self, builder, params=None):
		raise NotImplementedError()


class XContentBuilder(object):
	__metaclass__ = abc.ABCMeta

	@abc.abstractmethod
	def start_object(self, *args):
		raise NotImplementedError()

	@abc.abstractmethod
	def field(self, name, value):
		raise NotImplementedError()

	@abc.abstractmethod
	def end_object(self):
		raise NotImplementedError()

	@abc.abstractmethod
	def start_array(self, *args):
		raise NotImplementedError()

	@abc.abstractmethod
	def value(self, value):
		raise NotImplementedError()

	@abc.abstractmethod
	def end_array(self):
		raise NotImplementedError()


class SimpleXContentBuilder(XContentBuilder):

	def __init__(self):
		self._items = [[]]

	def start_object(self, *args):
		dct = {}
		if args:
			[name] = args
			self._items[-1][name] = dct
		else:
			self._items[-1].append(dct)
		self._items.append(dct)
		return self

	def field(self, name, value):
		self._items[-1][name] = to_simple(value)
		return self

	def end_object(self):
		if len(self._items) < 2 or not isinstance(self._items.pop(), dict):
			raise TypeError()
		return self

	def start_array(self, *args):
		lst = []
		if args:
			[name] = args
			self._items[-1][name] = lst
		else:
			self._items[-1].append(lst)
		self._items.append(lst)
		return self

	def value(self, value):
		self._items[-1].append(to_simple(value))
		return self

	def end_array(self):
		if len(self._items) < 2 or not isinstance(self._items.pop(), list):
			raise TypeError()
		return self

	def build(self):
		if len(self._items) != 1 or len(self._items[0]) != 1:
			raise TypeError()
		return self._items[0][0]


def to_simple(value, params=None):
	if not isinstance(value, ToXContent):
		return value
	builder = SimpleXContentBuilder()
	value.to_xcontent(builder, params)
	return builder.build()
