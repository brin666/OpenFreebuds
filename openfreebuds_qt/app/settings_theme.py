"""Shared visual treatment for the non-overview settings pages."""

from openfreebuds_qt.constants import ASSETS_PATH


_DROPDOWN_CHEVRON = (ASSETS_PATH / "image" / "dropdown-chevron.svg").as_posix()
_DROPDOWN_CHEVRON_UP = (ASSETS_PATH / "image" / "dropdown-chevron-up.svg").as_posix()
_CHECKMARK = (ASSETS_PATH / "image" / "checkbox-check.svg").as_posix()

SETTINGS_PAGE_STYLE = """
QWidget#settingsPageFrame {
    background: #fbfcfd;
    border: 1px solid #e0e8ef;
    border-radius: 20px;
}

QWidget[secondarySettingsPage="true"] {
    background: transparent;
    color: #31485e;
    border: none;
}

QWidget[secondarySettingsPage="true"] QLabel,
QWidget[secondarySettingsPage="true"] QCheckBox,
QWidget[secondarySettingsPage="true"] QRadioButton,
QWidget[secondarySettingsPage="true"] QGroupBox,
QWidget[secondarySettingsPage="true"] QTableWidget,
QWidget[secondarySettingsPage="true"] QListWidget,
QWidget[secondarySettingsPage="true"] QTreeWidget,
QWidget[secondarySettingsPage="true"] QLineEdit,
QWidget[secondarySettingsPage="true"] QComboBox,
QWidget[secondarySettingsPage="true"] QSpinBox,
QWidget[secondarySettingsPage="true"] QDoubleSpinBox,
QWidget[secondarySettingsPage="true"] QPushButton,
QWidget[secondarySettingsPage="true"] QToolButton {
    color: #3c5369;
}

QWidget[secondarySettingsPage="true"] QLabel {
    background: transparent;
    border: none;
}

QWidget[secondarySettingsPage="true"] QLabel:disabled,
QWidget[secondarySettingsPage="true"] QCheckBox:disabled,
QWidget[secondarySettingsPage="true"] QRadioButton:disabled {
    color: #9aa9b7;
}

QWidget[secondarySettingsPage="true"] QGroupBox {
    background: #ffffff;
    border: 1px solid #e3eaf0;
    border-radius: 15px;
    margin-top: 14px;
    padding: 18px 14px 14px 14px;
    color: #2f465c;
    font-weight: 600;
}

QWidget[secondarySettingsPage="true"] QGroupBox::title {
    subcontrol-origin: margin;
    left: 13px;
    padding: 0 6px;
    color: #2d455c;
    background: #ffffff;
}

QWidget[secondarySettingsPage="true"] QPushButton,
QWidget[secondarySettingsPage="true"] QToolButton {
    background: #f1f6fa;
    border: 1px solid #dce6ee;
    border-radius: 10px;
    padding: 6px 13px;
    min-height: 24px;
}

QWidget[secondarySettingsPage="true"] QPushButton:hover,
QWidget[secondarySettingsPage="true"] QToolButton:hover {
    background: #e9f2f8;
    border-color: #cbdce9;
}

QWidget[secondarySettingsPage="true"] QPushButton:pressed,
QWidget[secondarySettingsPage="true"] QToolButton:pressed,
QWidget[secondarySettingsPage="true"] QToolButton:checked {
    background: #dcebf5;
    border-color: #bdd3e3;
}

QWidget[secondarySettingsPage="true"] QPushButton:disabled,
QWidget[secondarySettingsPage="true"] QToolButton:disabled {
    color: #a6b3bf;
    background: #f6f8fa;
    border-color: #e8edf1;
}

QWidget[secondarySettingsPage="true"] QLineEdit,
QWidget[secondarySettingsPage="true"] QComboBox,
QWidget[secondarySettingsPage="true"] QSpinBox,
QWidget[secondarySettingsPage="true"] QDoubleSpinBox {
    background: #ffffff;
    border: 1px solid #dce6ee;
    border-radius: 10px;
    padding: 5px 10px;
    min-height: 24px;
    selection-background-color: #dcebf5;
    selection-color: #253c52;
}

QWidget[secondarySettingsPage="true"] QLineEdit:focus,
QWidget[secondarySettingsPage="true"] QComboBox:focus,
QWidget[secondarySettingsPage="true"] QSpinBox:focus,
QWidget[secondarySettingsPage="true"] QDoubleSpinBox:focus {
    border-color: #9bbbd2;
    background: #ffffff;
}

QWidget[secondarySettingsPage="true"] QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 28px;
    background: transparent;
    border: none;
    border-top-right-radius: 9px;
    border-bottom-right-radius: 9px;
}

QWidget[secondarySettingsPage="true"] QComboBox::down-arrow {
    image: url("__DROPDOWN_CHEVRON__");
    width: 12px;
    height: 12px;
}

QWidget[secondarySettingsPage="true"] QSpinBox::up-button,
QWidget[secondarySettingsPage="true"] QDoubleSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 24px;
    border: none;
    background: transparent;
    border-top-right-radius: 9px;
}

QWidget[secondarySettingsPage="true"] QSpinBox::down-button,
QWidget[secondarySettingsPage="true"] QDoubleSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 24px;
    border: none;
    background: transparent;
    border-bottom-right-radius: 9px;
}

QWidget[secondarySettingsPage="true"] QSpinBox::up-arrow,
QWidget[secondarySettingsPage="true"] QDoubleSpinBox::up-arrow {
    image: url("__DROPDOWN_CHEVRON_UP__");
    width: 10px;
    height: 10px;
}

QWidget[secondarySettingsPage="true"] QSpinBox::down-arrow,
QWidget[secondarySettingsPage="true"] QDoubleSpinBox::down-arrow {
    image: url("__DROPDOWN_CHEVRON__");
    width: 10px;
    height: 10px;
}

QWidget[secondarySettingsPage="true"] QComboBox QAbstractItemView {
    background: #ffffff;
    color: #344c63;
    border: 1px solid #dce6ee;
    border-radius: 10px;
    padding: 4px;
    outline: none;
    selection-background-color: #e6f0f7;
    selection-color: #253c52;
}

QWidget[secondarySettingsPage="true"] QComboBox QAbstractItemView::item {
    min-height: 26px;
    padding: 4px 9px;
    border-radius: 7px;
}

QWidget[secondarySettingsPage="true"] QCheckBox,
QWidget[secondarySettingsPage="true"] QRadioButton {
    background: transparent;
    spacing: 9px;
    padding: 3px 1px;
}

QWidget[secondarySettingsPage="true"] QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #bdcbd7;
    border-radius: 5px;
    background: #ffffff;
}

QWidget[secondarySettingsPage="true"] QCheckBox::indicator:hover,
QWidget[secondarySettingsPage="true"] QRadioButton::indicator:hover {
    border-color: #87abc4;
    background: #f2f7fa;
}

QWidget[secondarySettingsPage="true"] QCheckBox::indicator:checked {
    image: url("__CHECKMARK__");
    background: #6298bb;
    border-color: #6298bb;
}

QWidget[secondarySettingsPage="true"] QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #bdcbd7;
    border-radius: 9px;
    background: #ffffff;
}

QWidget[secondarySettingsPage="true"] QRadioButton::indicator:checked {
    border: 5px solid #6298bb;
    background: #ffffff;
}

QWidget[secondarySettingsPage="true"] QTableWidget,
QWidget[secondarySettingsPage="true"] QListWidget,
QWidget[secondarySettingsPage="true"] QTreeWidget {
    background: #ffffff;
    alternate-background-color: #f7fafc;
    border: 1px solid #e1e9f0;
    border-radius: 12px;
    gridline-color: #e9eef3;
    outline: none;
    selection-background-color: #e5f0f7;
    selection-color: #2a4258;
}

QWidget[secondarySettingsPage="true"] QAbstractItemView::item {
    padding: 7px 10px;
    border: none;
    border-radius: 7px;
}

QWidget[secondarySettingsPage="true"] QHeaderView::section {
    background: #f3f7fa;
    color: #60768a;
    border: none;
    border-bottom: 1px solid #e5ecf1;
    padding: 8px 10px;
}

QWidget[secondarySettingsPage="true"] QScrollBar:vertical {
    width: 8px;
    margin: 3px 1px 3px 1px;
    background: transparent;
    border: none;
}

QWidget[secondarySettingsPage="true"] QScrollBar::handle:vertical {
    min-height: 28px;
    background: #cbd7e0;
    border-radius: 4px;
}

QWidget[secondarySettingsPage="true"] QScrollBar::handle:vertical:hover {
    background: #aebfcd;
}

QWidget[secondarySettingsPage="true"] QScrollBar::add-line:vertical,
QWidget[secondarySettingsPage="true"] QScrollBar::sub-line:vertical,
QWidget[secondarySettingsPage="true"] QScrollBar::add-page:vertical,
QWidget[secondarySettingsPage="true"] QScrollBar::sub-page:vertical {
    height: 0;
    background: transparent;
    border: none;
}

QWidget[secondarySettingsPage="true"] QLabel:link {
    color: #4e83a7;
}
""".replace("__DROPDOWN_CHEVRON__", _DROPDOWN_CHEVRON).replace(
    "__DROPDOWN_CHEVRON_UP__", _DROPDOWN_CHEVRON_UP
).replace("__CHECKMARK__", _CHECKMARK)
