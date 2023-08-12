import os
import subprocess
import sys

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPalette, QColor, QTextCursor, QFont
from PyQt5.QtWidgets import QApplication, QWidget, QPlainTextEdit, QVBoxLayout


class SimplePythonTerminal(QWidget):
    def __init__(self):
        super().__init__()

        self.cursor_timer = None
        self.cursor_visible = None
        self.command_history = None
        self.current_path = None
        self.user_input = None
        self.text = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Terminal")
        self.setGeometry(100, 100, 800, 600)

        # Set dark mode palette
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(0, 0, 0))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(0, 0, 0))
        palette.setColor(QPalette.AlternateBase, QColor(0, 0, 0))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(0, 0, 0))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        self.setPalette(palette)

        self.text = QPlainTextEdit(self)
        self.text.setReadOnly(True)
        self.text.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        layout = QVBoxLayout()
        layout.addWidget(self.text)
        self.setLayout(layout)

        font = QFont("Source Code Pro", 11)
        self.text.setFont(font)

        self.user_input = ""
        self.command_history = []  # List to store command history
        self.current_path = os.getcwd()  # Get current working directory

        self.cursor_visible = True
        self.cursor_timer = QTimer(self)
        self.cursor_timer.timeout.connect(self.toggle_cursor)
        self.cursor_timer.start(500)  # Cursor visibility toggle interval in milliseconds

        self.update_prompt()

    def toggle_cursor(self):
        self.cursor_visible = not self.cursor_visible
        self.update_prompt()  # Update the prompt to reflect cursor visibility

    def update_prompt(self):
        cursor = self.text.textCursor()
        cursor.movePosition(QTextCursor.StartOfBlock, QTextCursor.MoveAnchor)
        cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)

        if self.cursor_visible:
            prompt = f"({self.current_path}) >: {self.user_input}_"
        else:
            prompt = f"({self.current_path}) >: {self.user_input}"

        cursor.removeSelectedText()
        cursor.insertText(prompt)

        cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.MoveAnchor)
        self.text.setTextCursor(cursor)

    def keyReleaseEvent(self, event):
        key = event.key()
        # print(key)
        if key == Qt.Key_Return:
            self.text.moveCursor(QTextCursor.End)
            self.text.insertPlainText("\n")
            self.command_history.append(self.user_input)  # Store the entered command
            # self.text.insertPlainText("You typed: " + self.user_input + "\n")
            self.execute_command(self.user_input)
            self.user_input = ""
            self.update_prompt()  # Update the prompt after handling Return key
        elif key == Qt.Key_Backspace:
            self.user_input = self.user_input[:-1]
            self.update_prompt()
        elif key == Qt.Key_Space:
            self.user_input += " "  # Add a space to user input
            self.update_prompt()
        else:
            self.user_input += event.text()
            self.update_prompt()

    def execute_command(self, command):
        try:
            result = subprocess.run(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.current_path,
            )
            if result.stdout:
                self.text.insertPlainText(result.stdout)
            if result.stderr:
                self.text.insertPlainText(result.stderr)
        except Exception as e:
            self.text.insertPlainText(f"Error: {str(e)}\n")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimplePythonTerminal()
    window.show()
    sys.exit(app.exec_())
