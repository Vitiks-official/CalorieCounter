from PyQt6.QtGui import QFont

font = QFont()
font.setFamily("Enigmatic Unicode")

ProgressBarStyle = """
        QProgressBar {
            height: 20px;
            background-color: white;
            border-radius: 10px; 
            overflow: hidden;
        }
        QProgressBar::chunk {
            border-radius: 10px; 
            background-color: #77dd77; 
        }"""

list_style = """
    QListWidget {
        border-radius: 10px;
        background-color: transparent;
    }
    QListWidget::item {
        border-radius: 20px;
        border: 4px solid darkgray;
        color: black;
        padding: 10px;
    }
    QScrollBar {
        width: 0px;
    }
"""