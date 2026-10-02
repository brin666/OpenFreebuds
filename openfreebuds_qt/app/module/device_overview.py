from PyQt6.QtCore import QEasingCurve, QRect, QRectF, QSize, Qt, QVariantAnimation
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPen, QPixmap
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from openfreebuds import IOpenFreebuds, OfbEventKind
from openfreebuds_qt.app.module.common import OfbQtCommonModule
from openfreebuds_qt.constants import ASSETS_PATH
from openfreebuds_qt.utils import OfbCoreEvent, get_img_colored


OVERVIEW_STYLE = """
QWidget#deviceOverviewPage {
    background: transparent;
    color: #23364b;
}
QLabel#pageTitle {
    color: #203349;
    background: transparent;
    font-size: 24px;
    font-weight: 700;
}
QLabel#pageSubtitle, QLabel#mutedText {
    color: #71849a;
    background: transparent;
    font-size: 12px;
}
QFrame#identityCard, QFrame#batteryPanel,
QFrame#connectionPanel, QFrame#shortcutsPanel {
    background-color: rgba(255, 255, 255, 236);
    border: 1px solid rgba(255, 255, 255, 248);
    border-radius: 20px;
}
QFrame#batteryTile {
    background: transparent;
    border: none;
}
QLabel#deviceName {
    color: #203349;
    background: transparent;
    font-size: 16px;
    font-weight: 650;
}
QLabel#connectionBadge {
    border: 1px solid #dce7ee;
    border-radius: 13px;
    background: #f1f5f8;
    color: #71849a;
    padding: 6px 12px;
    font-size: 11px;
    font-weight: 600;
}
QLabel#connectionBadge[connectionState="connected"] {
    background: #eaf5ef;
    border-color: #d8ebe0;
    color: #328067;
}
QLabel#connectionBadge[connectionState="connecting"] {
    background: #f7f2e8;
    border-color: #eee4cd;
    color: #9a7732;
}
QLabel#connectionBadge[connectionState="failed"] {
    background: #fbefee;
    border-color: #f1dcda;
    color: #a35b54;
}
QLabel#panelTitle {
    color: #263a50;
    background: transparent;
    font-size: 16px;
    font-weight: 650;
}
QLabel#batteryTileName {
    color: #71849a;
    background: transparent;
    font-size: 12px;
    font-weight: 550;
}
QLabel#batteryPercent {
    color: #203349;
    background: transparent;
    font-size: 34px;
    font-weight: 700;
}
QLabel#batteryUnit {
    color: #526b80;
    background: transparent;
    font-size: 16px;
    font-weight: 600;
    padding-top: 8px;
}
QLabel#batteryCaption {
    color: #71849a;
    background: transparent;
    font-size: 10px;
}
QProgressBar#batteryProgress {
    background: #e6edf2;
    border: none;
    border-radius: 4px;
    max-height: 7px;
    min-height: 7px;
    text-align: center;
}
QProgressBar#batteryProgress::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #79a9cc, stop:1 #9bc3df);
    border-radius: 4px;
}
QProgressBar#batteryProgress[low="true"]::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #d79476, stop:1 #edb394);
}
QProgressBar#batteryProgress:disabled {
    background: #edf1f4;
}
QFrame#batterySeparator, QFrame#summarySeparator {
    background: #e1e8ee;
    border: none;
    max-width: 1px;
}
QLabel#summaryLabel {
    color: #8493a3;
    background: transparent;
    font-size: 10px;
}
QLabel#summaryValue {
    color: #32485f;
    background: transparent;
    font-size: 12px;
    font-weight: 550;
}
QLabel#addressValue {
    color: #8493a3;
    background: transparent;
    font-size: 10px;
}
QLabel#statusDot {
    background: #39a780;
    border-radius: 4px;
    min-width: 8px;
    max-width: 8px;
    min-height: 8px;
    max-height: 8px;
}
QLabel#statusDot[connected="false"] {
    background: #aebbc6;
}
QLabel#quickTitle {
    color: #263a50;
    background: transparent;
    font-size: 17px;
    font-weight: 650;
}
QLabel#noiseTitle {
    color: #60758a;
    background: transparent;
    font-size: 11px;
    font-weight: 600;
}
QPushButton#overviewShortcut {
    color: #36516a;
    background-color: #f2f7fa;
    border: 1px solid #e7eef3;
    border-radius: 12px;
    padding: 10px 12px;
    text-align: left;
    font-size: 12px;
    font-weight: 600;
}
QPushButton#overviewShortcut:focus {
    border: 1px solid #78a8cb;
}
QPushButton#overviewShortcut:pressed {
    background: #e0edf6;
}
QPushButton#overviewShortcut:disabled {
    color: #a3afba;
    background: #f7f9fa;
}
QWidget#noiseControls QToolButton {
    background: #f2f7fa;
    border: 1px solid #e4ecf2;
    border-radius: 12px;
    padding: 2px;
}
QWidget#noiseControls QToolButton:hover {
    background: #e8f1f7;
}
QWidget#noiseControls QToolButton:checked {
    background: #dcebf5;
    border-color: #b9d1e3;
}
QComboBox#overviewAncLevel {
    background: #f5f8fa;
    border: 1px solid #e4ecf2;
    border-radius: 10px;
    padding: 7px 10px;
    color: #40576c;
}
QWidget#deviceOverviewPage:focus {
    outline: none;
}
"""


class DeviceGlyph(QFrame):
    """A small, crisp headphones mark for the connected-device card."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setFixedSize(44, 44)
        self.setAccessibleName(self.tr("Headphones"))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#edf4f8"))
        painter.drawRoundedRect(QRectF(0.5, 0.5, 43, 43), 14, 14)

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor("#6f94b0"), 2.2,
                            Qt.PenStyle.SolidLine,
                            Qt.PenCapStyle.RoundCap,
                            Qt.PenJoinStyle.RoundJoin))
        headband = QPainterPath()
        headband.moveTo(11, 23)
        headband.cubicTo(11, 15, 15, 10, 22, 10)
        headband.cubicTo(29, 10, 33, 15, 33, 23)
        painter.drawPath(headband)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#6f94b0"))
        painter.drawRoundedRect(QRectF(8, 20, 7, 12), 3, 3)
        painter.drawRoundedRect(QRectF(29, 20, 7, 12), 3, 3)
        painter.end()


def _apply_surface_shadow(surface: QWidget):
    shadow = QGraphicsDropShadowEffect(surface)
    shadow.setBlurRadius(20)
    shadow.setOffset(0, 5)
    shadow.setColor(QColor(49, 78, 101, 17))
    surface.setGraphicsEffect(shadow)


class OverviewShortcutButton(QPushButton):
    """A small, quiet hover transition for the two navigation actions."""

    def __init__(self, text: str, parent: QWidget | None = None):
        super().__init__(text, parent)
        self.setObjectName("overviewShortcut")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(42)
        self._hover_progress = 0.0
        self._hover_animation = QVariantAnimation(self)
        self._hover_animation.setDuration(150)
        self._hover_animation.setStartValue(0.0)
        self._hover_animation.setEndValue(1.0)
        self._hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._hover_animation.valueChanged.connect(self._paint_hover)

    def _animate_to(self, target: float):
        self._hover_animation.stop()
        self._hover_animation.setStartValue(self._hover_progress)
        self._hover_animation.setEndValue(target)
        self._hover_animation.start()

    def _paint_hover(self, progress):
        self._hover_progress = float(progress)
        start = QColor("#f2f7fa")
        end = QColor("#e6f0f7")
        r = round(start.red() + (end.red() - start.red()) * self._hover_progress)
        g = round(start.green() + (end.green() - start.green()) * self._hover_progress)
        b = round(start.blue() + (end.blue() - start.blue()) * self._hover_progress)
        self.setStyleSheet(
            "QPushButton#overviewShortcut {"
            f"background-color: rgb({r}, {g}, {b});"
            "color: #36516a; border: 1px solid #e7eef3; border-radius: 12px;"
            "padding: 10px 12px; text-align: left; font-size: 12px; font-weight: 600;}"
            "QPushButton#overviewShortcut:focus {border: 1px solid #78a8cb;}"
            "QPushButton#overviewShortcut:pressed {background: #e0edf6;}"
            "QPushButton#overviewShortcut:disabled {color: #a3afba; background: #f7f9fa;}"
        )

    def enterEvent(self, event):
        self._animate_to(1.0)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animate_to(0.0)
        super().leaveEvent(event)


class BatteryTile(QFrame):
    def __init__(self, title: str, art_size: QSize, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("batteryTile")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 2, 8, 0)
        layout.setSpacing(4)

        self.art = QLabel(self)
        self.art.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.art.setFixedSize(art_size)
        self.art.setAutoFillBackground(False)
        self.art.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(self.art, 0, Qt.AlignmentFlag.AlignHCenter)

        self.name = QLabel(title, self)
        self.name.setObjectName("batteryTileName")
        self.name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.name)

        value_row = QHBoxLayout()
        value_row.setContentsMargins(0, 0, 0, 0)
        value_row.setSpacing(1)
        value_row.addStretch(1)
        self.percent = QLabel("—", self)
        self.percent.setObjectName("batteryPercent")
        self.percent.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_row.addWidget(self.percent)
        self.unit = QLabel("%", self)
        self.unit.setObjectName("batteryUnit")
        self.unit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.unit.setVisible(False)
        value_row.addWidget(self.unit)
        value_row.addStretch(1)
        layout.addLayout(value_row)

        self.progress = QProgressBar(self)
        self.progress.setObjectName("batteryProgress")
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFormat("")
        self.progress.setEnabled(False)
        layout.addWidget(self.progress)

        self.caption = QLabel(self.tr("Waiting for connection"), self)
        self.caption.setObjectName("batteryCaption")
        self.caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.caption)

    def set_art(self, pixmap: QPixmap | None):
        if pixmap is None or pixmap.isNull():
            self.art.clear()
            return
        self.art.setPixmap(pixmap.scaled(
            self.art.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        ))

    def set_title(self, title: str):
        self.name.setText(title)

    def set_value(self, value, connected: bool, waiting_for_data: bool = False):
        percent = _to_percent(value) if connected else None
        self.progress.setProperty("low", "false" if percent is None else str(percent < 20).lower())
        self.progress.style().unpolish(self.progress)
        self.progress.style().polish(self.progress)
        if percent is None:
            self.percent.setText("—")
            self.unit.setVisible(False)
            self.progress.setValue(0)
            self.progress.setEnabled(False)
            if not connected:
                self.caption.setText(self.tr("Waiting for connection"))
            elif waiting_for_data:
                self.caption.setText(self.tr("Waiting for battery data"))
            else:
                self.caption.setText(self.tr("Temporarily unavailable"))
            return

        self.percent.setText(str(percent))
        self.unit.setVisible(True)
        self.progress.setValue(percent)
        self.progress.setEnabled(True)
        if percent >= 100:
            self.caption.setText(self.tr("Full"))
        elif percent < 20:
            self.caption.setText(self.tr("Low battery"))
        else:
            self.caption.setText(self.tr("Battery good"))


def _to_percent(value) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        value_text = str(value).strip().removesuffix("%")
        percent = int(float(value_text))
    except (TypeError, ValueError, OverflowError):
        return None
    return percent if 0 <= percent <= 100 else None


class OfbQtDeviceOverviewModule(OfbQtCommonModule):
    def __init__(self, parent: QWidget, context):
        super().__init__(parent, context)
        self.setObjectName("deviceOverviewPage")
        self.setStyleSheet(OVERVIEW_STYLE)
        self._connected = False
        self._device_name = ""
        self._device_address = ""
        self._product_sprite = QPixmap(str(ASSETS_PATH / "image" / "freebuds7i-product-redraw.png"))
        self._product_art = self._load_product_art(self._product_sprite)
        self._generic_art = self._load_generic_art()

        root = QVBoxLayout(self)
        root.setContentsMargins(26, 22, 26, 20)
        root.setSpacing(14)

        header = QVBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(4)
        self.page_title = QLabel(self.tr("Device overview"), self)
        self.page_title.setObjectName("pageTitle")
        self.page_subtitle = QLabel(self.tr("Your earbuds and case at a glance"), self)
        self.page_subtitle.setObjectName("pageSubtitle")
        header.addWidget(self.page_title)
        header.addWidget(self.page_subtitle)
        root.addLayout(header)

        self.identity_card = QFrame(self)
        self.identity_card.setObjectName("identityCard")
        identity_layout = QHBoxLayout(self.identity_card)
        identity_layout.setContentsMargins(18, 12, 18, 12)
        identity_layout.setSpacing(14)

        icon_frame = DeviceGlyph(self.identity_card)
        identity_layout.addWidget(icon_frame)

        identity_text = QVBoxLayout()
        identity_text.setContentsMargins(0, 0, 0, 0)
        identity_text.setSpacing(4)
        self.device_name_label = QLabel(self.tr("No device connected"), self.identity_card)
        self.device_name_label.setObjectName("deviceName")
        self.profile_label = QLabel(self.tr("Connect a supported device to begin"), self.identity_card)
        self.profile_label.setObjectName("mutedText")
        identity_text.addWidget(self.device_name_label)
        identity_text.addWidget(self.profile_label)
        identity_layout.addLayout(identity_text, 1)

        self.connection_badge = QLabel(self.tr("Not connected"), self.identity_card)
        self.connection_badge.setObjectName("connectionBadge")
        self.connection_badge.setProperty("connectionState", "disconnected")
        self.connection_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        identity_layout.addWidget(self.connection_badge)
        _apply_surface_shadow(self.identity_card)
        root.addWidget(self.identity_card)

        self.battery_panel = QFrame(self)
        self.battery_panel.setObjectName("batteryPanel")
        self.battery_panel.setMinimumHeight(304)
        battery_layout = QVBoxLayout(self.battery_panel)
        battery_layout.setContentsMargins(22, 16, 22, 16)
        battery_layout.setSpacing(10)

        battery_header = QHBoxLayout()
        battery_header.setContentsMargins(0, 0, 0, 0)
        battery_header.setSpacing(12)
        title = QLabel(self.tr("Battery status"), self.battery_panel)
        title.setObjectName("panelTitle")
        self.battery_status_label = QLabel(self.tr("Waiting for connection"), self.battery_panel)
        self.battery_status_label.setObjectName("mutedText")
        title_column = QVBoxLayout()
        title_column.setSpacing(3)
        title_column.addWidget(title)
        title_column.addWidget(self.battery_status_label)
        battery_header.addLayout(title_column, 1)
        battery_layout.addLayout(battery_header)

        tiles_row = QHBoxLayout()
        tiles_row.setContentsMargins(0, 2, 0, 0)
        tiles_row.setSpacing(10)
        self.left_tile = BatteryTile(self.tr("Left earbud"), QSize(84, 96), self.battery_panel)
        self.case_tile = BatteryTile(self.tr("Charging case"), QSize(112, 100), self.battery_panel)
        self.right_tile = BatteryTile(self.tr("Right earbud"), QSize(84, 96), self.battery_panel)
        self.left_separator = self._separator(self.battery_panel, "batterySeparator")
        self.right_separator = self._separator(self.battery_panel, "batterySeparator")
        tiles_row.addWidget(self.left_tile, 1)
        tiles_row.addWidget(self.left_separator)
        tiles_row.addWidget(self.case_tile, 1)
        tiles_row.addWidget(self.right_separator)
        tiles_row.addWidget(self.right_tile, 1)
        battery_layout.addLayout(tiles_row, 1)
        _apply_surface_shadow(self.battery_panel)
        root.addWidget(self.battery_panel)

        bottom_row = QHBoxLayout()
        bottom_row.setContentsMargins(0, 0, 0, 0)
        bottom_row.setSpacing(14)
        self.connection_panel = QFrame(self)
        self.connection_panel.setObjectName("connectionPanel")
        connection_layout = QVBoxLayout(self.connection_panel)
        connection_layout.setContentsMargins(20, 17, 20, 17)
        connection_layout.setSpacing(16)
        connection_title = QLabel(self.tr("Connection overview"), self.connection_panel)
        connection_title.setObjectName("panelTitle")
        connection_layout.addWidget(connection_title)

        summary_row = QHBoxLayout()
        summary_row.setContentsMargins(0, 0, 0, 0)
        summary_row.setSpacing(14)
        state_column = QVBoxLayout()
        state_column.setSpacing(6)
        state_label = QLabel(self.tr("Connection"), self.connection_panel)
        state_label.setObjectName("summaryLabel")
        state_value_row = QHBoxLayout()
        state_value_row.setContentsMargins(0, 0, 0, 0)
        state_value_row.setSpacing(7)
        self.status_dot = QLabel(self.connection_panel)
        self.status_dot.setObjectName("statusDot")
        self.status_dot.setProperty("connected", "false")
        self.connection_value = QLabel(self.tr("Not connected"), self.connection_panel)
        self.connection_value.setObjectName("summaryValue")
        state_value_row.addWidget(self.status_dot)
        state_value_row.addWidget(self.connection_value)
        state_value_row.addStretch(1)
        state_column.addWidget(state_label)
        state_column.addLayout(state_value_row)
        summary_row.addLayout(state_column, 1)

        summary_row.addWidget(self._separator(self.connection_panel, "summarySeparator"))
        address_column = QVBoxLayout()
        address_column.setSpacing(6)
        address_label = QLabel(self.tr("Bluetooth address"), self.connection_panel)
        address_label.setObjectName("summaryLabel")
        self.address_value = QLabel("—", self.connection_panel)
        self.address_value.setObjectName("addressValue")
        self.address_value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        address_column.addWidget(address_label)
        address_column.addWidget(self.address_value)
        summary_row.addLayout(address_column, 1)

        summary_row.addWidget(self._separator(self.connection_panel, "summarySeparator"))
        fields_column = QVBoxLayout()
        fields_column.setSpacing(6)
        fields_label = QLabel(self.tr("Battery fields"), self.connection_panel)
        fields_label.setObjectName("summaryLabel")
        self.fields_value = QLabel(self.tr("Waiting for connection"), self.connection_panel)
        self.fields_value.setObjectName("summaryValue")
        fields_column.addWidget(fields_label)
        fields_column.addWidget(self.fields_value)
        summary_row.addLayout(fields_column, 1)
        connection_layout.addLayout(summary_row)
        _apply_surface_shadow(self.connection_panel)
        bottom_row.addWidget(self.connection_panel, 2)

        self.shortcuts_panel = QFrame(self)
        self.shortcuts_panel.setObjectName("shortcutsPanel")
        shortcuts_layout = QVBoxLayout(self.shortcuts_panel)
        shortcuts_layout.setContentsMargins(18, 17, 18, 16)
        shortcuts_layout.setSpacing(10)
        shortcuts_title = QLabel(self.tr("Shortcuts"), self.shortcuts_panel)
        shortcuts_title.setObjectName("quickTitle")
        shortcuts_layout.addWidget(shortcuts_title)
        shortcut_row = QHBoxLayout()
        shortcut_row.setContentsMargins(0, 0, 0, 0)
        shortcut_row.setSpacing(8)
        self.device_info_button = OverviewShortcutButton(self.tr("Device information"), self.shortcuts_panel)
        self.tray_battery_button = OverviewShortcutButton(self.tr("Tray battery"), self.shortcuts_panel)
        self.device_info_button.setEnabled(False)
        shortcut_row.addWidget(self.device_info_button, 1)
        shortcut_row.addWidget(self.tray_battery_button, 1)
        shortcuts_layout.addLayout(shortcut_row)

        self.noise_section = QWidget(self.shortcuts_panel)
        self.noise_section.setObjectName("noiseControls")
        noise_layout = QVBoxLayout(self.noise_section)
        noise_layout.setContentsMargins(0, 2, 0, 0)
        noise_layout.setSpacing(7)
        noise_title = QLabel(self.tr("Noise control"), self.noise_section)
        noise_title.setObjectName("noiseTitle")
        noise_layout.addWidget(noise_title)
        self.noise_controls_layout = QHBoxLayout()
        self.noise_controls_layout.setContentsMargins(0, 0, 0, 0)
        self.noise_controls_layout.setSpacing(8)
        noise_layout.addLayout(self.noise_controls_layout)
        self.noise_section.setVisible(False)
        shortcuts_layout.addWidget(self.noise_section)
        _apply_surface_shadow(self.shortcuts_panel)
        bottom_row.addWidget(self.shortcuts_panel, 1)
        root.addLayout(bottom_row)

        root.addSpacing(10)
        footer = QLabel(self.tr("Battery levels are shown as reported by the connected device."), self)
        footer.setObjectName("mutedText")
        footer.setContentsMargins(2, 0, 0, 0)
        root.addWidget(footer)
        root.addStretch(1)

        self._render_art_for_device("")
        self._render_battery(None, connected=False, waiting_for_data=False)

    @staticmethod
    def _separator(parent: QWidget, object_name: str) -> QFrame:
        line = QFrame(parent)
        line.setObjectName(object_name)
        line.setFrameShape(QFrame.Shape.VLine)
        line.setFixedWidth(1)
        return line

    @staticmethod
    def _load_product_art(sprite: QPixmap) -> dict[str, QPixmap]:
        if sprite.isNull():
            return {}
        return {
            "left": sprite.copy(QRect(90, 160, 430, 625)),
            "case": sprite.copy(QRect(520, 65, 730, 760)),
            "right": sprite.copy(QRect(1254, 160, 430, 625)),
        }

    def _load_generic_art(self) -> dict[str, QPixmap]:
        color = self.palette().text().color().getRgb()
        return {
            "left": get_img_colored("batt_l", color, "icon/main_window", (52, 52)),
            "case": get_img_colored("batt_c", color, "icon/main_window", (52, 52)),
            "right": get_img_colored("batt_r", color, "icon/main_window", (52, 52)),
        }

    def _render_art_for_device(self, device_name: str):
        is_freebuds_7i = "freebuds" in device_name.casefold() and "7i" in device_name.casefold()
        art = self._product_art if is_freebuds_7i and self._product_art else self._generic_art
        self.left_tile.set_art(art.get("left"))
        self.case_tile.set_art(art.get("case"))
        self.right_tile.set_art(art.get("right"))

    def attach_noise_controls(self, anc_root: QWidget, anc_level: QWidget):
        for control in (anc_root, anc_level):
            previous_layout = control.parentWidget().layout()
            if previous_layout is not None:
                previous_layout.removeWidget(control)
            control.setParent(self.noise_section)

        anc_root.setStyleSheet(
            "QWidget#anc_root { background: transparent; }"
            "QToolButton { background: #f2f7fa; border: 1px solid #e4ecf2;"
            " border-radius: 12px; padding: 2px; }"
            "QToolButton:hover { background: #e8f1f7; }"
            "QToolButton:checked { background: #dcebf5; border-color: #b9d1e3; }"
        )
        anc_level.setObjectName("overviewAncLevel")
        anc_level.setMinimumHeight(38)
        self.noise_controls_layout.addWidget(anc_root, 2)
        self.noise_controls_layout.addWidget(anc_level, 1)
        self.noise_section.setVisible(False)

    def set_navigation_callbacks(self, open_device_info, open_tray_battery, tray_enabled: bool):
        self.device_info_button.clicked.connect(open_device_info)
        self.tray_battery_button.clicked.connect(open_tray_battery)
        self.device_info_button.setEnabled(self._connected)
        self.tray_battery_button.setEnabled(tray_enabled)
        if not tray_enabled:
            self.tray_battery_button.setToolTip(self.tr("Tray settings are managed by the running instance"))

    async def update_ui(self, event: OfbCoreEvent):
        identity_changed = event.kind_in([OfbEventKind.STATE_CHANGED, OfbEventKind.DEVICE_CHANGED])
        battery_changed = event.is_changed("battery", "")
        anc_changed = event.kind_in([OfbEventKind.STATE_CHANGED, OfbEventKind.DEVICE_CHANGED]) or event.is_changed("anc", "")

        if identity_changed:
            state = await self.ofb.get_state()
            self._connected = state == IOpenFreebuds.STATE_CONNECTED
            if self._connected:
                self._device_name, self._device_address = await self.ofb.get_device_tags()
                self.device_name_label.setText(self._device_name or self.tr("Connected device"))
                is_freebuds_7i = "freebuds" in self._device_name.casefold() and "7i" in self._device_name.casefold()
                self.profile_label.setText(
                    self.tr("Compatible profile: FreeBuds 6i")
                    if is_freebuds_7i else self.tr("Profile selected automatically")
                )
                self._set_connection_status(self.tr("Connected"), "connected")
            else:
                self._device_name = ""
                self._device_address = ""
                self.device_name_label.setText(self.tr("No device connected"))
                self.profile_label.setText(self.tr("Connect a supported device to begin"))
                if state == IOpenFreebuds.STATE_WAIT:
                    self._set_connection_status(self.tr("Connecting…"), "connecting")
                elif state == IOpenFreebuds.STATE_FAILED:
                    self._set_connection_status(self.tr("Connection failed"), "failed")
                else:
                    self._set_connection_status(self.tr("Not connected"), "disconnected")
            self._render_art_for_device(self._device_name)
            self.address_value.setText(self._device_address or "—")
            self.device_info_button.setEnabled(self._connected)
            self.connection_value.setText(
                self.tr("Connected") if self._connected else self.connection_badge.text()
            )
            self.status_dot.setProperty("connected", "true" if self._connected else "false")
            self.status_dot.style().unpolish(self.status_dot)
            self.status_dot.style().polish(self.status_dot)

        if identity_changed or battery_changed:
            battery = await self.ofb.get_property("battery") if self._connected else None
            self._render_battery(
                battery,
                connected=self._connected,
                waiting_for_data=self._connected and not battery,
            )

        if anc_changed:
            anc = await self.ofb.get_property("anc") if self._connected else None
            self.noise_section.setVisible(anc is not None)

    def _set_connection_status(self, text: str, state: str):
        self.connection_badge.setText(text)
        self.connection_badge.setProperty("connectionState", state)
        self.connection_badge.style().unpolish(self.connection_badge)
        self.connection_badge.style().polish(self.connection_badge)

    def _render_battery(self, battery, connected: bool, waiting_for_data: bool):
        battery = battery if isinstance(battery, dict) else {}
        separate_earbuds = (
            "case" in battery or "left" in battery or "right" in battery
            or (connected and not battery)
        )
        self.left_tile.setVisible(separate_earbuds or not connected)
        self.right_tile.setVisible(separate_earbuds or not connected)
        self.left_separator.setVisible(separate_earbuds or not connected)
        self.right_separator.setVisible(separate_earbuds or not connected)

        if separate_earbuds:
            self.case_tile.set_title(self.tr("Charging case"))
            left_value = battery.get("left")
            right_value = battery.get("right")
            case_value = battery.get("case")
            fields = [self.tr("Left earbud"), self.tr("Right earbud")]
            if "case" in battery:
                fields.append(self.tr("Charging case"))
            self.fields_value.setText(
                self.tr("Waiting for battery data") if waiting_for_data else " · ".join(fields)
            )
        else:
            self.case_tile.set_title(self.tr("Earbud") if connected else self.tr("Charging case"))
            left_value = None
            right_value = None
            case_value = battery.get("global")
            if not connected:
                self.fields_value.setText(self.tr("Waiting for connection"))
            elif waiting_for_data:
                self.fields_value.setText(self.tr("Waiting for battery data"))
            else:
                self.fields_value.setText(self.tr("Earbud battery"))

        self.left_tile.set_value(left_value, connected, waiting_for_data)
        self.right_tile.set_value(right_value, connected, waiting_for_data)
        self.case_tile.set_value(case_value, connected, waiting_for_data)

        if not connected:
            self.battery_status_label.setText(self.tr("Connect earbuds to see battery levels"))
        elif waiting_for_data:
            self.battery_status_label.setText(self.tr("Waiting for battery data"))
        else:
            self.battery_status_label.setText(self.tr("Battery synced"))
