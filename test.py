from cletus import *


def main():
	import pprint
	pprint.pprint(SearchSourceBuilder().timeout_in_millis(5).fields(['_id']).sorts([1,2,3]).to_simple())
	pprint.pprint(PartialField().name('something').includes(['a', 'b']).to_simple())
	pprint.pprint(
		BoolQueryBuilder()
		.minimumShouldMatch(3)
		.should([
			TermsQueryBuilder('x', 1, 2, 3),
			TermsQueryBuilder('x', 4, 5, 6),
			MatchQueryBuilder('thing', 'foo').type(MatchQueryBuilder.Type.PHRASE),
			MatchAllQueryBuilder(),
		])
		.to_simple())

if __name__ == '__main__':
	main()
