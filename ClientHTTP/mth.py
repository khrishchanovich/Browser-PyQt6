import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *

class SimpleBrowser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Простой браузер")
        self.setGeometry(0, 0, 800, 600)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.add_new_tab()

        self.nav_bar = QToolBar()
        self.addToolBar(self.nav_bar)

        back_btn = QAction("Назад", self)
        back_btn.triggered.connect(self.current_browser().back)
        self.nav_bar.addAction(back_btn)

        forward_btn = QAction("Вперед", self)
        forward_btn.triggered.connect(self.current_browser().forward)
        self.nav_bar.addAction(forward_btn)

        reload_btn = QAction("Обновить", self)
        reload_btn.triggered.connect(self.current_browser().reload)
        self.nav_bar.addAction(reload_btn)

        home_btn = QAction("Домой", self)
        home_btn.triggered.connect(self.navigate_home)
        self.nav_bar.addAction(home_btn)

        new_tab_btn = QAction("Новая вкладка", self)
        new_tab_btn.triggered.connect(self.add_new_tab)
        self.nav_bar.addAction(new_tab_btn)

        close_tab_btn = QAction("Закрыть вкладку", self)
        close_tab_btn.triggered.connect(self.close_current_tab)
        self.nav_bar.addAction(close_tab_btn)

        bookmark_list_btn = QAction("Закладки", self)
        bookmark_list_btn.triggered.connect(self.show_bookmarks)
        self.nav_bar.addAction(bookmark_list_btn)

        bookmark_btn = QAction("Добавить в закладки", self)
        bookmark_btn.triggered.connect(self.add_to_bookmarks)
        self.nav_bar.addAction(bookmark_btn)

        history_btn = QAction("История", self)
        history_btn.triggered.connect(self.show_history)
        self.nav_bar.addAction(history_btn)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.nav_bar.addWidget(self.url_bar)

        self.search_engines = QComboBox()
        self.search_engines.addItems(["Google", "Yandex", "Mail.ru"])
        self.search_engines.activated.connect(self.navigate_home)
        self.nav_bar.addWidget(self.search_engines)


        self.history = []
        self.load_history()

        self.bookmarks = []
        self.load_bookmarks()

        self.load_search_engine()
        self.navigate_home()

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

        bookmarks_list = QListWidget()
        for bookmark in self.bookmarks:
            bookmarks_list.addItem(f"{bookmark[0]} - {bookmark[1]}")
        layout.addWidget(bookmarks_list)

        delete_btn = QPushButton("Удалить закладку")
        delete_btn.clicked.connect(lambda: self.delete_bookmark(bookmarks_list.currentRow()))
        layout.addWidget(delete_btn)

        bookmarks_dialog.setLayout(layout)
        bookmarks_dialog.exec_()

    def delete_bookmark(self, index):
        if index >= 0:
            del self.bookmarks[index]
            self.save_bookmarks()

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

    def add_new_tab(self):
        browser = QWebEngineView()
        browser.setUrl(QUrl("https://www.google.com"))
        browser.urlChanged.connect(lambda q, browser=browser: self.update_url_bar(browser, q))
        browser.titleChanged.connect(self.update_tab_title)
        self.tabs.addTab(browser, "Новая вкладка")
        self.tabs.setCurrentWidget(browser)

    def update_history(self, q):
        url = q.toString()
        title = self.current_browser().title()
        if (url, title) not in self.history:
            self.history.append((url, title))
            self.save_history()

    def current_browser(self):
        return self.tabs.currentWidget()

    def navigate_home(self):
        search_engine = self.search_engines.currentText()
        if search_engine == "Google":
            self.current_browser().setUrl(QUrl("https://www.google.com"))
        elif search_engine == "Yandex":
            self.current_browser().setUrl(QUrl("https://yandex.ru"))
        elif search_engine == "Mail.ru":
            self.current_browser().setUrl(QUrl("https://mail.ru"))

        self.save_search_engine()

    def navigate_to_url(self):
        text = self.url_bar.text()
        search_engine = self.search_engines.currentText()
        if "." not in text:
            if search_engine == "Google":
                url = QUrl("https://www.google.com/search?q=" + text)
            elif search_engine == "Yandex":
                url = QUrl("https://yandex.ru/search/?text=" + text)
            elif search_engine == "Mail.ru":
                url = QUrl("https://go.mail.ru/search?q=" + text)
        else:
            url = QUrl(text)

        self.current_browser().setUrl(url)
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
        self.history_list = QListWidget()

        self.history_list.itemClicked.connect(self.item_selected)
        self.history_list.itemDoubleClicked.connect(self.item_double_clicked)

        history_dialog = QDialog(self)
        history_dialog.setWindowTitle("История посещений")
        history_layout = QVBoxLayout()

        self.history_list.clear()
        for url, title in self.history:
            self.history_list.addItem(f"{title} - {url}")
        history_layout.addWidget(self.history_list)

        clear_btn = QPushButton("Очистить историю")
        clear_btn.clicked.connect(self.clear_history)
        history_layout.addWidget(clear_btn)

        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.clicked.connect(self.delete_selected_item)
        history_layout.addWidget(self.delete_btn)

        history_dialog.setLayout(history_layout)

        self.history_list.itemClicked.disconnect(self.item_selected)
        self.history_list.itemDoubleClicked.disconnect(self.item_double_clicked)

        self.history_list.itemClicked.connect(self.item_selected)
        self.history_list.itemDoubleClicked.connect(self.item_double_clicked)

        history_dialog.exec_()

    def item_selected(self, item):
        self.selected_item = item.text()

    def delete_selected_item(self):
        if hasattr(self, 'selected_item'):
            self.history.remove(self.selected_item)
            self.save_history()
            self.history_list.clear()
            for url in self.history:
                self.history_list.addItem(url)

    def item_double_clicked(self, item):
        if hasattr(self, 'selected_item'):
            url = QUrl(self.selected_item)
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

app = QApplication(sys.argv)
browser = SimpleBrowser()
browser.show()
sys.exit(app.exec_())
