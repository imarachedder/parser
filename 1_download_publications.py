from elibrary_parser.Parsers import AuthorParser
from elibrary_parser.utils import find_common_publications

author_ids = [
    "679517",  # Марков
    "108193",  # Пузырёв
]

# "108193",  # Пузырёв
# "638022"  # Слепцов

publications = []

for author_id in author_ids:
    parser = AuthorParser(
        author_id=author_id,
        data_path="C:/Users/SZ/PycharmProjects/Parser/data/",
        date_from=2016,
        date_to=2017
    )
    # help(AuthorParser)
    parser.find_publications()
    parser.parse_publications()
    parser.save_publications()

    publications.append(set(parser.publications))

common_publications = find_common_publications(publications)
print("Found", len(common_publications), "common publications")

for publication in common_publications:
    print(publication.title)
    print(publication.authors)
    print("-"*20)
