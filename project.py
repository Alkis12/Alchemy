import sys  # импортируем все библиотеки
import sqlite3
import json
from PyQt5 import uic
from tkinter import messagebox as mb
from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog


class Game(QMainWindow):  # создание класса игры
    def __init__(self):
        super().__init__()
        uic.loadUi('project alhemy.ui', self)
        with open("pairs.json", "r") as pairs_read:  # импорт всех данных из json файлов
            self.pairs = json.load(pairs_read)
        with open("coins.json", "r") as coins_read:
            self.current_coins = json.load(coins_read)
        with open("generated.json", "r") as generated_read:
            self.generated = json.load(generated_read)
        with open("translate.json", "r") as translate_read:
            self.translate = json.load(translate_read)
        with open("translate1.json", "r") as translate1_read:
            self.translate1 = json.load(translate1_read)
        with open("language.json", "r") as language_read:
            self.language = json.load(language_read)
        self.con = sqlite3.connect("achievements.db")  # импорт достижений из SQL таблицы
        self.update_money()  # создание и подключение всех переменных и функций
        self.a = self.generated[0]  # переменные a и b хрант в себе информацию про текущий выбранный элемент
        self.b = self.generated[0]
        self.element_1.addItems(self.generated)  # у меня понятные и красивые имена переменных,
        self.element_2.addItems(self.generated)  # поэтому не вижу смысла в 100+ комментариях
        self.element_1.activated[str].connect(self.change_element_1)
        self.element_2.activated[str].connect(self.change_element_2)
        self.btn.clicked.connect(self.new_element)
        self.tip_buy.clicked.connect(self.tips)
        self.achievements_show.clicked.connect(self.print_achievements)
        self.settings_open.clicked.connect(self.settings)

    def change_element_1(self, text):
        self.a = text

    def change_element_2(self, text):
        self.b = text

    def new_element(self):
        a, b = self.a, self.b
        if self.language == 'e':
            a = self.translate1[a]
            b = self.translate1[b]
        if a > b:
            a, b = b, a
        pair = a + ' ' + b
        if pair in self.pairs:
            if self.language == 'r':
                element = self.pairs[pair]
            else:
                element = self.translate[self.pairs[pair]]
            if element in self.generated:
                if self.language == 'r':
                    self.itog.setText('Получен старый элемент - ' + element + '.')
                else:
                    self.itog.setText('Old item received - ' + element + '.')
            else:
                self.current_coins += 25
                self.update_money()
                if self.language == 'r':
                    self.generated.append(element)
                else:
                    self.generated.append(element)
                self.generated.sort()
                self.element_1.clear()
                self.element_2.clear()
                if self.language == 'r':
                    self.itog.setText('Получен новый элемент - ' + element + '!')
                    self.element_1.addItems(sorted(self.generated))
                    self.element_2.addItems(sorted(self.generated))
                else:
                    self.itog.setText('New item received - ' + element + '!')
                    self.element_1.addItems(sorted(self.generated))
                    self.element_2.addItems(sorted(self.generated))
                with open("generated.json", "w") as generated_save:
                    json.dump(self.generated, generated_save)
                self.new_achievement()
        else:
            if self.language == 'r':
                self.itog.setText('Некомбинируемые элементы')
            else:
                self.itog.setText('Not combinable elements')

    def update_money(self):
        self.coins_show.display(self.current_coins)
        with open("coins.json", "w") as coins_save:
            json.dump(self.current_coins, coins_save)

    def tips(self):
        if self.current_coins < 50:
            pass
        else:
            if self.language == 'r':
                answer = mb.askyesno(title="Подтверждение покупки", message="Потратить 50 монет на подсказку?")
            else:
                answer = mb.askyesno(title="Proof of purchase", message="Spend 50 coins on a hint?")
            if answer:
                self.current_coins -= 50
                self.update_money()
                for i in self.pairs:
                    j = i.split()
                    if self.language == 'r':
                        a = self.pairs[i]
                        b = j[0]
                        c = j[1]
                    else:
                        a = self.translate[self.pairs[i]]
                        b_1 = j[0] in self.translate
                        if b_1:
                            b = self.translate[j[0]]
                        else:
                            b = False
                        c_1 = j[1] in self.translate
                        if c_1:
                            c = self.translate[j[1]]
                        else:
                            c = False
                    if a not in self.generated and b in self.generated and c in self.generated:
                        if self.language == 'r':
                            mb.showinfo("Новая пара", j[0] + ' + ' + j[1] + ' = ' + self.pairs[i])
                        else:
                            created_element = self.translate[self.pairs[i]]
                            element1 = self.translate[j[0]]
                            element2 = self.translate[j[1]]
                            mb.showinfo("New pair", element1 + ' + ' + element2 + ' = ' + created_element)
                        break
                else:
                    if self.language == 'r':
                        mb.showinfo("Нет комбинаций", 'Вы собрали все возможные элементы. Достойно уважения!!!')
                    else:
                        mb.showinfo("No combinations", 'You have collected all possible elements. Worthy of respect!!!')

    def new_achievement(self):
        g = len(self.generated)
        cur = self.con.cursor()
        if self.language == 'r':
            result = cur.execute("""SELECT name FROM Names
                    WHERE number = """ + str(g)).fetchall()
        else:
            result = cur.execute("""SELECT english_name FROM Names
                    WHERE number = """ + str(g)).fetchall()
        if result:
            second_word = result[0][0]
            if self.language == 'r':
                first_word = "Новое достижение"
            else:
                first_word = "New achievement"
            mb.showinfo(first_word, second_word)
            cur = self.con.cursor()
            cur.execute("""UPDATE Names
    SET bool = 1
    WHERE number = """ + str(g))
            self.con.commit()

    def print_achievements(self):
        cur = self.con.cursor()
        if self.language == 'r':
            result = cur.execute("""SELECT name FROM Names
                                WHERE bool = 1""").fetchall()
            a = []
            for i in result:
                a.append(i[0])
            if not(a):
                a.append('У вас нет достижений')
            mb.showinfo("Список достижений", '\n'.join(a))
        else:
            result = cur.execute("""SELECT english_name FROM Names
                                            WHERE bool = 1""").fetchall()
            a = []
            for i in result:
                a.append(i[0])
            if not(a):
                a.append('You not have achievements')
            mb.showinfo("List of achievements", '\n'.join(a))

    def change_language(self):
        self.element_1.clear()
        self.element_2.clear()
        if self.language == "r":
            self.language = "e"
            self.choose_1.setText('Choose first element')
            self.choose_2.setText('Choose second element')
            self.btn.setText('COMBINE')
            self.tip_buy.setText('Use a hint')
            self.title.setText('Alchemy')
            self.achievements_show.setText('Achievements')
            translated_generated = []
            for i in self.generated:
                translated_generated.append(self.translate[i])
            self.generated = sorted(translated_generated)
            self.a = self.generated[0]
            self.b = self.generated[0]
        else:
            self.language = "r"
            self.choose_1.setText('Выберите первый елемент')
            self.choose_2.setText('Выберите второй елемент')
            self.btn.setText('СКРЕСТИТЬ')
            self.tip_buy.setText('Использовать подсказку')
            self.title.setText('Алхимия')
            self.achievements_show.setText('Достижения')
            translated_generated = []
            for i in self.generated:
                translated_generated.append(self.translate1[i])
            self.generated = sorted(translated_generated)
            self.a = self.generated[0]
            self.b = self.generated[0]
        self.element_1.addItems(self.generated)
        self.element_2.addItems(self.generated)
        with open("language.json", "w") as language_save:
            json.dump(self.language, language_save)
        with open("generated.json", "w") as generated_save:
            json.dump(self.generated, generated_save)

    def settings(self):
        if self.language == 'r':
            do1 = "Смена языка"
            do2 = "Сброс прогресса"
            do3 = "Выход из игры"
            do4 = "Выход из настроек"
            i, answer = QInputDialog.getItem(self, "Выберите действие",
                                             "Выберите необходимое действие",
                                             (do1, do2, do3, do4),
                                             0, False)
        else:
            do1 = "Switch language"
            do2 = "Reset progress"
            do3 = "Exit the game"
            do4 = "Exit the settings"
            i, answer = QInputDialog.getItem(self, "Select an action",
                                             "Select the desired action",
                                             (do1, do2, do3, do4),
                                             0, False)
        if answer:
            if i == do1:
                self.change_language()
            elif i == do2:
                self.delete_achievements()
                self.reset()
            elif i == do3:
                sys.exit(app.exec_())
            elif i != do4:
                if self.language == 'r':
                    mb.showerror("Ошибка", 'Введено некоррекное значение')
                else:
                    mb.showerror("Error", 'Invalid value entered')

    def delete_achievements(self):
        cur = self.con.cursor()
        cur.execute("""UPDATE Names
            SET bool = 0
            WHERE number > 0""")
        self.con.commit()

    def reset(self):
        if self.language == 'r':
            answer = mb.askyesno(title="Подтверждение действия", message="Удалить прогресс?")
        else:
            answer = mb.askyesno(title="Action confirmation", message="Delete progress?")
        if answer:
            with open("generated.json", "w") as generated_null:
                json.dump(['Вода', 'Воздух', 'Земля', 'Огонь'], generated_null)
            with open("coins.json", "w") as coins_null:
                json.dump(100, coins_null)
            with open("language.json", "w") as language_null:
                json.dump('r', language_null)
            if self.language == 'r':
                mb.showinfo("Удаление прогресса", 'Ваш прогресс удален')
            else:
                mb.showinfo("Delete progress", 'Your progress is deleted')
            self.current_coins = 100
            self.update_money()
            self.choose_1.setText('Выберите первый елемент')
            self.choose_2.setText('Выберите второй елемент')
            self.title.setText('Алхимия')
            self.btn.setText('СКРЕСТИТЬ')
            self.tip_buy.setText('Использовать подсказку')
            self.achievements_show.setText('Достижения')
            self.generated = ['Вода', 'Воздух', 'Земля', 'Огонь']
            self.language = 'r'
            self.element_1.clear()
            self.element_2.clear()
            self.a = self.generated[0]
            self.b = self.generated[0]
            self.element_1.addItems(self.generated)
            self.element_2.addItems(self.generated)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Game()
    ex.show()
    sys.exit(app.exec_())
# спасибо за внимание
# проект планирую развивать (но это не точно)
