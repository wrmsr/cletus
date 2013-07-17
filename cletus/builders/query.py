"""
BaseQueryBuilder
CommonTermsQueryBuilder
ConstantScoreQueryBuilder
CustomBoostFactorQueryBuilder
CustomFiltersScoreQueryBuilder
CustomScoreQueryBuilder
DisMaxQueryBuilder
FieldMaskingSpanQueryBuilder
FieldQueryBuilder
FilteredQueryBuilder
FuzzyLikeThisFieldQueryBuilder
FuzzyLikeThisQueryBuilder
FuzzyQueryBuilder
GeoShapeQueryBuilder
HasChildQueryBuilder
HasParentQueryBuilder
IdsQueryBuilder
IndicesQueryBuilder
MatchAllQueryBuilder
MatchQueryBuilder
MoreLikeThisFieldQueryBuilder
MoreLikeThisQueryBuilder
MultiMatchQueryBuilder
MultiTermQueryBuilder
NestedQueryBuilder
PrefixQueryBuilder
QueryBuilder
QueryBuilders
QueryFilterBuilder
QueryStringQueryBuilder
RangeQueryBuilder
RegexpQueryBuilder
SpanFirstQueryBuilder
SpanMultiTermQueryBuilder
SpanNearQueryBuilder
SpanNotQueryBuilder
SpanOrQueryBuilder
SpanQueryBuilder
SpanTermQueryBuilder
TermQueryBuilder
TermsQueryBuilder
TopChildrenQueryBuilder
WildcardQueryBuilder
WrapperQueryBuilder
"""

from ..builder import NamedBuilder
from ..builder import def_builder_items
from ..common import enum


class QueryBuilder(NamedBuilder):
	pass


class BoostableQueryBuilder(QueryBuilder):

	def_builder_items('boost', type=float)


class CoordinatingQueryBuilder(BoostableQueryBuilder):

	def_builder_items('minimum_should_match', type=basestring)
	def_builder_items('disable_coord', type=bool)
	
	
class BoolQueryBuilder(CoordinatingQueryBuilder):
	NAME = 'bool'

	def_builder_items('must', 'must_not', 'should', type=[QueryBuilder])


class BoostingQueryBuilder(BoostableQueryBuilder):
	NAME = 'boosting'

	def_builder_items('negative_query', 'positive_query', type=QueryBuilder)
	def_builder_items('negative_boost', type=float)


class CommonTermsQueryBuilder(CoordinatingQueryBuilder):
	NAME = 'common'

	Operator = enum('OR', 'AND')

	def __init__(self, name, text):
		self._name = name
		self._text = text

	def_builder_items('analyzer', type=basestring)
	def_builder_items('cutoff_frequency', type=float)
	def_builder_items('high_freq_operator', 'low_freq_operator', type=Operator)


class TermsQueryBuilder(BoostableQueryBuilder):
	NAME = 'terms'

	def __init__(self, name, *values):
		super(TermsQueryBuilder, self).__init__()
		self._name = name
		self._values = list(values)

	def_builder_items('disable_coord', type=bool)
	def_builder_items('minimum_should_match', type=basestring)

	def write_body_xcontent(self, builder, params=None):
		builder.start_array(self._name)
		for value in getattr(self, '_values', ()):
			builder.value(value)
		builder.end_array()


class MatchAllQueryBuilder(QueryBuilder):
	NAME = 'match_all'


class MatchQueryBuilder(QueryBuilder):
	NAME = 'match'

	Operator = enum('OR', 'AND')
	Type = enum('BOOLEAN', 'PHRASE', 'PHRASE_PREFIX')
	ZeroTermsQuery = enum('NONE', 'ALL')

	def __init__(self, name, text):
		self._name = name
		self._text = text

	def_builder_items('boost', 'cutoff_frequency', type=float)
	def_builder_items('slop', 'prefix_length', 'max_expansions', type=int)
	def_builder_items(
		'analyzer',
		'fuzziness',
		'minimum_should_match',
		'rewrite',
		'fuzzy_rewrite',
		'operator',
		'zero_terms_query',
		type=basestring)
	def_builder_items('type', type=basestring, formatter=lambda s: s.lower())
	def_builder_items('lenient', 'fuzzy_transpositions', type=bool)

	def write_xcontent(self, builder, params=None):
		builder.start_object(self.NAME)
		builder.start_object(self._name)
		builder.field('query', self._text)
		super(MatchQueryBuilder, self).write_xcontent(builder, params)
		builder.end_object()
		builder.end_object()
