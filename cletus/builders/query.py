# -*- coding: utf-8 -*-
"""
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
from .filter import FilterBuilder


class QueryBuilder(NamedBuilder):
	pass


class SpanQueryBuilder(QueryBuilder):
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
		super(CommonTermsQueryBuilder, self).__init__()
		self._name = name
		self._text = text

	def_builder_items('name', 'analyzer', type=basestring)
	def_builder_items('text')
	def_builder_items('cutoff_frequency', type=float)
	def_builder_items('high_freq_operator', 'low_freq_operator', type=Operator)


class ConstantScoreQueryBuilder(BoostableQueryBuilder):
	NAME = 'constant_score'

	def __init__(self, *args, **kwargs):
		super(ConstantScoreQueryBuilder, self).__init__()
		query, filter = None, None
		if args:
			if len(args) == 1:
				[arg] = args
				if isinstance(arg, FilterBuilder):
					filter = arg
				else:
					query = arg
			else:
				query, filter = args
		if kwargs:
			query = kwargs.pop('query', query)
			filter = kwargs.pop('filter', filter)
			if kwargs:
				raise TypeError(kwargs.keys())
		self._query, self._filter = query, filter

	def_builder_items('query', type=QueryBuilder)
	def_builder_items('filter', type=FilterBuilder)


class CustomBoostFactorQueryBuilder(BoostableQueryBuilder):
	NAME = 'custom_boost_factor'

	def __init__(self, query):
		super(ConstantScoreQueryBuilder, self).__init__()
		self._query = query

	def_builder_items('query', type=QueryBuilder)


class TermsQueryBuilder(BoostableQueryBuilder):
	NAME = 'terms'

	def __init__(self, name, *values):
		super(TermsQueryBuilder, self).__init__()
		self._name = name
		self._values = list(values)

	def_builder_items('disable_coord', type=bool)
	def_builder_items('minimum_should_match', type=basestring)

	def write_body(self, builder, params=None):
		builder.start_array(self._name)
		for value in getattr(self, '_values', ()):
			builder.value(value)
		builder.end_array()


class CustomFiltersScoreQueryBuilder(BoostableQueryBuilder):
	NAME = 'custom_filters_score'

	def __init__(self, query):
		super(CustomFiltersScoreQueryBuilder, self).__init__()
		self._query = query

	def_builder_items('params', type={basestring: object})
	def_builder_items('query', type=QueryBuilder)
	def_builder_items('boosts', type=[float])
	def_builder_items('filters', type=[FilterBuilder])
	def_builder_items('max_boost', type=float)
	def_builder_items('scripts', type=[basestring])
	def_builder_items('lang', 'score_mode', type=basestring)


class CustomScoreQueryBuilder(QueryBuilder):
	NAME = 'custom_boost_factor'

	def __init__(self, query):
		super(CustomScoreQueryBuilder, self).__init__()
		self._query = query

	def_builder_items('query', type=QueryBuilder)
	def_builder_items('boost_factor', type=float)


class DisMaxQueryBuilder(BoostableQueryBuilder):
	NAME = 'dis_max'

	def __init__(self, *queries):
		super(DisMaxQueryBuilder, self).__init__()
		self._queries = list(queries)

	def_builder_items('queries', type=[QueryBuilder])
	def_builder_items('tie_breaker', type=float)


class FieldMaskingSpanQueryBuilder(SpanQueryBuilder):
	NAME = 'field_masking_span'

	def __init__(self, query, field):
		super(FieldMaskingSpanQueryBuilder, self).__init__()
		self._query = query
		self._field = field

	def_builder_items('query', type=QueryBuilder)
	def_builder_items('field', type=basestring)


class MatchAllQueryBuilder(BoostingQueryBuilder):
	NAME = 'match_all'


class MatchQueryBuilder(BoostableQueryBuilder):
	NAME = 'match'

	Operator = enum('OR', 'AND')
	Type = enum('BOOLEAN', 'PHRASE', 'PHRASE_PREFIX')
	ZeroTermsQuery = enum('NONE', 'ALL')

	def __init__(self, name, text):
		super(MatchQueryBuilder, self).__init__()
		self._name = name
		self._text = text

	def_builder_items('cutoff_frequency', type=float)
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
