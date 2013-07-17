from ..builder import Builder
from ..builder import def_builder_items
from .common import PartialField
from .common import ScriptField


class FacetBuilder(Builder):
	pass


class HighlightBuilder(Builder):
	pass


class SortBuilder(Builder):
	pass


class SuggestBuilder(Builder):
	pass


class RescoreBuilder(Builder):
	pass


class SearchSourceBuilder(Builder):

	def_builder_items('from', 'size', type=int)
	def_builder_items('timeout_in_millis', type=int, field_name='timeout')
	def_builder_items('min_score', type=float)
	def_builder_items('explain', 'version', 'trackScore', type=bool)
	def_builder_items('fields', type=[basestring])
	def_builder_items('stats', type=[basestring])

	def_builder_items('index_boost', type={basestring: float})

	def_builder_items('highlight', type=HighlightBuilder, auto_create=True)
	def_builder_items('suggest', type=SuggestBuilder, auto_create=True)
	def_builder_items('rescore', type=RescoreBuilder, auto_create=True)

	def_builder_items('query') # QueryBuilder
	def_builder_items('filter') # FilterBuilder
	def_builder_items('facets', type=[FacetBuilder])
	def_builder_items('script_fields', type=[ScriptField])
	def_builder_items('partial_fields', type=[PartialField])
	def_builder_items('sorts', type=[])
