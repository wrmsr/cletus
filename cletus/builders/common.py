from ..builder import Builder
from ..builder import def_builder_items


class ScriptField(Builder):

	def_builder_items('field_name', 'script', 'lang', type=basestring)

class PartialField(Builder):

	def_builder_items('name', type=basestring)
	def_builder_items('includes', 'excludes', type=[basestring])
