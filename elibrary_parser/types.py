import re


class Publication:
    """
    Хранение информации о публикациях

    Находит сходства между указанными авторами

    Атрибуты
    ----------
        title: str
        название публикации
        authors: str
        авторы публикации
        info: str
        информация о публикации
        link: str
        ссылка на публикацию
        year: default None, else int
    """

    def __init__(self, title: str, authors: str, info: str, link: str, year = None):
        self.title = title
        self.authors = authors
        self.info = info
        self.link = link
        self.year = year
    missing_value = '-'

    def to_csv_row(self):
        """
        Создание колонок с ; 
        """

        return self.title + ';' + self.authors + ';' + self.info + ';' + self.link + ';' + self.year

    def get_year(self):
        """ 
        Получаем год публикации с 1900 по 2100
        """

        # years = re.findall(r'20\d{2}|19\d{2}', self.info)
        years = re.findall(r'\b(19\d{2}|20\d{2})\b(?=\.)', self.title)

        print("YEARS")
        print(years)
        if years:
            self.year = years[0]
        else:
            self.year = Publication.missing_value

    def __eq__(self, other) -> bool:
        """ 
        Выводит любые похожие публикации авторов,
        если их авторы, название, информация, ссылка и год совпадают

        Параметры:
        -----------
        other : другая информация для сравнения
        """

        return (
                self.title == other.title
                and self.authors == other.authors
                and self.info == other.info
                and self.link == other.link
                and self.year == other.year
        )

    def __hash__(self):
        """
        хэширование публикации
        """

        return hash(self.title) ^ hash(self.authors) ^ hash(self.info) ^ hash(self.link) ^ hash(self.year)
