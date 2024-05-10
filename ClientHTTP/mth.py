import os
import re
import sys


from PyQt6.QtWebEngineWidgets import *
from PyQt6.QtGui import QAction
from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest
from PyQt6.QtCore import QUrl, QDir, QFileInfo, QTimer
from PyQt6.QtWebEngineWidgets import *

from PyQt6.QtPrintSupport import QPrintPreviewDialog
from PyQt6.QtWidgets import *
from requests import get
from bs4 import BeautifulSoup

import socket


def check_internet_connection(host="www.google.com", port=80, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False


class SimpleBrowser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Браузер")
        self.setGeometry(0, 0, 800, 600)

        self.i = 1

        self.browser = QWebEngineView()

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        browser = QWebEngineView()
        self.tabs.addTab(browser, "Новая вкладка")
        self.tabs.setCurrentWidget(browser)

        browser.setUrl(QUrl("http://www.google.com"))

        browser.urlChanged.connect(lambda q, browser=browser: self.update_url_bar(browser, q))
        browser.titleChanged.connect(self.update_tab_title)

        self.nav_bar_top = QToolBar()
        self.addToolBar(self.nav_bar_top)

        self.nav_bar_bottom = QToolBar()
        self.addToolBar(self.nav_bar_bottom)

        self.nav_bar_top.setGeometry(10,10,200,30)

        # self.nav_bar_top.setMovable(False)
        # self.nav_bar_bottom.setMovable(False)

        self.back_btn = QPushButton("Назад")
        self.back_btn.clicked.connect(self.navigate_back)
        self.nav_bar_top.addWidget(self.back_btn)

        self.forward_btn = QPushButton("Вперед")
        self.forward_btn.clicked.connect(self.navigate_forward)
        self.nav_bar_top.addWidget(self.forward_btn)

        self.reload_btn = QPushButton("Обновить")
        self.reload_btn.clicked.connect(self.tabs.currentWidget().reload)
        self.nav_bar_top.addWidget(self.reload_btn)

        self.home_btn = QPushButton("Домой")
        self.home_btn.clicked.connect(self.navigate_home)
        self.nav_bar_top.addWidget(self.home_btn)

        # self.add_new_tab()

        new_tab_btn = QPushButton("Новая вкладка")
        new_tab_btn.clicked.connect(self.add_new_tab)
        self.nav_bar_bottom.addWidget(new_tab_btn)

        close_tab_btn = QPushButton("Закрыть вкладку")
        close_tab_btn.clicked.connect(self.close_current_tab)
        self.nav_bar_bottom.addWidget(close_tab_btn)

        bookmark_list_btn = QPushButton("Закладки")
        bookmark_list_btn.clicked.connect(self.show_bookmarks)
        self.nav_bar_bottom.addWidget(bookmark_list_btn)

        bookmark_btn = QPushButton("Добавить в закладки")
        bookmark_btn.clicked.connect(self.add_to_bookmarks)
        self.nav_bar_bottom.addWidget(bookmark_btn)

        history_btn = QPushButton("История")
        history_btn.clicked.connect(self.show_history)
        self.nav_bar_bottom.addWidget(history_btn)

        open_file_btn = QPushButton("Открыть файл")
        open_file_btn.clicked.connect(self.open_local_file)
        self.nav_bar_bottom.addWidget(open_file_btn)

        save_page_html_btn = QPushButton("Сохранить страницу (html)")
        save_page_html_btn.clicked.connect(self.save_page)
        self.nav_bar_bottom.addWidget(save_page_html_btn)

        save_page_pdf_btn = QPushButton("Сохранить страницу (pdf)")
        save_page_pdf_btn.clicked.connect(self.save_page_as_pdf)
        self.nav_bar_bottom.addWidget(save_page_pdf_btn)
        #
        # print_page_btn = QPushButton("Печать")
        # print_page_btn.clicked.connect(self.print_preview)
        # self.nav_bar_bottom.addWidget(print_page_btn)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.nav_bar_top.addWidget(self.url_bar)

        self.search_engines = QComboBox()
        self.search_engines.setEnabled(True)
        #
        # self.search_engines.addItems(["Google", "Yandex"])
        # self.search_engines.activated.connect(self.navigate_home)
        # self.nav_bar_top.addWidget(self.search_engines)

        self.request = None

        self.downloading = False
        self.browser_download_manager = QWebEngineView()
        self.browser_download_manager.page().profile().downloadRequested.connect(
            self.download_requested)

        self.download_timer = QTimer()
        self.download_timer.timeout.connect(self.update_download_progress)

        self.history = []
        self.load_history()

        self.bookmarks = []
        self.load_bookmarks()

        self.load_search_engine()
        self.navigate_home()


    def download_requested(self, request: QWebEngineDownloadRequest):
        if self.downloading:
            QMessageBox.warning(self, "Предупреждение", "Загрузка уже идет")
            return

        self.downloading = True

        self.request = request

        url = request.url()
        file_name = QFileInfo(url.path()).fileName()
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить файл", QDir.homePath() + "/" + file_name)

        if file_path:
            download_path = QDir.toNativeSeparators(file_path)
            request.setDownloadFileName(download_path)
            request.accept()

            self.progress_dialog = QProgressDialog(self)
            self.progress_dialog.setWindowTitle('Загрузка файла...')
            self.progress_dialog.setLabelText('Загрузка файла...')
            self.progress_dialog.setAutoReset(False)
            self.progress_dialog.setAutoClose(True)

            self.progress_dialog.setMinimum(0)
            self.progress_dialog.setMaximum(0)
            self.progress_dialog.setValue(0)

            self.progress_dialog.canceled.connect(lambda: self.cancel_download(request))

            self.progress_dialog.show()

            self.download_timer.start(1000)

    def update_download_progress(self):
        bytes_received = self.request.receivedBytes()
        bytes_total = self.request.totalBytes()
        progress = int((bytes_received / bytes_total) * 100)
        self.progress_dialog.setValue(progress)
        if progress >= 100:
            self.download_timer.stop()
            self.downloading = False
            self.progress_dialog.close()

    def download_finished(self):
        self.downloading = False
        self.progress_dialog.close()

    def cancel_download(self, request: QWebEngineDownloadRequest):
        if request:
            request.cancel()
        self.downloading = False
        self.progress_dialog.close()

    def save_page_as_pdf(self):
        filename, filter = QFileDialog.getSaveFileName(
            parent=self, caption="Save as", filter="PDF File (*.pdf);;All files (*.*)"
        )

        self.tabs.currentWidget().page().printToPdf(filename)

    def handle_pdf_save(self, success):
        if success:
            QMessageBox.information(self, "Успех", "Страница успешно сохранена в формате PDF.")
        else:
            QMessageBox.warning(self, "Ошибка", "Ошибка при сохранении страницы в формате PDF.")

    def save_page(self):
        file_path, filter = QFileDialog.getSaveFileName(
            parent=self, caption="Save as", filter="HTML Files (*.html *.htm)"
        )

        if file_path:
            self.current_browser().page().toHtml(lambda html: self.write_html_to_file(html, file_path))

    def write_html_to_file(self, html, file_path):
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(html)
            QMessageBox.information(self, "Успех", "Страница успешно сохранена.")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Возникла ошибка при сохранении страницы: {str(e)}")

    def open_local_file(self):
        browser = QWebEngineView()

        file_path, _ = QFileDialog.getOpenFileName(self, "Открыть HTML-файл", "", "HTML Files (*.html *.htm)")
        print("File Path:", file_path)  # Add this line to check the file path
        if file_path:
            browser.setUrl(QUrl.fromLocalFile(file_path))
            self.url_bar.setText('file:///' + file_path)
            browser.titleChanged.connect(self.update_tab_title)

            self.tabs.addTab(browser, "Новая вкладка")
            self.tabs.setCurrentWidget(browser)

    def add_to_bookmarks(self):
        current_url = self.current_browser().url().toString()
        current_title = self.current_browser().title()
        bookmark_name, ok = QInputDialog.getText(self, "Добавить в закладки", "Введите название закладки:")
        if ok and bookmark_name:
            self.bookmarks.append((bookmark_name, current_url, current_title))
            self.save_bookmarks()

    def show_bookmarks(self):
        bookmarks_dialog = QDialog(self)
        bookmarks_dialog.setWindowTitle("Закладки")
        layout = QVBoxLayout()

        self.bookmarks_list = QListWidget()

        self.bookmarks_list.itemClicked.connect(self.item_selected)
        self.bookmarks_list.itemDoubleClicked.connect(self.item_double_clicked)

        for bookmark in self.bookmarks:
            self.bookmarks_list.addItem(f"{bookmark[0]} - {bookmark[1]}")
        layout.addWidget(self.bookmarks_list)

        delete_btn = QPushButton("Удалить закладку")
        delete_btn.clicked.connect(lambda: self.delete_bookmark(self.bookmarks_list.currentRow()))
        layout.addWidget(delete_btn)

        bookmarks_dialog.setLayout(layout)

        self.bookmarks_list.itemClicked.disconnect(self.item_selected)
        self.bookmarks_list.itemDoubleClicked.disconnect(self.item_double_clicked)

        self.bookmarks_list.itemClicked.connect(self.item_selected)
        self.bookmarks_list.itemDoubleClicked.connect(self.item_double_clicked)

        bookmarks_dialog.exec()

    def delete_bookmark(self, index):
        if index >= 0 and index < len(self.bookmarks):
            del self.bookmarks[index]
            self.save_bookmarks()
            # Update the bookmarks list in the dialog
            self.bookmarks_list.clear()
            for bookmark in self.bookmarks:
                self.bookmarks_list.addItem(f"{bookmark[0]} - {bookmark[1]}")

    def load_bookmarks(self):
        try:
            with open("bookmarks.txt", "r") as file:
                for line in file.readlines():
                    parts = line.strip().split(",")
                    if len(parts) == 3:
                        self.bookmarks.append((parts[0], parts[1], parts[2]))
        except FileNotFoundError:
            pass

    def save_bookmarks(self):
        with open("bookmarks.txt", "w") as file:
            for bookmark in self.bookmarks:
                file.write(f"{bookmark[0]},{bookmark[1]},{bookmark[2]}\n")
        print("Закладки сохранены в файл")

    def load_search_engine(self):
        try:
            with open("search_engine.txt", "r") as file:
                search_engine = file.read().strip()
                index = self.search_engines.findText(search_engine)
                if index != -1:
                    self.search_engines.setCurrentIndex(index)
        except FileNotFoundError:
            pass

    def save_search_engine(self):
        search_engine = self.search_engines.currentText()
        with open("search_engine.txt", "w") as file:
            file.write(search_engine)

    def bind_navigation_buttons(self, browser):
        self.back_btn.clicked.connect(self.navigate_back)
        self.forward_btn.clicked.connect(self.navigate_forward)
        self.reload_btn.clicked.connect(browser.reload)
        self.home_btn.clicked.connect(self.navigate_home)

    def navigate_back(self):
        current_browser = self.current_browser()
        current_browser.back()

    def navigate_forward(self):
        current_browser = self.current_browser()
        current_browser.forward()

    def add_new_tab(self):
        browser = QWebEngineView()

        self.tabs.addTab(browser, "Новая вкладка")
        self.tabs.setCurrentWidget(browser)
        self.tabs.setCurrentIndex(self.i)
        self.i += 1
        self.bind_navigation_buttons(self.tabs.currentWidget())

        with open("search_engine.txt", "r") as file:
            search_engine = file.readline()

            if search_engine == 'Google':
                browser.setUrl(QUrl("http://www.google.com"))
            elif search_engine == 'Yandex':
                browser.setUrl(QUrl("http://www.yandex.ru"))

        browser.urlChanged.connect(lambda q, browser=browser: self.update_url_bar(browser, q))
        browser.titleChanged.connect(self.update_tab_title)

    def update_history(self, q):
        url = q.toString()

        response = get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title.string
        # title = self.current_browser().windowTitle()
        # title = self.current_browser().title()
        # title = self.tabs.currentWidget().page().title()
        if (title, url) not in self.history:
            self.history.append((title, url))
            self.save_history()

    def current_browser(self):
        return self.tabs.currentWidget()

    def navigate_home(self):
        # Проверяем, есть ли вкладки в браузере
        if self.tabs.count() > 0:
            # Получаем текущий объект QWebEngineView
            browser = self.current_browser()
            # Устанавливаем URL домашней страницы
            browser.setUrl(QUrl("http://www.google.com"))  # Или другой URL вашей домашней страницы
            # Обновляем адресную строку и заголовок вкладки
            self.url_bar.setText(browser.url().toString())
            self.update_tab_title(browser.page().title())
            # Сохраняем историю
            self.save_history()
        else:
            # Если вкладок нет, просто добавляем новую вкладку с домашним URL
            self.add_new_tab()

    def navigate_to_url(self):
        # browser = QWebEngineView()
        browser = self.current_browser()
        text = self.url_bar.text()
        if 'http' in text or 'https' in text:
            url = QUrl(text)
        else:
            url = QUrl("https://www.google.com/search?q=" + text)

        browser.setUrl(url)

        # browser.urlChanged.connect(lambda q, browser=browser: self.update_url_bar(browser, q))
        # browser.titleChanged.connect(self.update_tab_title)
        #
        # self.tabs.addTab(browser, "Новая вкладка")
        # self.tabs.setCurrentWidget(browser)

        self.update_url_bar(browser, url)
        self.update_tab_title(browser.page().title())

        self.save_history()

    def update_url_bar(self, browser, q):
        index = self.tabs.indexOf(browser)
        if index != -1:
            self.url_bar.setText(q.toString())
            url = QUrl(self.url_bar.text())
            self.update_history(url)

    def update_tab_title(self, title):
        index = self.tabs.currentIndex()
        if index != -1:
            self.tabs.setTabText(index, title)

    def close_current_tab(self):
        current_index = self.tabs.currentIndex()
        if current_index != -1:
            widget = self.tabs.widget(current_index)
            widget.deleteLater()
            self.tabs.removeTab(current_index)

    def show_history(self):
        history_dialog = QDialog(self)
        history_dialog.setWindowTitle("История")
        layout = QVBoxLayout()

        self.history_list = QListWidget()

        self.history_list.itemClicked.connect(self.item_selected)
        self.history_list.itemDoubleClicked.connect(self.item_double_clicked)

        for item in self.history:
            self.history_list.addItem(f"{item[0]} - {item[1]}")
        layout.addWidget(self.history_list)

        delete_btn = QPushButton("Удалить элемент из истории")
        delete_btn.clicked.connect(lambda: self.delete_selected_item(self.history_list.currentRow()))
        layout.addWidget(delete_btn)

        clear_btn = QPushButton("Очистить историю")
        clear_btn.clicked.connect(self.clear_history)
        layout.addWidget(clear_btn)

        history_dialog.setLayout(layout)

        self.history_list.itemClicked.disconnect(self.item_selected)
        self.history_list.itemDoubleClicked.disconnect(self.item_double_clicked)

        self.history_list.itemClicked.connect(self.item_selected)
        self.history_list.itemDoubleClicked.connect(self.item_double_clicked)

        history_dialog.exec()

    def item_selected(self, item):
        self.selected_item = item.text()

    def delete_selected_item(self, index):
        if index >= 0 and index < len(self.history):
            del self.history[index]
            self.save_history()
            self.history_list.clear()
            for item in self.history:
                self.history_list.addItem(f"{item[0]} - {item[1]}")

    def item_double_clicked(self, item):
        if hasattr(self, 'selected_item'):
            print(self.selected_item)
            get_title, get_url = self.selected_item.split(' - h', 1)
            print('1', get_title, '2', get_url)
            url = QUrl('h' + get_url)
            print(url)
            self.current_browser().setUrl(url)
            self.save_history()

    def clear_history(self):
        self.history = []
        self.save_history()
        self.history_list.clear()

    def load_history(self):
        try:
            with open("history.txt", "r") as file:
                for line in file.readlines():
                    url, title = line.strip().split(",")
                    self.history.append((url, title))
        except FileNotFoundError:
            pass

    def save_history(self):
        with open("history.txt", "w") as file:
            for url, title in self.history:
                file.write(f"{url},{title}\n")
        print("История сохранена в файл")


if check_internet_connection():
    app = QApplication(sys.argv)
    browser = SimpleBrowser()
    browser.show()
    sys.exit(app.exec())
else:
    print("Отсутствует подключение к интернету. Некоторые функции могут быть недоступны.")