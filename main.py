import sys  # sys нужен для передачи argv в QApplication
import threading

from PyQt5 import QtCore, QtWidgets, QtGui, Qt
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import QIODevice
from PyQt5.QtWidgets import QTableWidgetSelectionRange

import window  # Это наш конвертированный файл дизайна

import math
import sqlite3
import datetime
import time
from datetime import datetime

import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

serial = QSerialPort()

counterBlink = 0
counterDB = 0

period = 10

db = sqlite3.connect('database.db')
cursor = db.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS locations(
    date INT,
    X REAL,
    Y REAL,
    port TEXT
)''')
db.commit()


class Window(QtWidgets.QMainWindow, window.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        # self.running = None
        self.setFixedSize(1324, 716)
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("ico.png"))
        self.setWindowIcon(icon)
        self.exit_btn.clicked.connect(self.close_program)
        self.comboBox.currentTextChanged.connect(self.stop)
        self.open_btn.clicked.connect(self.open_port)
        self.close_btn.clicked.connect(self.close_port)
        self.find_ports()
        serial.readyRead.connect(self.on_read)
        self.update_plate()
        self.graphicsView.showGrid(x=True, y=True, alpha=0.5)
        self.tableWidget.setColumnWidth(0, 138)
        self.tableWidget.setColumnWidth(1, 100)
        self.tableWidget.setColumnWidth(2, 100)
        self.tableWidget.cellClicked.connect(self.select_row)
        self.tableWidget.cellDoubleClicked.connect(self.show_recorded_location)
        self.amount_lineEdit.textChanged.connect(self.lines_amount_changed)
        self.amount_lineEdit.keyPressEvent = self.key_press_event
        self.amont_accept_btn.clicked.connect(self.lines_amount_accept)
        self.period_lineEdit.textChanged.connect(self.period_lineedit_changed)
        self.period_accept_btn.clicked.connect(self.period_accept)
        self.size_x_lineEdit.textChanged.connect(self.size_lineedit_changed)
        self.size_y_lineEdit.textChanged.connect(self.size_lineedit_changed)
        self.size_accept_btn.clicked.connect(self.update_plate)
        self.play_animation_btn.clicked.connect(self.start_animation)
        self.stop_animation_btn.clicked.connect(self.stop_animation)
        self.tableWidget.setRowCount(25)
        self.graphicsView.setBackground('#1b1b1b')
        self.update_table()
        self.clear_plot()


    def find_ports(self):
        serial.setBaudRate(9600)
        port_list = []
        ports = QSerialPortInfo().availablePorts()
        for port in ports:
            port_list.append(port.portName())
        self.comboBox.addItems(port_list)

    def open_port(self):
        self.open_btn.setEnabled(False)
        self.close_btn.setEnabled(True)
        self.clear_plot()
        serial.setPortName(self.comboBox.currentText())
        serial.open(QIODevice.ReadWrite)

    def close_port(self):
        serial.close()
        self.open_btn.setEnabled(True)
        self.close_btn.setEnabled(False)
        self.clear_plot()

    @staticmethod
    def close_program():
        sys.exit(0)

    def on_read(self):
        self.update()
        rx = str(serial.readLine(), "utf-8").strip()
        data = rx.split(",")
        print(data[0], data[1])
        self.calculate_coordinates(data)

    def calculate_coordinates(self, data):
        global counterBlink
        global counterDB
        a = float(data[0])
        b = float(data[1])
        c = 100
        offset = 50
        diag = math.sqrt(150 * 150 + 100 * 100)
        p = (a + b + c) / 2
        area = math.sqrt(p * (p - a) * (p - b) * (p - c))
        y = round(area * 2 / c, 3)
        x = round(math.sqrt(b * b - y * y), 3)

        print("Сторона а:".ljust(26) + str(a))
        print("Сторона b:".ljust(26) + str(b))
        print("Основание:".ljust(26) + str(c))
        print("Расстояние до плоскости:".ljust(26) + str(offset))
        print("Полу периметр:".ljust(26) + str(p))
        print("Площадь:".ljust(26) + str(area))
        print("Координата Х:".ljust(26) + str(x))
        print("Координата Y:".ljust(26) + str(round(area * 2 / c - 50, 3)) + "\n")

        if counterDB == 0:
            cursor.execute(
                f'INSERT INTO locations VALUES ("{float(str(datetime.now().timestamp())[:10])}", "{x}", "{y}", "{self.comboBox.currentText()}")')
            # cursor.execute(f'INSERT INTO locations VALUES ("{datetime.now().strftime("%H:%M:%S %Y-%m-%d")}", "{x}", "{y}", "{self.comboBox.currentText()}")')
            self.update_table()
            counterDB += 1
        elif counterDB < period - 1:
            counterDB += 1
        else:
            counterDB = 0
        db.commit()
        if counterBlink == 0:
            self.draw(x, y)
            counterBlink += 1
        else:
            self.clear_plot()
            counterBlink -= 1

    def draw(self, x, y):
        self.graphicsView.plot([x], [y - 50], symbol='t1', symbolBrush=5, name='point', symbolSize=30)

    def clear_plot(self):
        self.graphicsView.clear()

    def update_table(self):
        sqlquery = f'SELECT * FROM locations WHERE port = "{self.comboBox.currentText()}" ORDER BY date DESC LIMIT {self.amount_lineEdit.text()}'
        self.tableWidget.setRowCount(25)

        table_row = 0
        for row in cursor.execute(sqlquery):
            # self.tableWidget.setItem(table_row, 0, QtWidgets.QTableWidgetItem(str(row[0])))
            self.tableWidget.setItem(table_row, 0, QtWidgets.QTableWidgetItem(
                datetime.utcfromtimestamp(int(row[0])).strftime('%H:%M:%S %Y-%m-%d'), ))
            self.tableWidget.setItem(table_row, 1, QtWidgets.QTableWidgetItem(str(row[1])))
            self.tableWidget.setItem(table_row, 2, QtWidgets.QTableWidgetItem(str(row[2])))
            self.tableWidget.setRowHeight(table_row, 50)
            self.tableWidget.verticalHeader().hide()
            table_row += 1

    def select_row(self, row):
        self.tableWidget.setRangeSelected(
            QTableWidgetSelectionRange(row, 0, row, self.tableWidget.columnCount() - 1), 1
        )

    def show_recorded_location(self, row, column):
        self.clear_plot()
        self.draw(float(self.tableWidget.item(row, 1).text()), float(self.tableWidget.item(row, 2).text()))

    def stop(self):
        self.close_port()
        self.clear_plot()
        self.tableWidget.setRowCount(0)
        self.update_table()

    def lines_amount_accept(self):
        self.tableWidget.setRowCount(int(self.amount_lineEdit.text()))
        self.update_table()
        self.amont_accept_btn.setEnabled(False)

    def lines_amount_changed(self):
        self.amont_accept_btn.setEnabled(True)

    def period_lineedit_changed(self):
        self.period_accept_btn.setEnabled(True)

    def period_accept(self):
        global period
        period = int(self.period_lineEdit.text())
        self.period_accept_btn.setEnabled(False)

    def size_lineedit_changed(self):
        self.size_accept_btn.setEnabled(True)

    def update_plate(self):
        self.graphicsView.setXRange(0, int(self.size_x_lineEdit.text()), padding=0)
        self.graphicsView.setYRange(0, int(self.size_y_lineEdit.text()), padding=0)
        self.size_accept_btn.setEnabled(False)

    def start_animation(self):
        self.animation_thread = threading.Thread(target=self.animation, daemon=True)
        self.animation_thread.start()

    def stop_animation(self):
        self.clear_plot()
        self.play_animation_btn.setEnabled(True)
        self.stop_animation_btn.setEnabled(False)
        self.running = False

    def animation(self):
        self.play_animation_btn.setEnabled(False)
        self.stop_animation_btn.setEnabled(True)
        self.running = True
        row = self.tableWidget.rowCount() - 1
        hui = float(self.tableWidget.item(row, 1).text())
        while self.running:
            if row == 0:
                self.clear_plot()
                self.graphicsView.repaint()
                self.play_animation_btn.setEnabled(True)
                self.stop_animation_btn.setEnabled(False)
                self.running = False
            self.graphicsView.repaint()
            self.draw(float(self.tableWidget.item(row, 1).text()), float(self.tableWidget.item(row, 2).text()))
            time.sleep(0.5)
            self.clear_plot()
            # self.tableWidget.clearSelection()
            row -= 1

    def key_press_event(self, event):
        sender = self.sender()
        self.statusBar().showMessage(sender.text() + ' was pressed')


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    app.setStyle('Fusion')
    window = Window()  # Создаём объект класса ExampleApp
    # app.setAttribute(QtCore.Qt.AA_Use96Dpi)
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
