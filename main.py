import datetime
import sqlite3
import sys
from datetime import date
from screeninfo import get_monitors
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QLineEdit, QComboBox, QTableWidget,
                             QTableWidgetItem, QAbstractItemView, QHeaderView, QProgressBar, QListWidget)
from PyQt6.QtGui import QPixmap, QIcon, QCursor
from PyQt6.QtCore import Qt
from pyqtgraph import PlotWidget
from other import font, ProgressBarStyle, list_style


# класс главного окна приложения
class CalorieCounter(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Calorie Counter")
        self.setFixedSize(900, 600)
        self.move((get_monitors()[0].width - self.width()) // 2, (get_monitors()[0].height - self.height()) // 2)
        self.background = QLabel(self)
        self.background.setGeometry(0, 0, self.width(), self.height())
        self.background.setPixmap(QPixmap('images/main_background_image.jpg'))
        self.setWindowIcon(QIcon("images/main_window_icon.png"))
        font.setPointSize(14)

        # кнопка настроек
        self.settings_button = QPushButton(self)
        self.settings_button.setGeometry(820, 10, 71, 71)
        self.settings_button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.settings_button.setIcon(QIcon('images/setting_icon.png'))
        self.settings_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.settings_button.setIconSize(self.settings_button.size())
        self.settings_button.clicked.connect(self.settings_button_clicked)

        # кнопка для перехода к статистике
        self.statistics_button = QPushButton(self)
        self.statistics_button.setGeometry(820, 90, 71, 71)
        self.statistics_button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.statistics_button.setIcon(QIcon('images/statistics_icon.png'))
        self.statistics_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.statistics_button.setIconSize(self.statistics_button.size())
        self.statistics_button.clicked.connect(self.statistics_button_clicked)

        # кнопка закрытия приложения
        self.exit_button = QPushButton(self)
        self.exit_button.setGeometry(10, 520, 71, 71)
        self.exit_button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.exit_button.setIcon(QIcon('images/exit_icon.png'))
        self.exit_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.exit_button.setIconSize(self.exit_button.size())
        self.exit_button.clicked.connect(self.close)

        # кнопка для добавления приема пища за сегодня
        self.add_meal_button = QPushButton(self)
        self.add_meal_button.setGeometry(340, 310, 221, 61)
        self.add_meal_button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.add_meal_button.setIcon(QIcon('images/add_meal_button_icon.png'))
        self.add_meal_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.add_meal_button.setIconSize(self.add_meal_button.size())
        self.add_meal_button.clicked.connect(self.add_meal_button_clicked)

        # кнопка для перехода в окно со всеми продуктами в базе данных
        self.database_food_button = QPushButton(self)
        self.database_food_button.setGeometry(350, 380, 201, 61)
        self.database_food_button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.database_food_button.setIcon(QIcon('images/add_food_button_icon.png'))
        self.database_food_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.database_food_button.setIconSize(self.database_food_button.size())
        self.database_food_button.clicked.connect(self.database_food_button_clicked)

        con = sqlite3.connect("database.sqlite")
        cur = con.cursor()
        # проверка, есть ли в базеданных сегоднящний день у пользователя или же нет
        if str(date.today()) not in [i[0] for i in cur.execute(f"""SELECT day FROM days_stats 
                WHERE name = '{open('login.txt', 'r').read()}'""")]:
            cur.execute(f"""INSERT INTO days_stats(name, day, calories, proteins, fats, carbohydrates)
                VALUES('{open('login.txt', 'r').read()}', '{date.today()}', {0}, {0}, {0}, {0})""")
        con.commit()
        information = cur.execute(f"""SELECT * FROM main WHERE login = '{open("login.txt", "r").read()}'""").fetchone()
        today_cpfc = cur.execute(f"""SELECT * FROM days_stats 
        WHERE name = '{open("login.txt", "r").read()}' AND day = '{date.today()}'""").fetchone()
        if information[5] == 1:
            ratio = 5
        else:
            ratio = -161
        calories = int((information[3] * 10 + information[4] * 6.25 - 5 * information[6] + ratio) * 1.375 *
                       cur.execute(f"""SELECT koef FROM goals WHERE id = (SELECT goal FROM main 
                       WHERE login = '{list(open("login.txt", 'r'))[0]}')""").fetchone()[0])

        # блоки с progressbar и label для калорий, белков, жиров, углеводов
        self.calories_progressBar = QProgressBar(self, minimum=0, maximum=100, textVisible=False)
        self.calories_progressBar.setGeometry(210, 110, 231, 23)
        self.calories_progressBar.setProperty("value",
                                              100 if today_cpfc[3] / calories > 1
                                              else today_cpfc[3] / calories * 100)
        self.calories_progressBar.setStyleSheet(ProgressBarStyle)

        self.calories_label = QLabel(self)
        self.calories_label.setGeometry(210, 140, 231, 25)
        self.calories_label.setFont(font)
        self.calories_label.setText(f"""Calories: {today_cpfc[3]}/{calories}""")
        self.calories_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.proteins_progressBar = QProgressBar(self, minimum=0, maximum=100, textVisible=False)
        self.proteins_progressBar.setGeometry(460, 110, 231, 23)
        self.proteins_progressBar.setProperty("value", 100 if int(today_cpfc[4]) / int(calories * 0.3 / 4) > 1
                                              else int(today_cpfc[4]) / int(calories * 0.3 / 4) * 100)
        self.proteins_progressBar.setStyleSheet(ProgressBarStyle)

        self.proteins_label = QLabel(self)
        self.proteins_label.setGeometry(460, 140, 231, 25)
        self.proteins_label.setFont(font)
        self.proteins_label.setText(f"Proteins: {int(today_cpfc[4])}/{int(calories * 0.3 / 4)}")
        self.proteins_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.fats_progressBar = QProgressBar(self, minimum=0, maximum=100, textVisible=False)
        self.fats_progressBar.setGeometry(210, 190, 231, 23)
        self.fats_progressBar.setProperty("value", 100 if int(today_cpfc[5]) / int(calories * 0.3 / 9) > 1
                                          else int(today_cpfc[5]) / int(calories * 0.3 / 9) * 100)
        self.fats_progressBar.setStyleSheet(ProgressBarStyle)

        self.fats_label = QLabel(self)
        self.fats_label.setGeometry(210, 220, 231, 25)
        self.fats_label.setFont(font)
        self.fats_label.setText(f"Fats: {int(today_cpfc[5])}/{int(calories * 0.3 / 9)}")
        self.fats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.carbohydrates_progressBar = QProgressBar(self, minimum=0, maximum=100, textVisible=False)
        self.carbohydrates_progressBar.setGeometry(460, 190, 231, 23)
        self.carbohydrates_progressBar.setProperty("value",
                                                   100 if int(today_cpfc[6]) / int(calories * 0.4 / 4) > 1
                                                   else int(today_cpfc[6]) / int(calories * 0.4 / 4) * 100)
        self.carbohydrates_progressBar.setStyleSheet(ProgressBarStyle)

        self.carbohydrates_label = QLabel(self)
        self.carbohydrates_label.setGeometry(460, 220, 231, 25)
        self.carbohydrates_label.setFont(font)
        self.carbohydrates_label.setText(f"Carbohydrates: {int(today_cpfc[6])}/{int(calories * 0.4 / 4)}")
        self.carbohydrates_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        con.close()

    # функция для перехода к окну статистики пользователя при нажатии на кнопку
    def statistics_button_clicked(self):
        global stats
        stats = Statistics()
        stats.show()
        self.close()

    # функция для перехода к настройкам при нажатии на кнопку
    def settings_button_clicked(self):
        global settings_window
        settings_window = Settings()
        settings_window.show()
        self.close()

    # функция для перехода к базе данных продуктов
    def database_food_button_clicked(self):
        global database_food_window
        database_food_window = Products()
        database_food_window.show()
        self.close()

    # функция для перехода к окну с добавлением приема пищи
    def add_meal_button_clicked(self):
        global meal
        meal = Meal()
        meal.show()
        self.close()


# класс настроек
class Settings(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Settings")
        self.setFixedSize(500, 800)
        self.move((get_monitors()[0].width - self.width()) // 2, (get_monitors()[0].height - self.height()) // 2)
        self.background = QLabel(self)
        self.background.setGeometry(0, 0, self.width(), self.height())
        self.background.setPixmap(QPixmap('images/settings_background_image.jpg'))
        self.setWindowIcon(QIcon("images/settings_window_icon.png"))

        font.setPointSize(22)
        con = sqlite3.connect("database.sqlite")
        cur = con.cursor()

        self.back_button = QPushButton(self)
        self.back_button.setGeometry(10, 10, 71, 71)
        self.back_button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.back_button.setIcon(QIcon('images/back_icon.png'))
        self.back_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.back_button.setIconSize(self.back_button.size())
        self.back_button.clicked.connect(self.back_button_clicked)

        self.profile_icon = QPushButton(self)
        self.profile_icon.setGeometry(370, 20, 111, 111)
        self.profile_icon.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.profile_icon.setIcon(QIcon('images/user_icon.png'))
        self.profile_icon.setIconSize(self.profile_icon.size())

        self.name = QLabel(self)
        self.name.setGeometry(100, 20, 261, 111)
        self.name.setText(f'''{cur.execute(f"""SELECT login FROM main WHERE login = 
                                            '{list(open("login.txt", "r"))[0]}'""").fetchone()[0]}''')
        self.name.setFont(font)
        self.name.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.name.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.height = QLabel(self)
        self.height.setGeometry(30, 160, 331, 41)
        self.height.setFont(font)
        self.height.setText(f'''Рост:\t{cur.execute(f"""SELECT height FROM main 
                                                            WHERE login = 
                                                            '{list(open("login.txt", "r"))[0]}'""").fetchone()[0]}  см''')
        self.height.setFont(font)

        self.height_change_button = QPushButton(self)
        self.height_change_button.setGeometry(370, 160, 121, 51)
        self.height_change_button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.height_change_button.setIcon(QIcon('images/Change_button_icon.png'))
        self.height_change_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.height_change_button.setIconSize(self.profile_icon.size())
        self.height_change_button.clicked.connect(self.change_height_clicked)

        self.weight = QLabel(self)
        self.weight.setGeometry(30, 220, 331, 41)
        self.weight.setFont(font)
        self.weight.setText(f'''Вес:\t{cur.execute(f"""SELECT weight FROM main 
                                                            WHERE login = 
                                                            '{list(open("login.txt", "r"))[0]}'""").fetchone()[0]}  кг''')
        self.height.setFont(font)

        self.weight_change_button = QPushButton(self)
        self.weight_change_button.setGeometry(370, 220, 121, 51)
        self.weight_change_button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.weight_change_button.setIcon(QIcon('images/Change_button_icon.png'))
        self.weight_change_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.weight_change_button.setIconSize(self.profile_icon.size())
        self.weight_change_button.clicked.connect(self.change_weight_clicked)

        self.age = QLabel(self)
        self.age.setGeometry(30, 280, 331, 41)
        self.age.setFont(font)
        self.age.setText(f'''Возраст:\t{cur.execute(f"""SELECT age FROM main 
                                                            WHERE login = 
                                                            '{list(open("login.txt", "r"))[0]}'""").fetchone()[0]}  лет''')
        self.age.setFont(font)

        self.age_change_button = QPushButton(self)
        self.age_change_button.setGeometry(370, 280, 121, 51)
        self.age_change_button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.age_change_button.setIcon(QIcon('images/Change_button_icon.png'))
        self.age_change_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.age_change_button.setIconSize(self.profile_icon.size())
        self.age_change_button.clicked.connect(self.change_age_clicked)

        self.gender = QLabel(self)
        self.gender.setGeometry(30, 340, 461, 41)
        self.gender.setFont(font)
        self.gender.setText(f"Пол:\t{cur.execute(f"""SELECT name FROM genders
                                                            WHERE id = (SELECT gender FROM main
                                                            WHERE login = 
                                                            '{list(open("login.txt", "r"))[0]}')""").fetchone()[0]}")

        self.IMT = QLabel(self)
        self.IMT.setGeometry(30, 400, 461, 41)
        self.IMT.setFont(font)
        index = (cur.execute(f"""SELECT weight FROM main WHERE login = '{list(open("login.txt", "r"))[0]}'""").fetchone()[0]
        / (cur.execute(f"""SELECT height FROM main WHERE login = '{list(open("login.txt", "r"))[0]}'""").fetchone()[0] / 100) ** 2)
        if index < 16:
            result = "Значительный дефицит"
        elif 16 <= index < 18.5:
            result = "Дефицит"
        elif 18.5 <= index <= 25:
            result = "Норма"
        elif 25 < index < 30:
            result = "Лишний вес"
        elif 30 <= index < 35:
            result = "Ожирение I"
        elif 35 <= index <= 40:
            result = "Ожирение II"
        else:
            result = "Ожирение III"
        self.IMT.setText(f"ИМТ:\t {round(index, 1)} ({result})")

        self.choice_goal = QLabel(self)
        self.choice_goal.setGeometry(30, 460, 301, 41)
        self.choice_goal.setFont(font)
        self.choice_goal.setText("Выбрать цель:")

        self.choice_goal_combobox = QComboBox(self)
        self.choice_goal_combobox.setGeometry(320, 462, 171, 37)
        self.choice_goal_combobox.addItems(["Набрать вес", "Поддерживать вес", "Сбросить вес"])
        self.choice_goal_combobox.setCurrentText(cur.execute(f"""SELECT goal FROM goals 
        WHERE id = (SELECT goal FROM main 
        WHERE login = '{list(open("login.txt", "r"))[0]}')""").fetchone()[0])

        self.recomendation = QLabel(self)
        self.recomendation.setGeometry(30, 520, 461, 131)
        font.setPointSize(16)
        self.recomendation.setFont(font)
        self.recomendation.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        if index < 18.5:
            self.recomendation.setText(f"Рекомендация:\nКонсультация специалиста,\nназначение диеты и образа жизни,\n"
                                       f"увеличение кол-ва потребляемых ккал\n(ОПЦИЯ НАБРАТЬ ВЕС)")
        elif index > 25:
            self.recomendation.setText(f"Рекомендация:\nКонсультация специалиста,\nфизическая нагрузка,\n"
                                       f"уменьшение кол-ва потребляемых ккал\n(ОПЦИЯ СБРОСИТЬ ВЕС)")
        else:
            self.recomendation.setText(f"Рекомендация:\nПродолжать поддержку нормы веса\n(ОПЦИЯ ПОДДЕРЖИВАТЬ ВЕС)")

        self.logout_button = QPushButton(self)
        self.logout_button.setGeometry(10, 670, 481, 51)
        self.logout_button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.logout_button.setIcon(QIcon('images/Logout_button_icon.png'))
        self.logout_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.logout_button.setIconSize(self.logout_button.size())
        self.logout_button.clicked.connect(self.logout_button_clicked)

        self.delete_account_button = QPushButton(self)
        self.delete_account_button.setGeometry(10, 730, 481, 51)
        self.delete_account_button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.delete_account_button.setIcon(QIcon('images/delete_account_button_icon.png'))
        self.delete_account_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.delete_account_button.setIconSize(self.delete_account_button.size())
        self.delete_account_button.clicked.connect(self.delete_account_button_clicked)

        con.close()

    def update_goal(self):
        con = sqlite3.connect("database.sqlite")
        cur = con.cursor()
        if self.choice_goal_combobox.currentText() == "Сбросить вес":
            cur.execute(f"""UPDATE main
            SET goal = 1 WHERE login = '{open("login.txt", 'r').read()}'""")
        elif self.choice_goal_combobox.currentText() == "Поддерживать вес":
            cur.execute(f"""UPDATE main
            SET goal = 2 WHERE login = '{open("login.txt", 'r').read()}'""")
        elif self.choice_goal_combobox.currentText() == "Набрать вес":
            cur.execute(f"""UPDATE main
            SET goal = 3 WHERE login = '{open("login.txt", 'r').read()}'""")
        con.commit()
        con.close()

    def back_button_clicked(self):
        global main_window
        self.update_goal()
        main_window = CalorieCounter()
        main_window.show()
        self.close()

    def change_height_clicked(self):
        global change_information_window
        change_information_window = ChangeInformation(0)
        change_information_window.show()
        self.update_goal()
        self.close()

    def change_weight_clicked(self):
        global change_information_window
        change_information_window = ChangeInformation(1)
        change_information_window.show()
        self.update_goal()
        self.close()

    def change_age_clicked(self):
        global change_information_window
        change_information_window = ChangeInformation(2)
        change_information_window.show()
        self.update_goal()
        self.close()

    def logout_button_clicked(self):
        self.update_goal()
        open('login.txt', 'w').write("")
        global registration_window
        registration_window = Registration()
        registration_window.show()
        self.close()

    def delete_account_button_clicked(self):
        global registration_window
        con = sqlite3.connect("database.sqlite")
        cur = con.cursor()
        cur.execute(f"""DELETE from main WHERE login = '{self.name.text()}'""")
        open('login.txt', 'w').write("")
        registration_window = Registration()
        registration_window.show()
        con.commit()
        con.close()
        self.close()


# класс окна с изменением информации
class ChangeInformation(QWidget):
    def __init__(self, mode):
        super().__init__()
        self.mode = mode
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Change account information")
        self.setFixedSize(370, 171)
        self.move((get_monitors()[0].width - self.width()) // 2, (get_monitors()[0].height - self.height()) // 2)
        self.background = QLabel(self)
        self.background.setGeometry(0, 0, self.width(), self.height())
        self.background.setPixmap(QPixmap('images/Registration_and_login_background_image.png'))
        self.setWindowIcon(QIcon("images/Change_information_icon.png"))
        font.setPointSize(18)

        self.cancel_button = QPushButton(self)
        self.cancel_button.setGeometry(10, 120, 170, 40)
        self.cancel_button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.cancel_button.setIcon(QIcon('images/cancel_button_icon.png'))
        self.cancel_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.cancel_button.setIconSize(self.cancel_button.size())
        self.cancel_button.clicked.connect(self.cancel_button_clicked)

        self.text = QLabel(self)
        self.text.setGeometry(0, 10, 371, 41)
        self.text.setFont(font)
        self.text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if self.mode == 1:
            self.text.setText("Введите новый вес:")
        elif self.mode == 0:
            self.text.setText("Введите новый рост:")
        elif self.mode == 2:
            self.text.setText("Введите новый возраст:")

        self.apply_button = QPushButton(self)
        self.apply_button.setGeometry(190, 120, 170, 40)
        self.apply_button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.apply_button.setIcon(QIcon('images/apply_button_icon.png'))
        self.apply_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.apply_button.setIconSize(self.apply_button.size())
        self.apply_button.clicked.connect(self.apply_button_clicked)

        self.new_information_lineEdit = QLineEdit(self)
        self.new_information_lineEdit.setGeometry(30, 70, 311, 31)

    # функция подтверждения изменений
    def apply_button_clicked(self):
        con = sqlite3.connect("database.sqlite")
        cur = con.cursor()
        if self.check_correct_input():
            if self.mode == 1:
                cur.execute(f"""UPDATE main
                                SET weight = {self.new_information_lineEdit.text()}
                                WHERE login = '{open("login.txt", 'r').read()}'""")
            elif self.mode == 0:
                cur.execute(f"""UPDATE main
                                SET height = {self.new_information_lineEdit.text()}
                                WHERE login = '{open("login.txt", 'r').read()}'""")
            elif self.mode == 2:
                cur.execute(f"""UPDATE main
                                SET age = {self.new_information_lineEdit.text()}
                                WHERE login = '{open("login.txt", 'r').read()}'""")
            con.commit()
            con.close()
            self.cancel_button_clicked()
        else:
            global error
            error = ErrorMessage()
            error.set_message("Введены некорректные данные!")
            error.show()

    # кнопка отмены и возращения обратно к настройкам
    def cancel_button_clicked(self):
        global settings_window
        settings_window = Settings()
        settings_window.show()
        self.close()

    # фукнция проверки правильности ввода
    def check_correct_input(self):
        if self.new_information_lineEdit.text().isnumeric():
            return True
        return False


# окно регистрации пользователя
class Registration(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Registration")
        self.setFixedSize(500, 353)
        self.move((get_monitors()[0].width - self.width()) // 2, (get_monitors()[0].height - self.height()) // 2)
        self.background = QLabel(self)
        self.background.setGeometry(0, 0, self.width(), self.height())
        self.background.setPixmap(QPixmap('images/Registration_and_login_background_image.png'))
        self.setWindowIcon(QIcon("images/user_icon.png"))

        font.setPointSize(22)
        self.reg_label = QLabel(self)
        self.reg_label.setGeometry(0, 10, 500, 41)
        self.reg_label.setText("Регистрация")
        self.reg_label.setFont(font)
        self.reg_label.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.reg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        font.setPointSize(18)
        self.login_label = QLabel(self)
        self.login_label.setGeometry(10, 60, 101, 31)
        self.login_label.setFont(font)
        self.login_label.setText("Логин:")

        self.login_lineEdit = QLineEdit(self)
        self.login_lineEdit.setGeometry(110, 60, 371, 31)

        self.password_label = QLabel(self)
        self.password_label.setGeometry(10, 100, 101, 31)
        self.password_label.setFont(font)
        self.password_label.setText("Пароль:")

        self.password_lineEdit = QLineEdit(self)
        self.password_lineEdit.setGeometry(110, 100, 371, 31)

        self.weight_label = QLabel(self)
        self.weight_label.setGeometry(10, 140, 101, 31)
        self.weight_label.setFont(font)
        self.weight_label.setText("Вес:")

        self.weight_lineEdit = QLineEdit(self)
        self.weight_lineEdit.setGeometry(110, 140, 371, 31)

        self.height_label = QLabel(self)
        self.height_label.setGeometry(10, 180, 101, 31)
        self.height_label.setFont(font)
        self.height_label.setText("Рост:")

        self.height_lineEdit = QLineEdit(self)
        self.height_lineEdit.setGeometry(110, 180, 371, 31)

        self.age_label = QLabel(self)
        self.age_label.setGeometry(10, 220, 171, 31)
        self.age_label.setFont(font)
        self.age_label.setText("Возраст:")

        self.age_lineEdit = QLineEdit(self)
        self.age_lineEdit.setGeometry(110, 220, 371, 31)

        self.gender_label = QLabel(self)
        self.gender_label.setGeometry(10, 260, 171, 31)
        self.gender_label.setFont(font)
        self.gender_label.setText("Выберите пол:")

        self.choice_gender = QComboBox(self)
        self.choice_gender.setGeometry(200, 260, 281, 31)
        self.choice_gender.addItems(["Мужской", "Женский"])

        self.to_login_button = QPushButton(self)
        self.to_login_button.setGeometry(10, 300, 231, 41)
        self.to_login_button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.to_login_button.setIcon(QIcon('images/login_button_icon.png'))
        self.to_login_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.to_login_button.setIconSize(self.to_login_button.size())
        self.to_login_button.clicked.connect(self.to_login_button_clicked)

        self.registration_button = QPushButton(self)
        self.registration_button.setGeometry(250, 300, 231, 41)
        self.registration_button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.registration_button.setIcon(QIcon('images/Registration_button_icon.png'))
        self.registration_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.registration_button.setIconSize(self.registration_button.size())
        self.registration_button.clicked.connect(self.registration_button_clicked)

    # фукнция для перехода к окну захода в аккаунт
    def to_login_button_clicked(self):
        global login_window
        login_window = Login()
        login_window.show()
        self.close()

    # функция подтверждения регистрации пользователя с проверкой правильности ввода данных
    def registration_button_clicked(self):
        global error
        con = sqlite3.connect("database.sqlite")
        cur = con.cursor()
        if self.login_lineEdit.text() in [i[0] for i in cur.execute("""SELECT login FROM main""")]:
            error = ErrorMessage()
            error.set_message("Такой аккаунт уже существует!")
            error.show()
        elif not (3 <= len(self.login_lineEdit.text()) <= 12):
            error = ErrorMessage()
            error.set_message("Длина логина должна быть\nне менее 3 и не более 12 символов!")
            error.show()
        elif not (4 <= len(self.password_lineEdit.text()) <= 15):
            error = ErrorMessage()
            error.set_message("Длина Пароля должна быть\nне менее 4 и не более 15 символов!")
            error.show()
        elif not self.weight_lineEdit.text().isnumeric():
            error = ErrorMessage()
            error.set_message("Вес должен быть числом!")
            error.show()
        elif not self.height_lineEdit.text().isnumeric():
            error = ErrorMessage()
            error.set_message("Рост должен быть числом!")
            error.show()
        elif not self.age_lineEdit.text().isnumeric():
            error = ErrorMessage()
            error.set_message("Возраст должен быть числом!")
            error.show()
        else:
            cur.execute(f"""INSERT INTO main(login, password, weight, height, gender, age, goal)
                        VALUES('{self.login_lineEdit.text()}', '{self.password_lineEdit.text()}', 
                        {self.weight_lineEdit.text()}, {self.height_lineEdit.text()}, (SELECT id FROM genders
                        WHERE name = '{self.choice_gender.currentText()}'), {self.age_lineEdit.text()}, {2})""")
            con.commit()
            con.close()
            self.to_login_button_clicked()


# окно захода в аккаунт
class Login(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Login")
        self.setFixedSize(500, 230)
        self.move((get_monitors()[0].width - self.width()) // 2, (get_monitors()[0].height - self.height()) // 2)
        self.background = QLabel(self)
        self.background.setGeometry(0, 0, self.width(), self.height())
        self.background.setPixmap(QPixmap('images/Registration_and_login_background_image.png'))
        self.setWindowIcon(QIcon("images/user_icon.png"))

        self.registration_button = QPushButton(self)
        self.registration_button.setGeometry(10, 180, 231, 41)
        self.registration_button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.registration_button.setIcon(QIcon('images/Registration_button_icon.png'))
        self.registration_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.registration_button.setIconSize(self.registration_button.size())
        self.registration_button.clicked.connect(self.registration_button_clicked)


        self.login_button = QPushButton(self)
        self.login_button.setGeometry(260, 180, 231, 41)
        self.login_button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.login_button.setIcon(QIcon('images/login_button_icon.png'))
        self.login_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.login_button.setIconSize(self.login_button.size())
        self.login_button.clicked.connect(self.login_button_clicked)

        font.setPointSize(22)
        self.login_window_name_label = QLabel(self)
        self.login_window_name_label.setGeometry(0, 10, 500, 41)
        self.login_window_name_label.setFont(font)
        self.login_window_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.login_window_name_label.setText("Войти")

        font.setPointSize(18)
        self.login_label = QLabel(self)
        self.login_label.setGeometry(20, 70, 101, 31)
        self.login_label.setFont(font)
        self.login_label.setText("Логин:")

        self.login_lineEdit = QLineEdit(self)
        self.login_lineEdit.setGeometry(130, 70, 351, 31)

        self.password_label = QLabel(self)
        self.password_label.setGeometry(20, 120, 101, 31)
        self.password_label.setFont(font)
        self.password_label.setText("Пароль:")

        self.password_lineEdit = QLineEdit(self)
        self.password_lineEdit.setGeometry(130, 120, 351, 31)

    # функция возращения к окну регистрации
    def registration_button_clicked(self):
        global registration_window
        registration_window = Registration()
        registration_window.show()
        self.close()

    # кнопка для подтверждения захода в аккаунт
    def login_button_clicked(self):
        global error
        con = sqlite3.connect("database.sqlite")
        cur = con.cursor()
        if self.login_lineEdit.text() in [i[0] for i in cur.execute("""SELECT login from main""")]:
            if self.password_lineEdit.text() == cur.execute(f"""SELECT password from main 
            WHERE login == '{self.login_lineEdit.text()}'""").fetchone()[0]:
                open("login.txt", "w").write(self.login_lineEdit.text())
                global main_window
                main_window = CalorieCounter()
                main_window.show()
                self.close()
            else:
                error = ErrorMessage()
                error.set_message("Неверный пароль!")
                error.show()
        else:
            error = ErrorMessage()
            error.set_message("Такого пользователя не существует.")
            error.show()
        con.close()


# класс окна с базой данных о продуктах
class Products(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Products")
        self.setFixedSize(900, 600)
        self.move((get_monitors()[0].width - self.width()) // 2, (get_monitors()[0].height - self.height()) // 2)
        self.background = QLabel(self)
        self.background.setGeometry(0, 0, self.width(), self.height())
        self.background.setPixmap(QPixmap('images/main_background_image.jpg'))
        self.setWindowIcon(QIcon("images/Products_window_icon.png"))

        self.refresh_button = QPushButton(self)
        self.refresh_button.setGeometry(100, 50, 185, 31)
        self.refresh_button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.refresh_button.setIcon(QIcon('images/refresh_button_icon.png'))
        self.refresh_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.refresh_button.setIconSize(self.refresh_button.size())
        self.refresh_button.clicked.connect(self.refresh_button_clicked)

        self.back_button = QPushButton(self)
        self.back_button.setGeometry(10, 10, 71, 71)
        self.back_button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.back_button.setIcon(QIcon('images/back_icon.png'))
        self.back_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.back_button.setIconSize(self.back_button.size())
        self.back_button.clicked.connect(self.back_button_clicked)

        self.search_button = QPushButton(self)
        self.search_button.setGeometry(300, 50, 185, 31)
        self.search_button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.search_button.setIcon(QIcon('images/search_button_icon.png'))
        self.search_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.search_button.setIconSize(self.search_button.size())
        self.search_button.clicked.connect(self.search_button_clicked)

        self.add_button = QPushButton(self)
        self.add_button.setGeometry(510, 300, 371, 41)
        self.add_button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.add_button.setIcon(QIcon('images/add_button_icon.png'))
        self.add_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.add_button.setIconSize(self.add_button.size())
        self.add_button.clicked.connect(self.add_button_clicked)

        self.delete_button = QPushButton(self)
        self.delete_button.setGeometry(510, 480, 371, 41)
        self.delete_button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.delete_button.setIcon(QIcon('images/delete_button_icon.png'))
        self.delete_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.delete_button.setIconSize(self.delete_button.size())
        self.delete_button.clicked.connect(self.delete_button_clicked)

        font.setPointSize(18)
        self.search_label = QLabel(self)
        self.search_label.setGeometry(100, 10, 91, 31)
        self.search_label.setFont(font)
        self.search_label.setText("Поиск:")

        self.search_lineEdit = QLineEdit(self)
        self.search_lineEdit.setGeometry(180, 10, 301, 31)

        self.add_label = QLabel(self)
        self.add_label.setGeometry(510, 20, 371, 31)
        self.add_label.setFont(font)
        self.add_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.add_label.setText("Добавить")

        self.delete_label = QLabel(self)
        self.delete_label.setGeometry(510, 400, 371, 31)
        self.delete_label.setFont(font)
        self.delete_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.delete_label.setText("Удалить")

        font.setPointSize(16)
        self.name_label = QLabel(self)
        self.name_label.setGeometry(510, 70, 141, 31)
        self.name_label.setFont(font)
        self.name_label.setText("Наименование:")

        self.name_lineEdit = QLineEdit(self)
        self.name_lineEdit.setGeometry(650, 70, 231, 31)

        self.calories_label = QLabel(self)
        self.calories_label.setGeometry(510, 110, 141, 31)
        self.calories_label.setFont(font)
        self.calories_label.setText("Калории")

        self.calories_lineEdit = QLineEdit(self)
        self.calories_lineEdit.setGeometry(650, 110, 231, 31)

        self.proteins_label = QLabel(self)
        self.proteins_label.setGeometry(510, 150, 141, 31)
        self.proteins_label.setFont(font)
        self.proteins_label.setText("Белки")

        self.proteins_lineEdit = QLineEdit(self)
        self.proteins_lineEdit.setGeometry(650, 150, 231, 31)

        self.fats_label = QLabel(self)
        self.fats_label.setGeometry(510, 190, 141, 31)
        self.fats_label.setFont(font)
        self.fats_label.setText("Жиры")

        self.fats_lineEdit = QLineEdit(self)
        self.fats_lineEdit.setGeometry(650, 190, 231, 31)

        self.carbohydrates_label = QLabel(self)
        self.carbohydrates_label.setGeometry(510, 230, 141, 31)
        self.carbohydrates_label.setFont(font)
        self.carbohydrates_label.setText("Углеводы")

        self.carbohydrates_lineEdit = QLineEdit(self)
        self.carbohydrates_lineEdit.setGeometry(650, 230, 231, 31)

        self.id_label = QLabel(self)
        self.id_label.setGeometry(510, 440, 41, 31)
        self.id_label.setFont(font)
        self.id_label.setText("ID:")

        self.id_lineEdit = QLineEdit(self)
        self.id_lineEdit.setGeometry(560, 440, 321, 31)

        font.setPointSize(9)
        self.warning_text = QLabel(self)
        self.warning_text.setGeometry(510, 270, 371, 20)
        self.warning_text.setFont(font)
        self.warning_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.warning_text.setText("Все значения вводятся на 100г. продукта")

        self.product_table = QTableWidget(self)
        self.product_table.setGeometry(10, 90, 480, 501)
        self.product_table.horizontalHeader().setDefaultSectionSize(77)
        self.product_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.product_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.refresh_button_clicked()
        for i in range(6):
            self.product_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)

    # кнопка с проверкой правильности ввода и занесения нового продукта в базу данных
    def add_button_clicked(self):
        global error
        con = sqlite3.connect("database.sqlite")
        cur = con.cursor()
        if not (self.name_lineEdit.text() != ""):
            error = ErrorMessage()
            error.set_message("Название продукта не должно быть пустым!")
            error.show()
        elif not(self.name_lineEdit.text() not in [i[0] for i in cur.execute(f"""SELECT name FROM products""")]):
            error = ErrorMessage()
            error.set_message("Такой продукт уже существует!")
            error.show()
        elif not self.calories_lineEdit.text().isdigit():
            error = ErrorMessage()
            error.set_message("Некорректный ввод данных в поле 'Калории'")
            error.show()
        elif not self.is_real(self.proteins_lineEdit.text()):
            error = ErrorMessage()
            error.set_message("Некорректный ввод данных в поле 'Белки'")
            error.show()
        elif not self.is_real(self.fats_lineEdit.text()):
            error = ErrorMessage()
            error.set_message("Некорректный ввод данных в поле 'Жиры'")
            error.show()
        elif not self.is_real(self.carbohydrates_lineEdit.text()):
            error = ErrorMessage()
            error.set_message("Некорректный ввод данных в поле 'Углеводы'")
            error.show()
        else:
            cur.execute(f"""INSERT INTO products(name, calories, proteins, fats, carbohydrates)
                                VALUES('{self.name_lineEdit.text()}', {self.calories_lineEdit.text()}, 
                                {self.proteins_lineEdit.text()}, {self.fats_lineEdit.text()}, 
                                {self.carbohydrates_lineEdit.text()})""")
            con.commit()
            self.refresh_button_clicked()

    # функция проверки является ли вводимое значние вещественным числом или целым, используется в self.add_button_clicked
    def is_real(self, num):
        if num.isdigit():
            return True
        else:
            try:
                float(num)
                return True
            except ValueError:
                return False

    # функция для обновления виджета с таблицей продуктов
    def refresh_button_clicked(self):
        con = sqlite3.connect("database.sqlite")
        cur = con.cursor()
        result = [*cur.execute(f"""SELECT * FROM products""")]
        self.product_table.setColumnCount(len(result[0]))
        self.product_table.setRowCount(len(result))
        self.product_table.clear()
        for row, item in enumerate(result):
            for col, value in enumerate(item):
                item = QTableWidgetItem(str(value))
                self.product_table.setItem(row, col, item)
        self.product_table.setHorizontalHeaderLabels(["ID", "name", "calories", "proteins", "fats", "carbs"])
        con.close()
        self.search_lineEdit.setText("")

    # функция удаления продукта из базы данных по ID
    def delete_button_clicked(self):
        global error
        con = sqlite3.connect("database.sqlite")
        cur = con.cursor()
        if self.id_lineEdit.text() not in [str(i[0]) for i in cur.execute(f"""SELECT id FROM products""")]:
            error = ErrorMessage()
            error.set_message("Некорректный ввод данных!")
            error.show()
        else:
            cur.execute(f"""DELETE from products WHERE id = {self.id_lineEdit.text()}""")
            con.commit()
        con.close()
        self.refresh_button_clicked()

    # функция поиска продукта по названию
    def search_button_clicked(self):
        con = sqlite3.connect("database.sqlite")
        cur = con.cursor()
        result = [*cur.execute(f"""SELECT * FROM products WHERE name LIKE '%{self.search_lineEdit.text()}%'""")]
        self.product_table.setColumnCount(0)
        if len(result) > 0:
            self.product_table.setColumnCount(len(result[0]))
        self.product_table.setRowCount(len(result))
        self.product_table.clear()
        for row, item in enumerate(result):
            for col, value in enumerate(item):
                item = QTableWidgetItem(str(value))
                self.product_table.setItem(row, col, item)
        self.product_table.setHorizontalHeaderLabels(["ID", "name", "calories", "proteins", "fats", "carbs"])
        con.close()

    # кнопка Назад
    def back_button_clicked(self):
        global main_window
        main_window = CalorieCounter()
        main_window.show()
        self.close()


# класс окна с предупреждением или ошибкой
class ErrorMessage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Warning")
        self.setFixedSize(320, 130)
        self.move((get_monitors()[0].width - self.width()) // 2, (get_monitors()[0].height - self.height()) // 2)
        self.background = QLabel(self)
        self.background.setGeometry(0, 0, self.width(), self.height())
        self.background.setPixmap(QPixmap('images/Registration_and_login_background_image.png'))
        self.setWindowIcon(QIcon("images/warning_icon.png"))

        self.warning = QLabel(self)
        self.warning.setGeometry(5, 0, 310, 40)
        font.setPointSize(20)
        self.warning.setFont(font)
        self.warning.setText("WARNING!")
        self.warning.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.message = QLabel(self)
        self.message.setGeometry(10, 40, 300, 50)
        self.message.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.button_ok = QPushButton(self)
        self.button_ok.setGeometry(110, 100, 100, 24)
        self.button_ok.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.button_ok.setIcon(QIcon('images/warning_ok_button_icon.png'))
        self.button_ok.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.button_ok.setIconSize(self.button_ok.size())
        self.button_ok.clicked.connect(self.close)

    # функция для выводимого текста ошибки
    def set_message(self, text):
        font.setPointSize(10)
        self.message.setFont(font)
        self.message.setText(f"{text}")


# класс окна с добавлением приема пищи
class Meal(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.text = []

    def initUI(self):
        self.setWindowTitle("Meal")
        self.setFixedSize(900, 600)
        self.move((get_monitors()[0].width - self.width()) // 2, (get_monitors()[0].height - self.height()) // 2)
        self.background = QLabel(self)
        self.background.setGeometry(0, 0, self.width(), self.height())
        self.background.setPixmap(QPixmap('images/main_background_image.jpg'))
        self.setWindowIcon(QIcon("images/meal_window_icon.png"))

        self.back_button = QPushButton(self)
        self.back_button.setGeometry(10, 10, 71, 71)
        self.back_button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.back_button.setIcon(QIcon('images/back_icon.png'))
        self.back_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.back_button.setIconSize(self.back_button.size())
        self.back_button.clicked.connect(self.back_button_clicked)

        self.search_lineEdit = QLineEdit(self)
        self.search_lineEdit.setGeometry(180, 9, 321, 31)

        self.list = QTableWidget(self)
        self.list.setGeometry(530, 10, 361, 421)
        self.list.horizontalHeader().setDefaultSectionSize(177)
        self.list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.list.setColumnCount(2)
        self.list.setRowCount(0)
        self.list.setHorizontalHeaderLabels(["name", "weight"])
        for i in range(3):
            self.list.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)

        self.refresh_button = QPushButton(self)
        self.refresh_button.setGeometry(110, 50, 185, 31)
        self.refresh_button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.refresh_button.setIcon(QIcon('images/refresh_button_icon.png'))
        self.refresh_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.refresh_button.setIconSize(self.refresh_button.size())
        self.refresh_button.clicked.connect(self.refresh_button_clicked)

        self.search_button = QPushButton(self)
        self.search_button.setGeometry(310, 50, 185, 31)
        self.search_button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.search_button.setIcon(QIcon('images/search_button_icon.png'))
        self.search_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.search_button.setIconSize(self.search_button.size())
        self.search_button.clicked.connect(self.search_button_clicked)

        self.id_lineEdit = QLineEdit(self)
        self.id_lineEdit.setGeometry(100, 470, 401, 31)

        self.weight_lineEdit = QLineEdit(self)
        self.weight_lineEdit.setGeometry(100, 510, 401, 31)

        self.add_button = QPushButton(self)
        self.add_button.setGeometry(80, 550, 371, 41)
        self.add_button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.add_button.setIcon(QIcon('images/add_button_icon.png'))
        self.add_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.add_button.setIconSize(self.add_button.size())
        self.add_button.clicked.connect(self.add_button_clicked)

        self.number_in_list_lineEdit = QLineEdit(self)
        self.number_in_list_lineEdit.setGeometry(640, 470, 241, 31)

        self.delete_button = QPushButton(self)
        self.delete_button.setGeometry(540, 505, 341, 41)
        self.delete_button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.delete_button.setIcon(QIcon('images/delete_button_icon.png'))
        self.delete_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.delete_button.setIconSize(self.delete_button.size())
        self.delete_button.clicked.connect(self.delete_button_clicked)

        self.already_button = QPushButton(self)
        self.already_button.setGeometry(540, 550, 341, 41)
        self.already_button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.already_button.setIcon(QIcon('images/already_button_icon.png'))
        self.already_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.already_button.setIconSize(self.delete_button.size())
        self.already_button.clicked.connect(self.already_button_clicked)

        font.setPointSize(18)
        self.search = QLabel(self)
        self.search.setGeometry(100, 10, 81, 31)
        self.search.setFont(font)
        self.search.setText("Поиск:")

        self.add_label = QLabel(self)
        self.add_label.setGeometry(10, 430, 501, 31)
        self.add_label.setFont(font)
        self.add_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.add_label.setText("Добавить")

        self.id_label = QLabel(self)
        self.id_label.setGeometry(20, 470, 81, 31)
        self.id_label.setFont(font)
        self.id_label.setText("ID:")

        self.weight_label = QLabel(self)
        self.weight_label.setGeometry(20, 510, 81, 31)
        self.weight_label.setFont(font)
        self.weight_label.setText("Вес(г):")

        self.delete_label = QLabel(self)
        self.delete_label.setGeometry(530, 430, 361, 31)
        self.delete_label.setFont(font)
        self.delete_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.delete_label.setText("Удалить")

        self.number_label = QLabel(self)
        self.number_label.setGeometry(540, 470, 91, 31)
        self.number_label.setFont(font)
        self.number_label.setText("Number:")

        self.product_table = QTableWidget(self)
        self.product_table.setGeometry(10, 90, 501, 341)
        self.product_table.horizontalHeader().setDefaultSectionSize(77)
        self.product_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.product_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.refresh_button_clicked()
        for i in range(6):
            self.product_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)

    # функция обновления таблицы с продуктами
    def refresh_button_clicked(self):
        con = sqlite3.connect("database.sqlite")
        cur = con.cursor()
        result = [*cur.execute(f"""SELECT * FROM products""")]
        self.product_table.setColumnCount(len(result[0]))
        self.product_table.setRowCount(len(result))
        self.product_table.clear()
        for row, item in enumerate(result):
            for col, value in enumerate(item):
                item = QTableWidgetItem(str(value))
                self.product_table.setItem(row, col, item)
        self.product_table.setHorizontalHeaderLabels(["ID", "name", "calories", "proteins", "fats", "carbs"])
        con.close()
        self.search_lineEdit.setText("")

    # фукция для поиска продукта по его названию
    def search_button_clicked(self):
        con = sqlite3.connect("database.sqlite")
        cur = con.cursor()
        result = [*cur.execute(f"""SELECT * FROM products WHERE name LIKE '%{self.search_lineEdit.text()}%'""")]
        self.product_table.setColumnCount(0)
        if len(result) > 0:
            self.product_table.setColumnCount(len(result[0]))
        self.product_table.setRowCount(len(result))
        self.product_table.clear()
        for row, item in enumerate(result):
            for col, value in enumerate(item):
                item = QTableWidgetItem(str(value))
                self.product_table.setItem(row, col, item)
        self.product_table.setHorizontalHeaderLabels(["ID", "name", "calories", "proteins", "fats", "carbs"])
        con.close()

    # функция добавления в лист продукта в приеме пищи
    def add_button_clicked(self):
        global error
        con = sqlite3.connect("database.sqlite")
        cur = con.cursor()
        if self.id_lineEdit.text() in [str(i[0]) for i in cur.execute("SELECT id from products").fetchall()]:
            product = cur.execute(f"""SELECT name FROM products WHERE id = {self.id_lineEdit.text()}""").fetchone()[0]
            if product in [i[0] for i in self.text] and self.weight_lineEdit.text().isnumeric():
                for i in self.text:
                    if i[0] == product:
                        i[1] += int(self.weight_lineEdit.text())
                        break
            elif self.weight_lineEdit.text().isnumeric():
                self.text.append([product, int(self.weight_lineEdit.text())])
            else:
                error = ErrorMessage()
                error.set_message("Некорректный ввод!")
                error.show()
            self.refresh_list()
        else:
            error = ErrorMessage()
            error.set_message("Некорректный ввод!")
            error.show()
        con.close()

    # функция для обновления листа
    def refresh_list(self):
        self.list.setColumnCount(2)
        self.list.setRowCount(len(self.text))
        for row, item in enumerate(self.text):
            for col, value in enumerate(item):
                item = QTableWidgetItem(str(value))
                self.list.setItem(row, col, item)

    # кнопка удаления лишнего продукта в приеме пищи по индексу
    def delete_button_clicked(self):
        global error
        if not self.number_in_list_lineEdit.text().isdigit():
            error = ErrorMessage()
            error.set_message("Некорректный ввод данных!")
            error.show()
        elif 1 > int(self.number_in_list_lineEdit.text()) or int(self.number_in_list_lineEdit.text()) > len(self.text):
            error = ErrorMessage()
            error.set_message("Неправильный индекс!")
            error.show()
        else:
            self.text.pop(int(self.number_in_list_lineEdit.text()) - 1)
            self.refresh_list()

    # функция добавления всего КБЖУ в базу данных для пользователя
    def already_button_clicked(self):
        con = sqlite3.connect("database.sqlite")
        cur = con.cursor()
        cpfc = [0, 0, 0, 0]
        for i in self.text:
            cpfc[0] += int(cur.execute(f"""SELECT calories FROM products 
            WHERE name = '{i[0]}'""").fetchone()[0] * i[1] / 100)
            cpfc[1] += float(cur.execute(f"""SELECT proteins FROM products 
            WHERE name = '{i[0]}'""").fetchone()[0] * i[1] / 100)
            cpfc[2] += float(cur.execute(f"""SELECT fats FROM products 
            WHERE name = '{i[0]}'""").fetchone()[0] * i[1] / 100)
            cpfc[3] += float(cur.execute(f"""SELECT carbohydrates FROM products 
            WHERE name = '{i[0]}'""").fetchone()[0] * i[1] / 100)
        cur.execute(f"""UPDATE days_stats SET calories = calories + {cpfc[0]},
            proteins = proteins + {cpfc[1]}, fats = fats + {cpfc[2]}, carbohydrates = carbohydrates + {cpfc[3]}
            WHERE name = '{open('login.txt', 'r').read()}' AND day = '{date.today()}'""")
        con.commit()
        self.text.clear()
        self.refresh_list()
        con.close()

    # кнопка Назад
    def back_button_clicked(self):
        global main_window
        main_window = CalorieCounter()
        main_window.show()
        self.close()


# класс окна со статистикой
class Statistics(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Statistics")
        self.setFixedSize(1100, 600)
        self.move((get_monitors()[0].width - self.width()) // 2, (get_monitors()[0].height - self.height()) // 2)
        self.background = QLabel(self)
        self.background.setGeometry(0, 0, self.width(), self.height())
        self.background.setPixmap(QPixmap('images/Statistics_background_image.png'))
        self.setWindowIcon(QIcon("images/Statistic_window_icon.png"))

        font.setPointSize(24)
        con = sqlite3.connect("database.sqlite")
        cur = con.cursor()

        self.back_button = QPushButton(self)
        self.back_button.setGeometry(10, 10, 71, 71)
        self.back_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.back_button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.back_button.setIcon(QIcon('images/back_icon.png'))
        self.back_button.setIconSize(self.back_button.size())
        self.back_button.clicked.connect(self.back_button_clicked)

        self.days_list_with_stats = QListWidget(self)
        self.days_list_with_stats.setGeometry(10, 90, 601, 501)
        self.days_list_with_stats.setFont(font)
        self.days_list_with_stats.setStyleSheet(list_style)
        self.days_list_with_stats.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        for i in list(cur.execute(f"""SELECT * from days_stats WHERE name == '{list(open("login.txt", 'r'))[0]}'"""))[::-1]:
            data = i[2].split('-')
            message = f"""Дата:\t{data[2]}.{data[1]}.{data[0]}
Calories:\t\t{round(i[3], 2)} ККал
Proteins:\t\t{round(i[4], 2)} г
Fats:\t\t\t{round(i[5], 2)} г
Carbohydrates:\t{round(i[6], 2)} г"""
            self.days_list_with_stats.addItem(message)

        self.main_label = QLabel(self)
        self.main_label.setGeometry(80, 10, 941, 71)
        self.main_label.setFont(font)
        self.main_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_label.setText("Статистика")

        font.setPointSize(16)
        stats = []
        for i in range(-6, 1):
            arr = list(cur.execute(f"""SELECT * from days_stats WHERE name == '{list(open('login.txt', 'r'))[0]}' AND
             day == '{date.today() + datetime.timedelta(days=i)}'"""))
            if arr:
                stats.append([arr[0][3], arr[0][4], arr[0][5], arr[0][6]])
            else:
                stats.append([0, 0, 0, 0])

        self.Calories_graphic = PlotWidget(self)
        self.Calories_graphic.setGeometry(620, 130, 231, 192)
        self.Calories_graphic.setInteractive(False)
        self.Calories_graphic.setBackground('white')
        self.Calories_graphic.plot([i for i in range(1, 8)], [i[0] for i in stats], pen='black')

        self.Calories_label = QLabel(self)
        self.Calories_label.setGeometry(620, 90, 231, 31)
        self.Calories_label.setFont(font)
        self.Calories_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.Calories_label.setText("Calories")

        self.Proteins_graphic = PlotWidget(self)
        self.Proteins_graphic.setGeometry(860, 130, 231, 192)
        self.Proteins_graphic.setInteractive(False)
        self.Proteins_graphic.setBackground('white')
        self.Proteins_graphic.plot([i for i in range(1, 8)], [i[1] for i in stats], pen='black')

        self.Proteins_label = QLabel(self)
        self.Proteins_label.setGeometry(860, 90, 231, 31)
        self.Proteins_label.setFont(font)
        self.Proteins_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.Proteins_label.setText("Proteins")

        self.Fats_graphic = PlotWidget(self)
        self.Fats_graphic.setGeometry(620, 390, 231, 192)
        self.Fats_graphic.setInteractive(False)
        self.Fats_graphic.setBackground('white')
        self.Fats_graphic.plot([i for i in range(1, 8)], [i[2] for i in stats], pen='black')

        self.fats_label = QLabel(self)
        self.fats_label.setGeometry(620, 350, 231, 31)
        self.fats_label.setFont(font)
        self.fats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fats_label.setText("Fats")

        self.Carbohydrates_graphic = PlotWidget(self)
        self.Carbohydrates_graphic.setGeometry(860, 390, 231, 192)
        self.Carbohydrates_graphic.setInteractive(False)
        self.Carbohydrates_graphic.setBackground('white')
        self.Carbohydrates_graphic.plot([i for i in range(1, 8)], [i[3] for i in stats], pen='black')

        self.Carbohydrates_label = QLabel(self)
        self.Carbohydrates_label.setGeometry(860, 350, 231, 31)
        self.Carbohydrates_label.setFont(font)
        self.Carbohydrates_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.Carbohydrates_label.setText("Carbohydrates")

        con.close()

    # кнопка Назад
    def back_button_clicked(self):
        global main_window
        main_window = CalorieCounter()
        main_window.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    if not list(open("login.txt", "r")):
        registration_window = Registration()
        registration_window.show()
    else:
        main_window = CalorieCounter()
        main_window.show()
    sys.exit(app.exec())
