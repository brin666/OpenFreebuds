from typing import Optional

from PyQt6.QtCore import pyqtSlot, Qt
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import QWidget, QBoxLayout, QVBoxLayout

from openfreebuds_qt.utils.qt_utils import widget_with_layout
from openfreebuds_qt.app.widget import OfbQListItem
from openfreebuds_qt.app.widget.list_header import OfbQListHeader


class OfbQtSettingsTabHelper:
    class Entry:
        def __init__(self, label: str, content: QWidget, display_content: QWidget, section):
            self.label = label
            self.list_item = OfbQListItem(section.root, section.root.tr(label))
            self.content = display_content
            self.focus_widget = content
            self.section: OfbQtSettingsTabHelper.Section = section

            section.root_layout.addWidget(self.list_item)
            section.items.append(self)

    class Section:
        def __init__(self, parent: QWidget, label: str, index: int):
            self.label = label
            self.items: list[OfbQtSettingsTabHelper.Entry] = []
            self.index: int = index

            self.root, self.root_layout = widget_with_layout(parent, QBoxLayout.Direction.Down)
            self.list_item: OfbQListHeader = OfbQListHeader(self.root, self.root.tr(label)) if label else None
            self.root_layout.addWidget(self.list_item)

        def set_visible(self, visible: bool):
            self.root.setVisible(visible)

    def __init__(self, tabs_root: QWidget, body_root: QWidget):
        self.tabs_root = tabs_root
        self.root = body_root

        self.root_layout = QBoxLayout(QBoxLayout.Direction.Down)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)
        self.root.setLayout(self.root_layout)

        self.tabs_layout = QBoxLayout(QBoxLayout.Direction.Down)
        self.tabs_layout.setContentsMargins(0, 0, 0, 0)
        self.tabs_layout.setSpacing(0)
        self.tabs_root.setLayout(self.tabs_layout)

        self._active_entry: Optional[OfbQtSettingsTabHelper.Entry] = None
        self._sections: list[OfbQtSettingsTabHelper.Section] = [
            OfbQtSettingsTabHelper.Section(self.tabs_root, "", 0)
        ]

    def set_active_tab(self, section: int, tab: int):
        if self._active_entry is not None:
            self._active_entry.list_item.set_active(False)
            self._active_entry.content.setVisible(False)

        new_active = self._sections[section].items[tab]
        new_active.list_item.set_active(True)
        new_active.content.setVisible(True)
        new_active.focus_widget.setFocus()

        self._active_entry = new_active

    @property
    def active_tab(self):
        return self._active_entry

    def add_tab(self, label: str, content: QWidget):
        section_num = len(self._sections) - 1
        tab = len(self._sections[section_num].items)

        display_content = content
        if content.property("secondarySettingsPage") == "true":
            display_content = QWidget(self.root)
            display_content.setObjectName("settingsPageFrame")
            display_content.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
            frame_layout = QVBoxLayout(display_content)
            frame_layout.setContentsMargins(16, 16, 16, 16)
            frame_layout.setSpacing(0)
            frame_layout.addWidget(content)

        entry = OfbQtSettingsTabHelper.Entry(label=label,
                                             content=content,
                                             display_content=display_content,
                                             section=self._sections[section_num])

        @pyqtSlot()
        def _activate(*_):
            self.set_active_tab(section_num, tab)

        @pyqtSlot()
        def _kbd_activate(e: QKeyEvent):
            if e.key() in [Qt.Key.Key_Return, Qt.Key.Key_Space]:
                _activate(e)
            elif e.key() == Qt.Key.Key_Down:
                entry.list_item.focusNextChild()
            elif e.key() == Qt.Key.Key_Up:
                entry.list_item.focusPreviousChild()

        entry.list_item.label.mousePressEvent = _activate
        entry.list_item.label.keyPressEvent = _kbd_activate
        self.root_layout.addWidget(display_content)
        display_content.setVisible(False)

        return entry

    def add_section(self, label: str):
        section = len(self._sections)
        entry = OfbQtSettingsTabHelper.Section(self.tabs_root, label=label, index=section)
        # self.tabs_layout.addWidget(entry.list_item)
        self._sections.append(entry)
        return entry

    def finalize_list(self):
        self.tabs_layout.insertStretch(-1, 1)
