from cletus import *


def main():
	print(SearchSourceBuilder().timeout_in_millis(5).fields(['_id']).sorts([1,2,3]))
	print(PartialField().name('something').includes(['a', 'b']))
	print(
		BoolQueryBuilder()
		.minimumShouldMatch(3)
		.should([
			TermsQueryBuilder('x', 1, 2, 3),
			TermsQueryBuilder('x', 4, 5, 6),
			MatchQueryBuilder('thing', 'foo').type(MatchQueryBuilder.Type.PHRASE),
			MatchAllQueryBuilder(),
			ConstantScoreQueryBuilder(query=MatchAllQueryBuilder(), special=True),
			{'literal_thing': True},
		]))

if __name__ == '__main__':
	main()
