from elibrary_parser.Parsers import AuthorParser
from elibrary_parser.utils import find_common_publications
from elibrary_parser.graphs import PublicationVisualizer
from pathlib import Path
# Ложников П.С. id 159775

# БРОВИНА АННА ВИКТОРОВНА * 731081

author_ids = ["731081"]
publications = []
data_path = "/Users/imarachedder/Desktop/omgtu/проект/Parser/data"
date_from = 2004
date_to = 2024

for author_id in author_ids:
    parser = AuthorParser(
        author_id=author_id,
        data_path=data_path,
        date_from=date_from, 
        date_to=date_to 
    )

    # parser.find_publications()  # Загрузка HTML-файлов с публикациями
    parser.parse_publications()  # Извлечение информации из HTML-файлов
    parser.save_publications_to_csv()  # Сохранение информации в CSV-файл

    publications.append(set(parser.publications))

# Поиск общих публикаций коллектива авторов
common_publications = find_common_publications(publications)
print("Найдено", len(common_publications), "общих публикаций")

# Вывод названия и авторов общих публикаций
for publication in common_publications:
    print(publication.title)
    print(publication.authors)
    print("-" * 20)

data_path = Path(data_path)
data_path = data_path / "processed" / author_ids[0]
visualizer = PublicationVisualizer(data_path)
visualizer.save_year_distribution("publication_years.jpeg")
