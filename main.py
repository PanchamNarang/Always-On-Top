import sys
import pygetwindow as gw
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QComboBox
from PyQt5.QtCore import QTimer
import win32api  # Add this
import win32gui
import win32con


def set_always_on_top(hwnd):
    if hwnd:
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

def remove_always_on_top(hwnd):
    if hwnd:
        win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

def is_window_fullscreen(hwnd):
    rect = win32gui.GetWindowRect(hwnd)
    screen_width = win32api.GetSystemMetrics(0)  # Fix: Use win32api
    screen_height = win32api.GetSystemMetrics(1)  # Fix: Use win32api
    return rect == (0, 0, screen_width, screen_height)


class AlwaysOnTopApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Always On Top")
        self.setGeometry(100, 100, 300, 150)
        
        self.layout = QVBoxLayout()
        self.window_list = QComboBox()
        self.refresh_window_list()
        self.layout.addWidget(self.window_list)

        self.set_top_button = QPushButton("Set Selected Window Always on Top")
        self.set_top_button.clicked.connect(self.set_selected_window_on_top)
        self.layout.addWidget(self.set_top_button)

        self.remove_top_button = QPushButton("Remove Selected Window Always on Top")
        self.remove_top_button.clicked.connect(self.remove_selected_window_from_top)
        self.layout.addWidget(self.remove_top_button)

        self.setLayout(self.layout)

        # Delay getting hwnd until after window is shown
        QTimer.singleShot(500, self.set_own_window_on_top)

        # Timer to check fullscreen
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_fullscreen_status)
        self.timer.start(1000)  # Check every second

    def set_own_window_on_top(self):
        """Find own window handle after it appears on screen."""
        self.hwnd = win32gui.FindWindow(None, "Always On Top")
        if self.hwnd:
            set_always_on_top(self.hwnd)

    def refresh_window_list(self):
        self.window_list.clear()
        windows = gw.getAllTitles()
        self.window_list.addItems([title for title in windows if title.strip()])

    def set_selected_window_on_top(self):
        title = self.window_list.currentText()
        hwnd = win32gui.FindWindow(None, title)
        if hwnd:
            set_always_on_top(hwnd)

    def remove_selected_window_from_top(self):
        title = self.window_list.currentText()
        hwnd = win32gui.FindWindow(None, title)
        if hwnd:
            remove_always_on_top(hwnd)

    def check_fullscreen_status(self):
        selected_window = self.window_list.currentText()
        hwnd = win32gui.FindWindow(None, selected_window)
        if hwnd and is_window_fullscreen(hwnd):
            remove_always_on_top(hwnd)

    def changeEvent(self, event):
        """Keep GUI on top unless minimized."""
        if event.type() == 105:  # Window state changed
            if self.isMinimized():
                remove_always_on_top(self.hwnd)
            else:
                set_always_on_top(self.hwnd)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AlwaysOnTopApp()
    window.show()
    sys.exit(app.exec_())
