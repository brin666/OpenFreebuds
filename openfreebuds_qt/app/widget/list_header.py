from PyQt6.QtWidgets import QLabel, QWidget


class OfbQListHeader(QLabel):
    def __init__(self, parent: QWidget, text: str = ""):
        super().__init__(parent)
        self.setStyleSheet("font-weight: 600;"
                           "font-size: 10px;"
                           "padding: 12px 12px 6px;"
                           "color: #8493a3")
        self.setText(text)

    def setText(self, a0: str):
        super().setText(a0.upper())
