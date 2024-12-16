import csv
from pathlib import Path
import random
import time
import bs4
import pandas as pd
import re

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from elibrary_parser import config
from elibrary_parser.types import Publication


class AuthorParser:
    """
    Класс для загрузки и обработки публикация с интернет ресурса eLibrary по авторам

     Attributes
     Атрибуты
     -----------
     driver: WebDriver
        firefox веб драйвер
        Set by method: setup_webdriver

     publications: lst
        Список с информацией по кажлдому автору
        Set by method: save_publications

     author_id: str
        айди автора

     data_path: Path
        путь куда загружаются все данные

     date_to, date_from: int

        период год по которым необходимо произвести парсинг
     """
    USER_AGENTS = (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML,like Gecko) Iron/28.0.1550.1 Chrome/28.0.1550.1',
        'Opera/9.80 (Windows NT 6.1; WOW64) Presto/2.12.388 Version/12.16',
    )
    DRIVER_PATH = config.DRIVER_PATH

    def __init__(self, author_id, data_path, date_to, date_from):

        self.author_id = author_id
        self.driver = None
        self.files_dir = None
        self.publications = []
        self.data_path = Path(data_path)
        self.date_to = date_to
        self.date_from = date_from

        self.create_files_dir()
        self.setup_webdriver()

    missing_value = '-'

    def setup_webdriver(self):
        """Settings for a selenium web driver
        Changes a self.driver attribute
        Настроки для веб драйвера selenium 
        """
        

        new_useragent = random.choice(self.USER_AGENTS)

        profile = webdriver.FirefoxProfile()
        profile.set_preference("general.useragent.override", new_useragent)
        options = Options()
        options.headless = True

        self.driver = webdriver.Firefox(profile, executable_path=self.DRIVER_PATH, options=options)

    def create_files_dir(self):
        """Creates directory for the web-pages of an specific author
        Созданные директори для для страничек с айди автора
        """
        raw_data_dir = self.data_path / "raw"
        raw_data_dir.mkdir(exist_ok=True)

        processed_data_dir = self.data_path / "processed"
        processed_data_dir.mkdir(exist_ok=True)

        self.files_dir = self.data_path / "raw" / self.author_id

        print("Директория автора: ", self.files_dir.absolute())

        self.files_dir.mkdir(exist_ok=True)

    def find_publications(self):
        """
        Gets the web-page with chosen years
        Поиск страниц с выбранной датой
        """

        author_page_url = f'https://www.elibrary.ru/author_items.asp?authorid={self.author_id}'
        print("URL страницы автора:", author_page_url)

        print("Получаем список страниц по автору")
        self.driver.get(author_page_url)
        print("Выполнено успешно")

        self.driver.find_element_by_xpath('//*[@id="hdr_years"]').click()
        time.sleep(20)

        for i in range(self.date_from, self.date_to+1):
            try:
                year = '//*[@id="year_' + str(i) + '"]'
                element = WebDriverWait(self.driver, 1).until(EC.element_to_be_clickable((By.XPATH, year)))
                self.driver.execute_script("arguments[0].click();", element)
                print('Года:', i)
            except TimeoutException:
                print("Невозможно загрузить выбор года")
                print('Нет публикаций для:' + str(i) + 'года')
            except NoSuchElementException:
                print('Нет публикаций для:' + str(i) + 'года')

        # кнопка поиска по году
        self.driver.find_element_by_xpath('//td[6]/div').click()  # TODO: remove hardcoded index

        page_number = 1
        is_page_real = True

        while is_page_real:
            with open(self.files_dir / f"page_{page_number}.html", 'a', encoding='utf-8') as f:
                f.write(self.driver.page_source)

            print("Загрузка страницы под номером: ", page_number)
            page_number += 1
            
            try:
                self.driver.find_element_by_link_text('Следующая страница').click()
            except NoSuchElementException:
                is_page_real = False
                print('Все страницы загружены, страниц больше нет')

            sleep_seconds = random.randint(5, 15)
            print("Ожидание", sleep_seconds, "секунд")

            time.sleep(sleep_seconds)


    @staticmethod
    def get_title(table_cell: bs4.element.ResultSet) -> str:
        """
        Возвращаем названия из HTML - документа

        Parameters:
        Параметры:
        -----------
        table_cell : bs4.element.ResultSet
        """

        title = table_cell.find_all('span', style="line-height:1.0;")

        if not title:
            title = AuthorParser.missing_value
        else:
            title = title[0].text

        return title

    @staticmethod
    def get_authors(table_cell: bs4.element.ResultSet) -> str:
        """
        Возрвращаем авторов с загруженной страниц
        """

        box_of_authors = table_cell.find_all('font', color="#00008f")
        if not box_of_authors:
            authors = AuthorParser.missing_value
        else:
            authors = box_of_authors[0].find_all('i')
            if not authors:
                authors = AuthorParser.missing_value
            else:
                authors = authors[0].text

        return authors

    @staticmethod
    def get_info(table_cell: bs4.element.ResultSet) -> str:
        """
        Возращаем информацию о публикации с загруженной страницы
        """

        if len(table_cell) == 0:
            biblio_info = AuthorParser.missing_value
        else:
            biblio_info = list(table_cell.children)[-1]
            biblio_info = biblio_info.text.strip()
            biblio_info = biblio_info.replace('\xa0', ' ')
            biblio_info = biblio_info.replace('\r\n', ' ')
            biblio_info = biblio_info.replace('\n', ' ')

        return biblio_info

    @staticmethod
    def get_link(table_cell: bs4.element.ResultSet) -> str:
        """
        Возвращаем артикль с загруженной странцы
        """

        information_wint_links_in_box = table_cell.find_all('a')
        if not information_wint_links_in_box:
            paper_link = AuthorParser.missing_value
        else:
            title_information_with_link = information_wint_links_in_box[0]
            link = title_information_with_link.get('href')
            # TODO: проверить, всегда ли это бумажная ссылка
            paper_link = 'https://www.elibrary.ru/' + link 

        return paper_link

    @staticmethod
    def create_table_cells(soup):
        publications_table = soup.find_all('table', id="restab")[0]

        rubbish = publications_table.find_all('table', width="100%", cellspacing="0")
        for box in rubbish:
            # Удалить все внутренние теги
            box.decompose() 

        table_cells = publications_table.find_all('td', align="left", valign="top")

        return table_cells

    @staticmethod
    def get_year(table_cell: bs4.element.ResultSet):
        """ 
        Получаем год публикации с 1900 по 2100
        из текста
        """
        # преобразуем содержимое ячейки в текст
        cell_text = table_cell.get_text(strip=True) if hasattr(table_cell, "get_text") else str(table_cell)

        # years = re.findall(r'20\d{2}|19\d{2}', self.info) cтарая реализация, не работает
        # years = re.findall(r'\b(19\d{2}|20\d{2})', cell_text)
        years = re.findall(r'20\d{2}|19\d{2}', cell_text)

        return years[0] if years else "-"

    def save_publications_to_csv(self):
        """
        Функция сохраняет список публикаций в csv-файл через pandas
        """
        data = [
            {
                "Название": pub.title,
                "Авторы": pub.authors,
                "Информация": pub.info,
                "Ссылка": pub.link,
                "Год публикации": pub.year,
            }
            for pub in self.publications
        ]
        save_path = self.data_path / "processed" / self.author_id
        save_path.mkdir(exist_ok=True)

        csv_path = save_path / "publications2.csv"
        df = pd.DataFrame(data)
        df.to_csv(csv_path, sep=";", index=False)

        print("Публикации сохранены в csv-файл")

    def save_publications(self):
        """
        Сохраняем автором публикаций в csv - файл
        """

        save_path = self.data_path / "processed" / self.author_id
        save_path.mkdir(exist_ok=True)

        csv_path = save_path / "publications.csv"

        with open(csv_path, 'a', encoding="utf8", newline='') as csvfile:
            wr = csv.writer(csvfile, delimiter=';')
            for publication in self.publications:
                saving_publication = [
                    publication.title,
                    publication.authors,
                    publication.info,
                    publication.link,
                    publication.year
                ]
                wr.writerow(saving_publication)

    def parse_publications(self):
        """
        Функция выполняет парсинг HTML-файла и сохраняет из него информацию.
        """

        print("Поиск публикаций по автору: ", self.author_id)

        for file in self.files_dir.glob("*.html"):
            print("Чтение файла", file.name)

            with open(file, "r", encoding="utf8") as f:
                page_text = f.read()

            soup = BeautifulSoup(page_text, "html.parser")

            table_cells = self.create_table_cells(soup)
            print("ОБЪЕМ ИНФОРМАЦИИ", len(table_cells))

            for table_cell in table_cells:
                info = self.get_info(table_cell)

                publication = Publication(
                    title=self.get_title(table_cell),
                    authors=self.get_authors(table_cell),
                    info=info,
                    link=self.get_link(table_cell),
                    year=self.get_year(table_cell)
                )
                # publication.get_year()

                self.publications.append(publication)
