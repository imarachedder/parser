import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class PublicationVisualizer:
    def __init__(self, data_path):
        """
        Инициализация класса с DataFrame
        :param df: pandas DataFrame с данными, содержащими столбец 'Год публикации'
        """
        self.data_path = data_path
        self.df = pd.read_csv(self.data_path/"publications2.csv", sep=';')

    def save_year_distribution(self, filename="year_distribution.jpeg"):
        """
        Строит график распределения публикаций по годам и сохраняет в файл
        :param filename: имя файла для сохранения (по умолчанию JPEG)
        """
        # Группировка данных по годам
        filepath = self.data_path / filename
        year_counts = self.df['Год публикации'].value_counts().sort_index()

        # Построение графика
        plt.figure(figsize=(10, 8))
        
        # Столбчатая диаграмма
        plt.bar(year_counts.index, year_counts.values, alpha=0.7, color='green', label='Количество публикаций')
        
        
        sns.kdeplot(
            data=self.df,
            x='Год публикации',
            bw_adjust=0.5,
            fill=False,
            color='blue',
            label='Плотность',
            clip=(min(year_counts.index), max(year_counts.index))
        )

        plt.xlabel('Год публикации')
        plt.ylabel('Количество публикаций')
        plt.title('Количество публикаций по годам')
        plt.xticks(ticks=year_counts.index, labels=year_counts.index, rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.legend()

        # Сохранение графика в файл
        plt.savefig(filepath, format="jpeg", dpi=300)
        plt.close()  
        print(f"График сохранён в файл: {filename}")