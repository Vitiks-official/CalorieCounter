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