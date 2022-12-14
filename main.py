from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QThread
from PySide6.QtGui import Qt
from PySide6.QtCharts import QChartView, QChart, QLineSeries

import webbrowser
import pygetwindow
import configparser

from UI.main.ui_main import Ui_MainWindow
from UI.WindowRecordUi.window_record import Ui_Window_Record
from UI.AddWindowUi.add_window import UiAddWindow

from PytrackUtils.config_helper import edit_config
from PytrackUtils.window_record_reader import *
from PytrackUtils.window_type import *

from PyTrackMain import PyTrackWorker, PointChecker


class PytrackMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Pytrack")
        self.main_loop_active = False

        self.pytrack_worker = PyTrackWorker(self)
        self.pytrack_worker_thread = QThread()
        self.point_checker_worker = PointChecker(self)
        self.point_checker_worker_thread = QThread()

        # setting text and placeholder texts
        self.button_activate_deactivate_main_loop.setText("Activate")
        self.line_edit_point_threshold_break.setPlaceholderText(
            str(self.pytrack_worker.point_tracker.POINT_THRESHOLD_TAKE_A_BREAK)
        )
        self.line_edit_point_threshold_warning.setPlaceholderText(
            str(self.pytrack_worker.point_tracker.POINT_THRESHOLD_GET_BACK_TO_WORK)
        )

        # set combo box items
        combo_box_date_items = ["today", "yesterday", "this week", "this month", "all"]
        self.comboBox_date.addItems(combo_box_date_items)
        combo_box_type_items = ["all", "bad", "good"]
        self.comboBox_type.addItems(combo_box_type_items)
        self.get_records("today", "all")

        # set Charts
        self.point_line_series = QLineSeries()
        chart = QChart()
        chart.addSeries(self.point_line_series)
        chart.setTitle("Points Over Time")
        chart_view = QChartView()
        chart_view.setChart(chart)
        self.point_graph_container_layout.addWidget(chart_view)

        # setting the button signals to slots
        self.button_go_to_home.clicked.connect(self.go_to_home_page)  # type: ignore
        self.button_go_to_analytics.clicked.connect(self.go_to_analytics_page)  # type: ignore
        self.button_go_to_settings.clicked.connect(self.go_to_settings_page)  # type: ignore
        self.button_activate_deactivate_main_loop.clicked.connect(self.activate_deactivate_main_loop)  # type: ignore
        self.button_activate_deactivate_main_loop.clicked.connect(self.pytrack_worker.main_loop)  # type: ignore
        self.button_activate_deactivate_main_loop.clicked.connect(self.point_checker_worker.point_checking_loop)  # type: ignore
        self.point_checker_worker.looped.connect(
            self.copy_line_series
        )  # this signal is used for the point checking loop
        self.button_settings_general.clicked.connect(self.go_to_settings_general)  # type: ignore
        self.button_settings_window.clicked.connect(self.go_to_settings_window)  # type: ignore
        self.button_settings_about.clicked.connect(self.go_to_settings_about)  # type: ignore
        self.button_link_to_twitter.clicked.connect(self.go_to_link_twitter)  # type: ignore
        self.button_link_to_github.clicked.connect(self.go_to_link_github)  # type: ignore
        self.button_link_to_youtube_video.clicked.connect(self.go_to_link_youtube_video)  # type: ignore
        self.button_link_to_youtube_channel.clicked.connect(self.go_to_link_youtube_channel)  # type: ignore
        self.button_link_to_github_repository.clicked.connect(self.go_to_link_github_repository)  # type: ignore
        self.button_add_windows.clicked.connect(self.add_windows)  # type: ignore
        # setting the text edit signals to slots
        self.line_edit_point_threshold_break.editingFinished.connect(self.edit_point_threshold_break)  # type: ignore
        self.line_edit_point_threshold_warning.editingFinished.connect(self.edit_point_threshold_warning)  # type: ignore
        # set combo box signals to slots
        self.comboBox_date.currentTextChanged.connect(self.combo_box_date_updates)  # type: ignore
        self.comboBox_type.currentTextChanged.connect(self.combo_box_type_updates)  # type: ignore

        # move workers to their threads and start the threads
        self.pytrack_worker.moveToThread(self.pytrack_worker_thread)
        self.pytrack_worker_thread.start()
        self.point_checker_worker.moveToThread(self.point_checker_worker_thread)
        self.point_checker_worker_thread.start()

        # show the window
        self.show()

    def go_to_home_page(self):
        print("to home page")
        self.stackedWidget.setCurrentWidget(self.page_home)

    def go_to_analytics_page(self):
        print("to analytics page")
        self.stackedWidget.setCurrentWidget(self.page_analytics)

    def go_to_settings_page(self):
        print("go to settings page")
        self.stackedWidget.setCurrentWidget(self.page_settings)

    def go_to_settings_general(self):
        print("go to general settings")
        self.page_settings_stacked_widget.setCurrentWidget(
            self.page_settings_stacked_widget_page_general
        )

    def go_to_settings_window(self):
        print("go to window settings")
        self.page_settings_stacked_widget.setCurrentWidget(
            self.page_settings_stacked_widget_page_window
        )

    def go_to_settings_about(self):
        print("go to about settings")
        self.page_settings_stacked_widget.setCurrentWidget(
            self.page_settings_stacked_widget_page_about
        )

    def go_to_link_twitter(self):
        # webbrowser.open("")
        pass

    def go_to_link_github(self):
        webbrowser.open("https://github.com/0CottonBuds")

    def go_to_link_youtube_video(self):
        webbrowser.open("")

    def go_to_link_youtube_channel(self):
        webbrowser.open("")

    def go_to_link_github_repository(self):
        webbrowser.open("https://github.com/0CottonBuds/pytrack")

    def edit_point_threshold_break(self):
        """edit the point threshold of break"""
        value = self.line_edit_point_threshold_break.text()
        print(f"changing point threshold for break to {value}")
        edit_config("./settings", "App", "break_threshold", value)
        self.pytrack_worker.point_tracker.read_settings_config_file()
        self.line_edit_point_threshold_break.setPlaceholderText(
            str(self.pytrack_worker.point_tracker.POINT_THRESHOLD_TAKE_A_BREAK)
        )
        self.line_edit_point_threshold_break.clear()

    def edit_point_threshold_warning(self):
        """edit the point threshold of warning"""
        value = self.line_edit_point_threshold_warning.text()
        print(f"changing point threshold for warning to {value}")

        config_obj = configparser.ConfigParser()
        config_obj.read("settingsConfig.ini")
        section_to_edit = config_obj["App"]
        section_to_edit["warning_threshold"] = value
        with open("settingsConfig.ini", "w") as config_file:
            config_obj.write(config_file)

        self.pytrack_worker.point_tracker.read_settings_config_file()
        self.line_edit_point_threshold_warning.setPlaceholderText(
            str(self.pytrack_worker.point_tracker.POINT_THRESHOLD_GET_BACK_TO_WORK)
        )
        self.line_edit_point_threshold_break.clear()

    def activate_deactivate_main_loop(self):
        if not self.main_loop_active:
            print("Activated")
            self.main_loop_active = True
            self.button_activate_deactivate_main_loop.setText("Deactivate")
        elif self.main_loop_active:
            print("Deactivated")
            self.main_loop_active = False
            self.button_activate_deactivate_main_loop.setText("Activate")

    def copy_line_series(self):
        print("copied")
        self.point_line_series = self.point_checker_worker.line_series

    def combo_box_date_updates(self, text):
        print(f"signal: {text}")
        self.get_records(
            self.comboBox_date.currentText(), self.comboBox_type.currentText()
        )

    def combo_box_type_updates(self, text):
        print(f"signal: {text}")
        self.get_records(
            self.comboBox_date.currentText(), self.comboBox_type.currentText()
        )

    def get_records(self, query_date: str, query_type: str):
        """Fetches records by query date and type using the window record fetcher class and updates the scroll area contents

        Parameters:
            query_date: (string) date to query ex. today, yesterday, etc
            query_type: (string) type to query ex. good, bad, all"""

        print("getting records")
        records: list[WindowRecord] = []
        fetcher = WindowRecordFetcher()
        dates = fetcher.get_dates(query_date)
        fetcher.format_records(fetcher.retrieve_all_raw_records_by_many_dates(dates))
        fetcher.filter_formatted_records_by_type(query_type)
        records = fetcher.formatted_records
        records = get_time_of_each_window(records)
        records = get_percentage_of_time_of_each_window(records)
        self.update_scroll_area_contents(records)

    def update_scroll_area_contents(self, records: list[WindowRecord]):
        """Updates the scroll area contents by the list of window records that is passed

        Parameters:
            records: (list[WindowRecord]) list of window records that contains the data to update the contents of the scroll area"""

        # clears the scroll area
        for i in reversed(range(self.scroll_area_contents_layout.count())):
            self.scroll_area_contents_layout.itemAt(i).widget().setParent(None)  # type: ignore

        print("updating contents")
        for record in records:
            obj = Ui_Window_Record()
            obj.label_name.setText(record.window_short_name)
            obj.label_total_time.setText(str(record.window_time_elapsed.get_time()))
            obj.progressBar.setValue(int(record.window_time_elapsed.percentage))

            self.scroll_area_contents_layout.addWidget(obj)
            self.scroll_area_contents_layout.setAlignment(
                obj, Qt.AlignmentFlag.AlignTop
            )

    def add_windows(self):
        """this function spawns add window ui in the add ui scroll area"""
        window_filter = WindowFilter(pygetwindow.getAllWindows())
        window_filter.full_filter()

        # clear the add window contents layout
        for i in reversed(range(self.add_window_contents_layout.count())):
            self.add_window_contents_layout.itemAt(i).widget().setParent(None)  # type: ignore

        for window in window_filter.windows:
            add_window_ui = UiAddWindow(window.title)
            self.add_window_contents_layout.addWidget(add_window_ui)


if __name__ == "__main__":
    app = QApplication()
    window = PytrackMainWindow()
    app.exec()
