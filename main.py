from elibrary_parser.Parsers import AuthorParser
from elibrary_parser.utils import find_common_publications
import os

# Ложников П.С. 159775

author_ids = ["1"]
publications = []

for author_id in author_ids:
    parser = AuthorParser(
        author_id=author_id,
        data_path=os.path.join("data"),
        date_from=2000,
        date_to=2021 
    )

    parser.find_publications()  # Загрузка HTML-файлов с публикациями
    parser.parse_publications()  # Извлечение информации из HTML-файлов
    parser.save_publications()  # Сохранение информации в CSV-файл

    publications.append(set(parser.publications))

# Поиск общих публикаций коллектива авторов
common_publications = find_common_publications(publications)
print("Found", len(common_publications), "common publications")

# Вывод названия и авторов общих публикаций
for publication in common_publications:
    print(publication.title)
    print(publication.authors)
    print("-" * 20)
