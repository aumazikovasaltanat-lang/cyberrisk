"""
================================================================================
  Умная касса и KDS кофейни в стиле Drinkit
  Фреймворк: PyQt6 | Автономный запуск (без внешних файлов и картинок)
  Автор: Antigravity Assistant для Салтанат
================================================================================
"""

import sys
import time
from dataclasses import dataclass, field
from typing import Optional, List, Dict

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QScrollArea, QFrame,
    QDialog, QButtonGroup, QRadioButton, QCheckBox, QSizePolicy,
    QStackedWidget, QGraphicsOpacityEffect
)
from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve,
    pyqtSignal, QObject, QRect, QPoint
)
from PyQt6.QtGui import (
    QColor, QFont, QPainter, QPainterPath,
    QLinearGradient, QPen, QBrush, QPixmap,
    QPalette, QCursor
)

# ─────────────────────────── ЦВЕТОВАЯ ПАЛИТРА ───────────────────────────── #
C_BG           = "#141517"  # Глубокий матовый графит (основной фон)
C_CARD         = "#1E2024"  # Приглушенный темно-серый с теплым подтоном
C_CARD_HOVER   = "#25282E"  # Фон карточки при наведении
C_BORDER       = "#2A2D34"  # Стандартная аккуратная рамка
C_BORDER_HOVER = "#383B42"  # Легкое осветление рамки при hover
C_ACCENT       = "#D97736"  # Мягкий янтарно-карамельный акцент
C_ACCENT_HOVER = "#E08844"  # Более яркая карамель при взаимодействии
C_YELLOW       = "#E5A93C"  # Статус «В работе» / внимание (2-4 мин)
C_GREEN        = "#2EB872"  # Статус «Готов / Свежий»
C_RED          = "#E05252"  # Предупреждение / просрочено (> 4 мин)
C_TEXT         = "#F3F4F6"  # Основной мягкий белый текст
C_TEXT_MUTED   = "#9CA3AF"  # Нейтральный дымчатый вторичный текст
C_DIVIDER      = "#23262C"  # Тонкий разделитель блоков

# ─────────────────────────── КАТАЛОГ НАПИТКОВ ────────────────────────────── #
MENU_ITEMS = [
    {
        "id": 1,
        "name": "Капучино",
        "price": 1200,
        "icon": "cappuccino",
        "cup_color": "#8B5E3C",
        "desc": "Классический баланс эспрессо и шелковистой молочной пены"
    },
    {
        "id": 2,
        "name": "Латте",
        "price": 1300,
        "icon": "latte",
        "cup_color": "#C4956A",
        "desc": "Нежный кофейно-молочный напиток с тонким слоем крема"
    },
    {
        "id": 3,
        "name": "Американо",
        "price": 900,
        "icon": "americano",
        "cup_color": "#3D2B1F",
        "desc": "Двойной эспрессо с горячей фильтр-водой"
    },
    {
        "id": 4,
        "name": "Фильтр-кофе",
        "price": 1000,
        "icon": "filter",
        "cup_color": "#6F4E37",
        "desc": "Светлая обжарка, чистый и многогранный вкус спешелти зерна"
    },
    {
        "id": 5,
        "name": "Матча Латте",
        "price": 1500,
        "icon": "matcha",
        "cup_color": "#4A7C59",
        "desc": "Церемониальная зеленая японская матча с взбитым молоком"
    },
    {
        "id": 6,
        "name": "Флэт Уайт",
        "price": 1400,
        "icon": "flatwhite",
        "cup_color": "#B8845A",
        "desc": "Двойной ристретто с бархатистой микропеной"
    },
    {
        "id": 7,
        "name": "Раф Ванильный",
        "price": 1600,
        "icon": "raf",
        "cup_color": "#D4A96A",
        "desc": "Эспрессо, взбитый со сливками 10% и натуральной ванилью"
    },
    {
        "id": 8,
        "name": "Моккачино с темным шоколадом",
        "price": 1650,
        "icon": "mocha",
        "cup_color": "#4A2C17",
        "desc": "Эспрессо, горячий бельгийский шоколад и нежное молоко"
    },
    {
        "id": 9,
        "name": "Бамбл-кофе (кофе + апельсиновый фреш)",
        "price": 1700,
        "icon": "bumble",
        "cup_color": "#E07B39",
        "desc": "Освежающий слоистый микс эспрессо, карамели и сока"
    },
    {
        "id": 10,
        "name": "Испанский латте со сгущенным молоком",
        "price": 1550,
        "icon": "spanish",
        "cup_color": "#D4924A",
        "desc": "Сливочно-сладкий латте на карамелизированной сгущенке"
    },
]

SIZE_OPTIONS = [
    {"label": "S", "ml": "250 мл", "extra": 0},
    {"label": "M", "ml": "350 мл", "extra": 250},
    {"label": "L", "ml": "450 мл", "extra": 450},
]

MILK_OPTIONS = [
    {"label": "Стандартное коровье", "extra": 0, "is_alt": False},
    {"label": "Овсяное Barista",    "extra": 350, "is_alt": True},
    {"label": "Кокосовое",          "extra": 350, "is_alt": True},
    {"label": "Миндальное",         "extra": 350, "is_alt": True},
    {"label": "Без молока",         "extra": 0,   "is_alt": False},
]

TEMP_OPTIONS = [
    "Стандартная горячая",
    "Экстра-горячий (85°C)",
    "Со льдом (Cold / Iced)"
]

SYRUPS = [
    {"label": "Ваниль",          "price": 150},
    {"label": "Соленая карамель", "price": 150},
    {"label": "Лесной орех",     "price": 150},
    {"label": "Лаванда",         "price": 150},
]

EXTRAS = [
    {"label": "Дополнительный эспрессо-шот", "price": 250},
    {"label": "Взбитые сливки",              "price": 200},
]

def fmt_price(val: int) -> str:
    """Форматирование цены в тенге с пробелом тысяч."""
    return f"{val:,} ₸".replace(",", " ")


# ─────────────────────────── МОДЕЛИ ДАННЫХ ──────────────────────────────── #

@dataclass
class OrderItem:
    """Элемент заказа с полным списком кастомизаций."""
    name: str
    base_price: int
    size: str
    size_extra: int
    milk: str
    milk_extra: int
    milk_is_alt: bool
    temp: str
    syrups: Dict[str, int] = field(default_factory=dict)
    extras: List[str] = field(default_factory=list)
    extra_prices: Dict[str, int] = field(default_factory=dict)

    @property
    def total(self) -> int:
        t = self.base_price + self.size_extra + self.milk_extra
        for s, count in self.syrups.items():
            t += count * 150
        for e in self.extras:
            t += self.extra_prices.get(e, 0)
        return t

    def modifiers_list(self) -> List[tuple[str, bool]]:
        """Возвращает список (текст_модификатора, выделить_жирным)."""
        mods = []
        mods.append((f"Размер: {self.size}", False))
        if self.milk:
            mods.append((f"Молоко: {self.milk}", self.milk_is_alt))
        mods.append((f"Подача: {self.temp}", False))
        for syrup, count in self.syrups.items():
            if count > 0:
                mods.append((f"Сироп {syrup} ×{count}", True))
        for extra in self.extras:
            mods.append((f"+ {extra}", False))
        return mods


@dataclass
class KDSOrder:
    """Заказ в очереди Kitchen Display System."""
    number: int
    items: List[OrderItem]
    created_at: float = field(default_factory=time.time)
    status: str = "pending"  # pending | in_progress | done


class AppState(QObject):
    """Единый реактивный менеджер состояния POS & KDS."""
    cart_changed   = pyqtSignal()
    order_sent     = pyqtSignal(object)  # KDSOrder
    kds_order_done = pyqtSignal(int)     # order number

    def __init__(self):
        super().__init__()
        self.cart: List[OrderItem] = []
        self.kds_orders: List[KDSOrder] = []
        self._order_counter = 13  # Начинаем с номера #014

    def add_to_cart(self, item: OrderItem):
        self.cart.append(item)
        self.cart_changed.emit()

    def remove_from_cart(self, index: int):
        if 0 <= index < len(self.cart):
            self.cart.pop(index)
            self.cart_changed.emit()

    def checkout(self) -> Optional[KDSOrder]:
        if not self.cart:
            return None
        self._order_counter += 1
        order = KDSOrder(
            number=self._order_counter,
            items=list(self.cart),
            created_at=time.time(),
            status="pending"
        )
        self.kds_orders.append(order)
        self.cart.clear()
        self.cart_changed.emit()
        self.order_sent.emit(order)
        return order

    def complete_order(self, number: int):
        self.kds_orders = [o for o in self.kds_orders if o.number != number]
        self.kds_order_done.emit(number)

    @property
    def cart_total(self) -> int:
        return sum(item.total for item in self.cart)


# ────────────────────── ВЕКТОРНАЯ ОТРИСОВКА ИКОНОК ──────────────────────── #

def draw_drink_icon(icon_type: str, cup_color: str, size: int = 90) -> QPixmap:
    """
    Автономная отрисовка векторных кофейных чашек и стаканов через QPainter.
    Поддерживает латте-арт, слои градиента, дрип-фильтр, пену и матча.
    """
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    base_c = QColor(cup_color)
    foam_c = QColor("#F4EDE3")
    crema  = QColor("#9E6238")

    cx = size // 2
    w  = int(size * 0.60)
    h  = int(size * 0.54)
    x0 = cx - w // 2
    y0 = int(size * 0.28)

    # 1. Чашки с латте-артом (Капучино, Латте, Флэт Уайт, Раф, Испанский)
    if icon_type in ("cappuccino", "latte", "flatwhite", "raf", "spanish"):
        # Блюдце
        saucer_w = int(w * 1.30)
        saucer_h = int(h * 0.16)
        p.setBrush(QBrush(QColor(base_c.darker(140))))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(cx - saucer_w // 2, y0 + h - 2, saucer_w, saucer_h)

        # Ручка чашки
        handle_pen = QPen(base_c.darker(110), int(size * 0.055))
        p.setPen(handle_pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawArc(QRect(x0 + w - int(w * 0.12), y0 + int(h * 0.20), int(w * 0.32), int(h * 0.48)), -80 * 16, 160 * 16)

        # Корпус кружки
        body = QPainterPath()
        body.moveTo(x0, y0 + h * 0.12)
        body.cubicTo(x0, y0 + h * 0.8, x0 + w * 0.15, y0 + h, x0 + w * 0.5, y0 + h)
        body.cubicTo(x0 + w * 0.85, y0 + h, x0 + w, y0 + h * 0.8, x0 + w, y0 + h * 0.12)
        body.closeSubpath()

        grad = QLinearGradient(x0, y0, x0 + w, y0)
        grad.setColorAt(0.0, base_c.lighter(130))
        grad.setColorAt(1.0, base_c.darker(120))
        p.setBrush(QBrush(grad))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPath(body)

        # Шелковистая пенка
        p.setBrush(QBrush(foam_c))
        p.drawEllipse(x0 + 2, y0, w - 4, int(h * 0.24))

        # Латте-арт (аккуратное сердечко)
        p.setBrush(QBrush(crema if icon_type != "raf" else QColor("#D49C6B")))
        hx = cx
        hy = y0 + int(h * 0.10)
        r = max(2, int(size * 0.04))
        p.drawEllipse(hx - r * 2, hy - r, r * 2, r * 2)
        p.drawEllipse(hx, hy - r, r * 2, r * 2)
        triangle = QPainterPath()
        triangle.moveTo(hx - r * 2, hy)
        triangle.lineTo(hx + r * 2, hy)
        triangle.lineTo(hx, hy + int(r * 2.2))
        triangle.closeSubpath()
        p.drawPath(triangle)

    # 2. Высокий прозрачный стакан Американо
    elif icon_type == "americano":
        glass = QPainterPath()
        glass.moveTo(x0 + w * 0.08, y0)
        glass.lineTo(x0 + w * 0.16, y0 + h)
        glass.lineTo(x0 + w * 0.84, y0 + h)
        glass.lineTo(x0 + w * 0.92, y0)
        glass.closeSubpath()

        grad = QLinearGradient(x0, y0, x0 + w, y0)
        grad.setColorAt(0.0, QColor("#2B1D14"))
        grad.setColorAt(0.5, QColor("#4A3324"))
        grad.setColorAt(1.0, QColor("#22160F"))
        p.setBrush(QBrush(grad))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPath(glass)

        # Тонкая крема сверху
        p.setBrush(QBrush(QColor("#9E6A38")))
        p.drawEllipse(int(x0 + w * 0.08), y0, int(w * 0.84), int(h * 0.16))

        # Стеклянный блик
        p.setBrush(QBrush(QColor(255, 255, 255, 30)))
        p.drawRect(int(x0 + w * 0.20), y0 + 4, int(w * 0.10), h - 10)

    # 3. Фильтр-кофе (V60 дриппер + стеклянный сертифицированный декантер)
    elif icon_type == "filter":
        funnel = QPainterPath()
        funnel.moveTo(cx - w * 0.40, y0)
        funnel.lineTo(cx + w * 0.40, y0)
        funnel.lineTo(cx + w * 0.15, y0 + h * 0.38)
        funnel.lineTo(cx - w * 0.15, y0 + h * 0.38)
        funnel.closeSubpath()
        p.setBrush(QBrush(QColor("#E4D2BE")))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPath(funnel)

        carafe = QPainterPath()
        cy0 = int(y0 + h * 0.44)
        ch  = int(h * 0.56)
        carafe.moveTo(cx - w * 0.20, cy0)
        carafe.lineTo(cx - w * 0.45, cy0 + ch)
        carafe.lineTo(cx + w * 0.45, cy0 + ch)
        carafe.lineTo(cx + w * 0.20, cy0)
        carafe.closeSubpath()

        p.setBrush(QBrush(QColor("#543825")))
        p.drawPath(carafe)

        p.setPen(QPen(QColor("#543825"), 2))
        p.drawLine(cx, int(y0 + h * 0.38), cx, cy0)

    # 4. Церемониальная матча в японской чаше
    elif icon_type == "matcha":
        bowl = QPainterPath()
        bowl.moveTo(x0, y0 + h * 0.35)
        bowl.cubicTo(x0, y0 + h * 0.8, cx - w * 0.2, y0 + h, cx, y0 + h)
        bowl.cubicTo(cx + w * 0.2, y0 + h, x0 + w, y0 + h * 0.8, x0 + w, y0 + h * 0.35)
        bowl.closeSubpath()

        p.setBrush(QBrush(QColor("#243D2A")))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPath(bowl)

        p.setBrush(QBrush(QColor("#5A9E6E")))
        p.drawEllipse(x0 + 2, int(y0 + h * 0.28), w - 4, int(h * 0.22))
        p.setBrush(QBrush(QColor("#8ED6A2")))
        p.drawEllipse(cx - int(w * 0.25), int(y0 + h * 0.30), int(w * 0.50), int(h * 0.12))

    # 5. Моккачино с темным шоколадом (слоистый стакан)
    elif icon_type == "mocha":
        glass = QPainterPath()
        glass.moveTo(x0 + w * 0.08, y0)
        glass.lineTo(x0 + w * 0.16, y0 + h)
        glass.lineTo(x0 + w * 0.84, y0 + h)
        glass.lineTo(x0 + w * 0.92, y0)
        glass.closeSubpath()

        p.setBrush(QBrush(QColor("#402B1E")))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPath(glass)

        p.setBrush(QBrush(QColor("#1E110A")))
        p.drawRect(int(x0 + w * 0.14), int(y0 + h * 0.65), int(w * 0.72), int(h * 0.35))

        p.setBrush(QBrush(foam_c))
        p.drawEllipse(int(x0 + w * 0.08), y0 - 4, int(w * 0.84), int(h * 0.24))

    # 6. Бамбл-кофе (апельсиновый сок + эспрессо + соломинка)
    elif icon_type == "bumble":
        glass = QPainterPath()
        glass.moveTo(x0 + w * 0.08, y0)
        glass.lineTo(x0 + w * 0.16, y0 + h)
        glass.lineTo(x0 + w * 0.84, y0 + h)
        glass.lineTo(x0 + w * 0.92, y0)
        glass.closeSubpath()

        p.setBrush(QBrush(QColor("#E67E22")))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPath(glass)

        p.setBrush(QBrush(QColor("#2C180E")))
        p.drawRect(int(x0 + w * 0.10), y0, int(w * 0.80), int(h * 0.45))

        p.setBrush(QBrush(QColor(255, 255, 255, 50)))
        p.drawRoundedRect(int(cx - w * 0.20), int(y0 + h * 0.25), int(w * 0.20), int(w * 0.20), 3, 3)

        straw_pen = QPen(QColor("#F39C12"), int(size * 0.045))
        p.setPen(straw_pen)
        p.drawLine(cx + int(w * 0.20), int(y0 - size * 0.14), cx + int(w * 0.10), y0 + h)

    p.setPen(QPen(QColor(255, 255, 255, 12), 1))
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawRoundedRect(1, 1, size - 2, size - 2, 12, 12)

    p.end()
    return px


# ─────────────────────── ВСПОМОГАТЕЛЬНЫЕ КОМПОНЕНТЫ ────────────────────── #

def create_label(text: str, size: int = 13, bold: bool = False,
                 color: str = C_TEXT, align=Qt.AlignmentFlag.AlignLeft) -> QLabel:
    lbl = QLabel(text)
    font = QFont("Segoe UI", size)
    font.setBold(bold)
    lbl.setFont(font)
    lbl.setStyleSheet(f"color: {color}; background: transparent;")
    lbl.setAlignment(align)
    return lbl


class HoverCard(QFrame):
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._normal_style = ""
        self._hover_style  = ""

    def setup_styles(self, normal: str, hover: str):
        self._normal_style = normal
        self._hover_style  = hover
        self.setStyleSheet(normal)

    def enterEvent(self, event):
        self.setStyleSheet(self._hover_style)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet(self._normal_style)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class SyrupCounter(QWidget):
    value_changed = pyqtSignal()

    def __init__(self, label: str, price: int):
        super().__init__()
        self.label_text = label
        self.price = price
        self._count = 0
        self._init_ui()

    def _init_ui(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        title = create_label(self.label_text, 13, bold=False, color=C_TEXT)
        title.setMinimumWidth(140)
        lay.addWidget(title)
        lay.addStretch()

        btn_css = (
            f"QPushButton {{ background: {C_CARD}; color: {C_TEXT};"
            f" border: 1px solid {C_BORDER}; border-radius: 8px;"
            f" font-size: 16px; font-weight: bold; min-width: 32px; min-height: 32px; }}"
            f"QPushButton:hover {{ background: {C_BORDER_HOVER}; border-color: {C_ACCENT}; }}"
            f"QPushButton:pressed {{ background: {C_ACCENT}; color: #fff; }}"
        )
        self.btn_minus = QPushButton("−")
        self.btn_minus.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_minus.setStyleSheet(btn_css)
        self.btn_minus.setFixedSize(32, 32)
        self.btn_minus.clicked.connect(self._decrement)

        self.count_lbl = create_label("0", 13, bold=True, color=C_TEXT, align=Qt.AlignmentFlag.AlignCenter)
        self.count_lbl.setFixedWidth(28)

        self.btn_plus = QPushButton("+")
        self.btn_plus.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_plus.setStyleSheet(btn_css)
        self.btn_plus.setFixedSize(32, 32)
        self.btn_plus.clicked.connect(self._increment)

        price_tag = create_label(f"+{self.price} ₸", 11, color=C_TEXT_MUTED)
        price_tag.setMinimumWidth(55)

        lay.addWidget(self.btn_minus)
        lay.addWidget(self.count_lbl)
        lay.addWidget(self.btn_plus)
        lay.addWidget(price_tag)

    def _increment(self):
        self._count += 1
        self.count_lbl.setText(str(self._count))
        self.count_lbl.setStyleSheet(f"color: {C_ACCENT}; font-weight: bold;")
        self.value_changed.emit()

    def _decrement(self):
        if self._count > 0:
            self._count -= 1
            self.count_lbl.setText(str(self._count))
            if self._count == 0:
                self.count_lbl.setStyleSheet(f"color: {C_TEXT}; font-weight: bold;")
            self.value_changed.emit()

    @property
    def count(self) -> int:
        return self._count


class ToastNotification(QFrame):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setStyleSheet(
            f"QFrame {{ background: {C_CARD}; border: 2px solid {C_GREEN};"
            f" border-radius: 14px; padding: 10px 20px; }}"
        )
        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(10)

        dot = create_label("●", 16, bold=True, color=C_GREEN)
        self.msg_lbl = create_label("", 13, bold=True, color=C_TEXT)
        lay.addWidget(dot)
        lay.addWidget(self.msg_lbl)

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._fade_out)
        self.hide()

    def show_toast(self, text: str, duration_ms: int = 3000):
        self.msg_lbl.setText(text)
        self.adjustSize()
        pw = self.parent().width()
        ph = self.parent().height()
        self.move((pw - self.width()) // 2, ph - self.height() - 40)
        self.show()
        self.raise_()

        self.opacity_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_anim.setDuration(250)
        self.opacity_anim.setStartValue(0.0)
        self.opacity_anim.setEndValue(1.0)
        self.opacity_anim.start()

        self._timer.start(duration_ms)

    def _fade_out(self):
        self.fade_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_anim.setDuration(350)
        self.fade_anim.setStartValue(1.0)
        self.fade_anim.setEndValue(0.0)
        self.fade_anim.finished.connect(self.hide)
        self.fade_anim.start()


# ────────────────────── МОДАЛЬНЫЙ КОНСТРУКТОР НАПИТКА ──────────────────── #

class CustomizeDialog(QDialog):
    def __init__(self, item_data: dict, parent=None):
        super().__init__(parent)
        self.item_data = item_data
        self.result_item: Optional[OrderItem] = None
        self._init_ui()

    def _init_ui(self):
        clean_name = self.item_data["name"].replace("\n", " ")
        self.setWindowTitle(f"Настроить напиток: {clean_name}")
        self.setMinimumWidth(540)
        self.setMaximumWidth(620)
        self.setStyleSheet(f"QDialog {{ background: {C_BG}; color: {C_TEXT}; }}")

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 22, 24, 22)
        root.setSpacing(16)

        header_row = QHBoxLayout()
        icon_px = draw_drink_icon(self.item_data["icon"], self.item_data["cup_color"], 64)
        icon_lbl = QLabel()
        icon_lbl.setPixmap(icon_px)
        icon_lbl.setFixedSize(64, 64)

        info_box = QVBoxLayout()
        info_box.setSpacing(4)
        title_lbl = create_label(clean_name, 17, bold=True)
        desc_lbl  = create_label(self.item_data.get("desc", ""), 11, color=C_TEXT_MUTED)
        desc_lbl.setWordWrap(True)
        base_lbl  = create_label(f"Базовая цена: {fmt_price(self.item_data['price'])}", 12, bold=True, color=C_ACCENT)
        info_box.addWidget(title_lbl)
        info_box.addWidget(desc_lbl)
        info_box.addWidget(base_lbl)

        header_row.addWidget(icon_lbl)
        header_row.addSpacing(14)
        header_row.addLayout(info_box, 1)
        root.addLayout(header_row)

        self._add_sep(root)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        container.setStyleSheet(f"background: {C_BG};")
        lay = QVBoxLayout(container)
        lay.setContentsMargins(0, 0, 10, 0)
        lay.setSpacing(16)

        # 1. Размер
        lay.addWidget(create_label("1. ВЫБОР РАЗМЕРА", 11, bold=True, color=C_TEXT_MUTED))
        self.size_group = QButtonGroup(self)
        size_row = QHBoxLayout()
        size_row.setSpacing(10)
        for i, opt in enumerate(SIZE_OPTIONS):
            extra_txt = f" (+{opt['extra']} ₸)" if opt["extra"] else ""
            rb = self._create_chip_radio(f"{opt['label']}  •  {opt['ml']}{extra_txt}", self.size_group)
            if i == 0:
                rb.setChecked(True)
            size_row.addWidget(rb)
        lay.addLayout(size_row)

        self._add_sep(lay)

        # 2. Выбор молока
        lay.addWidget(create_label("2. ВЫБОР МОЛОКА", 11, bold=True, color=C_TEXT_MUTED))
        self.milk_group = QButtonGroup(self)
        milk_grid = QGridLayout()
        milk_grid.setSpacing(8)
        for i, opt in enumerate(MILK_OPTIONS):
            extra_txt = f" (+{opt['extra']} ₸)" if opt["extra"] else ""
            rb = self._create_chip_radio(f"{opt['label']}{extra_txt}", self.milk_group)
            if i == 0:
                rb.setChecked(True)
            milk_grid.addWidget(rb, i // 2, i % 2)
        lay.addLayout(milk_grid)

        self._add_sep(lay)

        # 3. Температура подачи
        lay.addWidget(create_label("3. ТЕМПЕРАТУРА ПОДАЧИ", 11, bold=True, color=C_TEXT_MUTED))
        self.temp_group = QButtonGroup(self)
        temp_row = QHBoxLayout()
        temp_row.setSpacing(10)
        for i, temp_name in enumerate(TEMP_OPTIONS):
            rb = self._create_chip_radio(temp_name, self.temp_group)
            if i == 0:
                rb.setChecked(True)
            temp_row.addWidget(rb)
        lay.addLayout(temp_row)

        self._add_sep(lay)

        # 4. Сиропы и сладость
        lay.addWidget(create_label("4. СИРОПЫ И СЛАДОСТЬ (150 ₸ за помпу)", 11, bold=True, color=C_TEXT_MUTED))
        self.syrup_widgets: List[SyrupCounter] = []
        for s in SYRUPS:
            sc = SyrupCounter(s["label"], s["price"])
            sc.value_changed.connect(self._recalculate_total)
            lay.addWidget(sc)
            self.syrup_widgets.append(sc)

        self._add_sep(lay)

        # 5. Дополнительно
        lay.addWidget(create_label("5. ДОПОЛНИТЕЛЬНО", 11, bold=True, color=C_TEXT_MUTED))
        self.extra_checkboxes: List[QCheckBox] = []
        for ex in EXTRAS:
            cb = QCheckBox(f"{ex['label']} (+{ex['price']} ₸)")
            cb.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            cb.setStyleSheet(
                f"QCheckBox {{ color: {C_TEXT}; font-size: 13px; spacing: 10px; padding: 4px 0; }}"
                f"QCheckBox::indicator {{ width: 20px; height: 20px; border-radius: 6px;"
                f" border: 1px solid {C_BORDER}; background: {C_CARD}; }}"
                f"QCheckBox::indicator:hover {{ border-color: {C_ACCENT}; }}"
                f"QCheckBox::indicator:checked {{ background: {C_ACCENT}; border-color: {C_ACCENT}; }}"
            )
            cb.stateChanged.connect(self._recalculate_total)
            lay.addWidget(cb)
            self.extra_checkboxes.append(cb)

        scroll.setWidget(container)
        root.addWidget(scroll, 1)

        self.submit_btn = QPushButton("Добавить в заказ • ... ₸")
        self.submit_btn.setMinimumHeight(52)
        self.submit_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.submit_btn.setStyleSheet(
            f"QPushButton {{ background: {C_ACCENT}; color: #ffffff; border: none;"
            f" border-radius: 14px; font-size: 15px; font-weight: bold; padding: 0 20px; }}"
            f"QPushButton:hover {{ background: {C_ACCENT_HOVER}; }}"
            f"QPushButton:pressed {{ background: {C_ACCENT}; padding-top: 2px; }}"
        )
        self.submit_btn.clicked.connect(self._on_submit)
        root.addWidget(self.submit_btn)

        self.size_group.buttonToggled.connect(lambda *_: self._recalculate_total())
        self.milk_group.buttonToggled.connect(lambda *_: self._recalculate_total())
        self._recalculate_total()

    def _create_chip_radio(self, text: str, group: QButtonGroup) -> QRadioButton:
        rb = QRadioButton(text)
        rb.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        rb.setStyleSheet(
            f"QRadioButton {{ color: {C_TEXT}; font-size: 12px; padding: 8px 12px;"
            f" border: 1px solid {C_BORDER}; border-radius: 10px; background: {C_CARD}; }}"
            f"QRadioButton:hover {{ border-color: {C_BORDER_HOVER}; background: {C_CARD_HOVER}; }}"
            f"QRadioButton:checked {{ border-color: {C_ACCENT}; color: {C_ACCENT}; background: #2A1E17; font-weight: bold; }}"
            f"QRadioButton::indicator {{ width: 0; height: 0; }}"
        )
        group.addButton(rb)
        return rb

    def _add_sep(self, layout):
        line = QFrame()
        line.setFixedHeight(1)
        line.setStyleSheet(f"background: {C_DIVIDER};")
        layout.addWidget(line)

    def _get_selected_size(self):
        for i, rb in enumerate(self.size_group.buttons()):
            if rb.isChecked():
                return SIZE_OPTIONS[i]
        return SIZE_OPTIONS[0]

    def _get_selected_milk(self):
        for i, rb in enumerate(self.milk_group.buttons()):
            if rb.isChecked():
                return MILK_OPTIONS[i]
        return MILK_OPTIONS[0]

    def _get_selected_temp(self):
        for i, rb in enumerate(self.temp_group.buttons()):
            if rb.isChecked():
                return TEMP_OPTIONS[i]
        return TEMP_OPTIONS[0]

    def _calculate_total(self) -> int:
        total = self.item_data["price"]
        total += self._get_selected_size()["extra"]
        total += self._get_selected_milk()["extra"]
        for sc in self.syrup_widgets:
            total += sc.count * 150
        for i, cb in enumerate(self.extra_checkboxes):
            if cb.isChecked():
                total += EXTRAS[i]["price"]
        return total

    def _recalculate_total(self):
        total = self._calculate_total()
        self.submit_btn.setText(f"Добавить в заказ • {fmt_price(total)}")

    def _on_submit(self):
        size_opt = self._get_selected_size()
        milk_opt = self._get_selected_milk()
        temp     = self._get_selected_temp()
        syrups   = {sc.label_text: sc.count for sc in self.syrup_widgets if sc.count > 0}
        extras   = [EXTRAS[i]["label"] for i, cb in enumerate(self.extra_checkboxes) if cb.isChecked()]
        prices   = {ex["label"]: ex["price"] for ex in EXTRAS}

        self.result_item = OrderItem(
            name=self.item_data["name"].replace("\n", " "),
            base_price=self.item_data["price"],
            size=f"{size_opt['label']} ({size_opt['ml']})",
            size_extra=size_opt["extra"],
            milk=milk_opt["label"],
            milk_extra=milk_opt["extra"],
            milk_is_alt=milk_opt["is_alt"],
            temp=temp,
            syrups=syrups,
            extras=extras,
            extra_prices=prices
        )
        self.accept()


# ────────────────────────── КАРТОЧКА НАПИТКА ────────────────────────────── #

class DrinkCard(HoverCard):
    def __init__(self, item_data: dict, parent=None):
        super().__init__(parent)
        self.item_data = item_data
        self._init_ui()

    def _init_ui(self):
        self.setFixedSize(192, 220)
        normal = (
            f"DrinkCard {{ background: {C_CARD}; border: 1px solid {C_BORDER};"
            f" border-radius: 14px; }}"
        )
        hover = (
            f"DrinkCard {{ background: {C_CARD_HOVER}; border: 1px solid {C_BORDER_HOVER};"
            f" border-radius: 14px; }}"
        )
        self.setup_styles(normal, hover)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(6)

        px = draw_drink_icon(self.item_data["icon"], self.item_data["cup_color"], 88)
        icon_lbl = QLabel()
        icon_lbl.setPixmap(px)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet("background: transparent;")
        lay.addWidget(icon_lbl)

        lay.addSpacing(4)

        clean_name = self.item_data["name"]
        name_lbl = create_label(clean_name, 12, bold=True, color=C_TEXT, align=Qt.AlignmentFlag.AlignCenter)
        name_lbl.setWordWrap(True)
        lay.addWidget(name_lbl)

        lay.addStretch()

        price_lbl = create_label(
            fmt_price(self.item_data["price"]),
            13, bold=True, color=C_ACCENT,
            align=Qt.AlignmentFlag.AlignCenter
        )
        lay.addWidget(price_lbl)


# ─────────────────────────── ПАНЕЛЬ КОРЗИНЫ ─────────────────────────────── #

class CartItemWidget(QFrame):
    remove_requested = pyqtSignal(int)

    def __init__(self, item: OrderItem, index: int, parent=None):
        super().__init__(parent)
        self.index = index
        self.setStyleSheet(
            f"QFrame {{ background: {C_BG}; border: 1px solid {C_BORDER}; border-radius: 10px; }}"
        )
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(4)

        top_row = QHBoxLayout()
        name_lbl = create_label(item.name, 13, bold=True, color=C_TEXT)
        name_lbl.setWordWrap(True)
        top_row.addWidget(name_lbl, 1)

        del_btn = QPushButton("✕")
        del_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        del_btn.setFixedSize(22, 22)
        del_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {C_TEXT_MUTED}; border: none;"
            f" font-size: 11px; border-radius: 11px; }}"
            f"QPushButton:hover {{ background: #381A1A; color: {C_RED}; }}"
        )
        del_btn.clicked.connect(lambda: self.remove_requested.emit(self.index))
        top_row.addWidget(del_btn)
        lay.addLayout(top_row)

        for mod_text, is_bold in item.modifiers_list():
            col = C_YELLOW if is_bold else C_TEXT_MUTED
            mod_lbl = create_label(f"• {mod_text}", 10, bold=is_bold, color=col)
            mod_lbl.setWordWrap(True)
            lay.addWidget(mod_lbl)

        price_lbl = create_label(fmt_price(item.total), 12, bold=True, color=C_ACCENT, align=Qt.AlignmentFlag.AlignRight)
        lay.addWidget(price_lbl)


class CartPanel(QFrame):
    checkout_requested = pyqtSignal()

    def __init__(self, state: AppState, parent=None):
        super().__init__(parent)
        self.state = state
        self.setFixedWidth(340)
        self.setStyleSheet(
            f"CartPanel {{ background: {C_CARD}; border-left: 1px solid {C_BORDER}; border-radius: 0; }}"
        )
        self._init_ui()
        self.state.cart_changed.connect(self._render_cart)

    def _init_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 22, 18, 22)
        lay.setSpacing(14)

        header_row = QHBoxLayout()
        title = create_label("Текущий заказ", 17, bold=True)
        self.badge = create_label("0 поз.", 12, color=C_TEXT_MUTED)
        header_row.addWidget(title)
        header_row.addStretch()
        header_row.addWidget(self.badge)
        lay.addLayout(header_row)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {C_DIVIDER};")
        lay.addWidget(sep)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.list_container = QWidget()
        self.list_container.setStyleSheet("background: transparent;")
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(0, 0, 6, 0)
        self.list_layout.setSpacing(10)
        self.list_layout.addStretch()

        self.scroll.setWidget(self.list_container)
        lay.addWidget(self.scroll, 1)

        self.empty_widget = QWidget()
        empty_lay = QVBoxLayout(self.empty_widget)
        empty_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_icon = create_label("☕", 32, align=Qt.AlignmentFlag.AlignCenter)
        empty_txt = create_label(
            "Корзина пуста\n\nВыберите напиток из каталога слева для настройки",
            12, color=C_TEXT_MUTED, align=Qt.AlignmentFlag.AlignCenter
        )
        empty_txt.setWordWrap(True)
        empty_lay.addWidget(empty_icon)
        empty_lay.addWidget(empty_txt)
        lay.addWidget(self.empty_widget)

        sep2 = QFrame()
        sep2.setFixedHeight(1)
        sep2.setStyleSheet(f"background: {C_DIVIDER};")
        lay.addWidget(sep2)

        total_row = QHBoxLayout()
        total_row.addWidget(create_label("Итого к оплате:", 14, bold=True))
        total_row.addStretch()
        self.total_lbl = create_label("0 ₸", 18, bold=True, color=C_ACCENT)
        total_row.addWidget(self.total_lbl)
        lay.addLayout(total_row)

        self.pay_btn = QPushButton("Оплатить и отправить заказ")
        self.pay_btn.setMinimumHeight(54)
        self.pay_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.pay_btn.setStyleSheet(
            f"QPushButton {{ background: {C_ACCENT}; color: #ffffff; border: none;"
            f" border-radius: 14px; font-size: 14px; font-weight: bold; padding: 0 16px; }}"
            f"QPushButton:hover {{ background: {C_ACCENT_HOVER}; }}"
            f"QPushButton:pressed {{ background: {C_ACCENT}; padding-top: 2px; }}"
            f"QPushButton:disabled {{ background: {C_BORDER}; color: {C_TEXT_MUTED}; }}"
        )
        self.pay_btn.clicked.connect(self.checkout_requested.emit)
        lay.addWidget(self.pay_btn)

        self._render_cart()

    def _render_cart(self):
        while self.list_layout.count() > 1:
            child = self.list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        cart = self.state.cart
        count = len(cart)
        has_items = count > 0

        self.empty_widget.setVisible(not has_items)
        self.scroll.setVisible(has_items)
        self.pay_btn.setEnabled(has_items)
        self.badge.setText(f"{count} поз.")

        for i, item in enumerate(cart):
            row = CartItemWidget(item, i)
            row.remove_requested.connect(self.state.remove_from_cart)
            self.list_layout.insertWidget(self.list_layout.count() - 1, row)

        self.total_lbl.setText(fmt_price(self.state.cart_total))


# ─────────────────────── ЭКРАН ТЕРМИНАЛА ЗАКАЗА ─────────────────────────── #

class OrderTerminalScreen(QWidget):
    def __init__(self, state: AppState, parent=None):
        super().__init__(parent)
        self.state = state
        self._toast = ToastNotification(self)
        self._init_ui()

    def _init_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        left_box = QWidget()
        left_box.setStyleSheet(f"background: {C_BG};")
        left_lay = QVBoxLayout(left_box)
        left_lay.setContentsMargins(28, 22, 28, 22)
        left_lay.setSpacing(16)

        header_box = QVBoxLayout()
        header_box.setSpacing(4)
        title = create_label("Каталог кофе и авторских напитков", 20, bold=True)
        subtitle = create_label("Нажмите на любой напиток, чтобы настроить размер, тип молока, температуру и сиропы", 12, color=C_TEXT_MUTED)
        header_box.addWidget(title)
        header_box.addWidget(subtitle)
        left_lay.addLayout(header_box)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        grid_container = QWidget()
        grid_container.setStyleSheet(f"background: {C_BG};")
        self.grid = QGridLayout(grid_container)
        self.grid.setSpacing(14)
        self.grid.setContentsMargins(0, 0, 0, 0)

        for idx, item in enumerate(MENU_ITEMS):
            card = DrinkCard(item)
            card.clicked.connect(lambda checked=False, d=item: self._open_customizer(d))
            self.grid.addWidget(card, idx // 4, idx % 4)

        scroll.setWidget(grid_container)
        left_lay.addWidget(scroll, 1)

        root.addWidget(left_box, 1)

        self.cart_panel = CartPanel(self.state)
        self.cart_panel.checkout_requested.connect(self._handle_checkout)
        root.addWidget(self.cart_panel)

    def _open_customizer(self, item_data: dict):
        dlg = CustomizeDialog(item_data, self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.result_item:
            self.state.add_to_cart(dlg.result_item)

    def _handle_checkout(self):
        order = self.state.checkout()
        if order:
            QApplication.beep()
            self._toast.show_toast(
                f"Заказ #{order.number:03d} успешно оплачен и отправлен на KDS!",
                3200
            )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._toast.isVisible():
            pw = self.width()
            ph = self.height()
            self._toast.move((pw - self._toast.width()) // 2, ph - self._toast.height() - 40)


# ────────────────────────── КАРТОЧКА ЗАКАЗА KDS ─────────────────────────── #

class KDSOrderCard(QFrame):
    done_clicked = pyqtSignal(int)

    def __init__(self, order: KDSOrder, parent=None):
        super().__init__(parent)
        self.order = order
        self._status = "pending"
        self._init_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_elapsed)
        self.timer.start(1000)
        self._update_elapsed()

    def _init_ui(self):
        self.setFixedWidth(300)
        self.setMinimumHeight(240)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.MinimumExpanding)
        self._apply_border_color(C_BORDER)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.header = QFrame()
        self.header.setFixedHeight(54)
        self.header.setStyleSheet(
            f"QFrame {{ background: {C_BORDER}; border-radius: 12px 12px 0 0; }}"
        )
        h_lay = QHBoxLayout(self.header)
        h_lay.setContentsMargins(14, 0, 14, 0)

        self.order_num_lbl = create_label(f"#{self.order.number:03d}", 20, bold=True, color="#ffffff")
        self.timer_badge = create_label("00:00", 14, bold=True, color=C_TEXT_MUTED)

        h_lay.addWidget(self.order_num_lbl)
        h_lay.addStretch()
        h_lay.addWidget(self.timer_badge)
        lay.addWidget(self.header)

        body = QFrame()
        body.setStyleSheet(
            f"QFrame {{ background: {C_CARD}; border-radius: 0 0 12px 12px; border: none; }}"
        )
        b_lay = QVBoxLayout(body)
        b_lay.setContentsMargins(14, 12, 14, 14)
        b_lay.setSpacing(8)

        for item in self.order.items:
            drink_title = create_label(f"• {item.name}", 13, bold=True, color=C_TEXT)
            drink_title.setWordWrap(True)
            b_lay.addWidget(drink_title)

            for mod_text, is_bold in item.modifiers_list():
                col = C_YELLOW if is_bold else C_TEXT_MUTED
                mod_lbl = create_label(f"    {mod_text}", 11, bold=is_bold, color=col)
                mod_lbl.setWordWrap(True)
                b_lay.addWidget(mod_lbl)

        b_lay.addSpacing(10)

        self.btn_work = QPushButton("▶  В работу")
        self.btn_work.setMinimumHeight(38)
        self.btn_work.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_work.setStyleSheet(
            f"QPushButton {{ background: #2A2312; color: {C_YELLOW};"
            f" border: 1px solid {C_YELLOW}; border-radius: 10px; font-size: 13px; font-weight: bold; }}"
            f"QPushButton:hover {{ background: #3D3215; }}"
            f"QPushButton:disabled {{ background: {C_CARD}; color: {C_TEXT_MUTED}; border-color: {C_BORDER}; }}"
        )
        self.btn_work.clicked.connect(self._mark_in_progress)
        b_lay.addWidget(self.btn_work)

        self.btn_done = QPushButton("✓  Готов к выдаче")
        self.btn_done.setMinimumHeight(38)
        self.btn_done.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_done.setStyleSheet(
            f"QPushButton {{ background: #0E291B; color: {C_GREEN};"
            f" border: 1px solid {C_GREEN}; border-radius: 10px; font-size: 13px; font-weight: bold; }}"
            f"QPushButton:hover {{ background: #16402A; }}"
        )
        self.btn_done.clicked.connect(self._mark_done)
        b_lay.addWidget(self.btn_done)

        lay.addWidget(body)

    def _apply_border_color(self, color_hex: str):
        self.setStyleSheet(
            f"KDSOrderCard {{ background: transparent; border: 2px solid {color_hex};"
            f" border-radius: 14px; }}"
        )

    def _update_elapsed(self):
        elapsed = int(time.time() - self.order.created_at)
        mins = elapsed // 60
        secs = elapsed % 60
        self.timer_badge.setText(f"{mins:02d}:{secs:02d}")

        if elapsed < 120:
            self.timer_badge.setStyleSheet(f"color: {C_TEXT_MUTED}; font-weight: bold; background: transparent;")
            if self._status == "pending":
                self._apply_border_color(C_BORDER)
        elif elapsed < 240:
            self.timer_badge.setStyleSheet(f"color: {C_YELLOW}; font-weight: bold; background: transparent;")
            if self._status == "pending":
                self._apply_border_color(C_YELLOW)
        else:
            self.timer_badge.setStyleSheet(f"color: {C_RED}; font-weight: bold; background: transparent;")
            self._apply_border_color(C_RED)

    def _mark_in_progress(self):
        self._status = "in_progress"
        self.order.status = "in_progress"
        self.header.setStyleSheet(
            f"QFrame {{ background: {C_YELLOW}; border-radius: 12px 12px 0 0; }}"
        )
        self.order_num_lbl.setStyleSheet("color: #141517; font-weight: bold; background: transparent;")
        self.timer_badge.setStyleSheet("color: #141517; font-weight: bold; background: transparent;")
        self.btn_work.setEnabled(False)
        self.btn_work.setText("◉  В процессе приготовления...")
        self._apply_border_color(C_YELLOW)

    def _mark_done(self):
        self.timer.stop()
        self.done_clicked.emit(self.order.number)


# ─────────────────────────── ЭКРАН БАРИСТА (KDS) ────────────────────────── #

class BaristKDSScreen(QWidget):
    def __init__(self, state: AppState, parent=None):
        super().__init__(parent)
        self.state = state
        self.cards: Dict[int, KDSOrderCard] = {}
        self._init_ui()
        self.state.order_sent.connect(self._on_incoming_order)

    def _init_ui(self):
        self.setStyleSheet(f"background: {C_BG};")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 22, 28, 22)
        lay.setSpacing(16)

        top_bar = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        title = create_label("Экран сборки заказов (KDS)", 20, bold=True)
        sub = create_label("Заказы поступают мгновенно без перезагрузки интерфейса", 12, color=C_TEXT_MUTED)
        title_box.addWidget(title)
        title_box.addWidget(sub)
        top_bar.addLayout(title_box)
        top_bar.addStretch()

        self.queue_badge = create_label("0 в очереди", 14, bold=True, color=C_ACCENT)
        top_bar.addWidget(self.queue_badge)
        lay.addLayout(top_bar)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {C_DIVIDER};")
        lay.addWidget(sep)

        legend = QHBoxLayout()
        legend.setSpacing(18)
        for col, desc in [
            (C_TEXT_MUTED, "До 2 мин: стандартное время"),
            (C_YELLOW, "От 2 до 4 мин: требуется внимание"),
            (C_RED, "Более 4 мин: срочный приоритет!")
        ]:
            dot = create_label("●", 14, color=col)
            txt = create_label(desc, 11, color=C_TEXT_MUTED)
            legend.addWidget(dot)
            legend.addWidget(txt)
        legend.addStretch()
        lay.addLayout(legend)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.cards_container = QWidget()
        self.cards_container.setStyleSheet("background: transparent;")
        self.cards_row = QHBoxLayout(self.cards_container)
        self.cards_row.setContentsMargins(0, 4, 0, 8)
        self.cards_row.setSpacing(18)
        self.cards_row.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        self.scroll.setWidget(self.cards_container)
        lay.addWidget(self.scroll, 1)

        self.empty_kds = QWidget()
        ek_lay = QVBoxLayout(self.empty_kds)
        ek_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ek_lay.setSpacing(10)
        icon_lbl = create_label("✨", 40, align=Qt.AlignmentFlag.AlignCenter)
        msg_lbl = create_label(
            "Все заказы приготовлены!\n\nНовые клиентские чеки появятся на этом экране автоматически",
            14, color=C_TEXT_MUTED, align=Qt.AlignmentFlag.AlignCenter
        )
        msg_lbl.setWordWrap(True)
        ek_lay.addWidget(icon_lbl)
        ek_lay.addWidget(msg_lbl)
        lay.addWidget(self.empty_kds, 1)

        self._refresh_state()

    def _on_incoming_order(self, order: KDSOrder):
        card = KDSOrderCard(order)
        card.done_clicked.connect(self._complete_order_animated)
        self.cards[order.number] = card
        self.cards_row.addWidget(card)
        self._refresh_state()

    def _complete_order_animated(self, order_num: int):
        if order_num in self.cards:
            card = self.cards.pop(order_num)
            effect = QGraphicsOpacityEffect(card)
            card.setGraphicsEffect(effect)

            anim = QPropertyAnimation(effect, b"opacity")
            anim.setDuration(350)
            anim.setStartValue(1.0)
            anim.setEndValue(0.0)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)

            def on_finished():
                self.cards_row.removeWidget(card)
                card.deleteLater()
                self._refresh_state()

            anim.finished.connect(on_finished)
            anim.start()
            self.state.complete_order(order_num)

    def _refresh_state(self):
        count = len(self.cards)
        self.queue_badge.setText(f"{count} в очереди" if count else "Очередь чиста")
        self.empty_kds.setVisible(count == 0)
        self.scroll.setVisible(count > 0)


# ────────────────────────── ВЕРХНИЙ ТАБ-БАР ─────────────────────────────── #

class TopTabBar(QWidget):
    tab_switched = pyqtSignal(int)

    def __init__(self, tab_names: List[str], parent=None):
        super().__init__(parent)
        self.setFixedHeight(60)
        self.setStyleSheet(f"background: {C_CARD}; border-bottom: 1px solid {C_BORDER};")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(28, 0, 28, 0)
        lay.setSpacing(0)

        logo_box = QHBoxLayout()
        logo_box.setSpacing(8)
        logo_icon = create_label("◈", 18, bold=True, color=C_ACCENT)
        logo_text = create_label("DRINKIT POS", 15, bold=True, color=C_TEXT)
        logo_box.addWidget(logo_icon)
        logo_box.addWidget(logo_text)
        lay.addLayout(logo_box)

        lay.addStretch()

        self.tab_buttons: List[QPushButton] = []
        for i, name in enumerate(tab_names):
            btn = QPushButton(name)
            btn.setFixedHeight(40)
            btn.setMinimumWidth(200)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.setCheckable(True)
            idx = i
            btn.clicked.connect(lambda checked=False, n=idx: self._select_tab(n))
            self.tab_buttons.append(btn)
            lay.addWidget(btn)

        lay.addStretch()
        self._select_tab(0)

    def _select_tab(self, index: int):
        for i, btn in enumerate(self.tab_buttons):
            active = (i == index)
            if active:
                btn.setStyleSheet(
                    f"QPushButton {{ background: #2A1E17; color: {C_ACCENT};"
                    f" border: none; border-bottom: 3px solid {C_ACCENT};"
                    f" border-radius: 0; font-size: 13px; font-weight: bold; padding: 0 16px; }}"
                )
            else:
                btn.setStyleSheet(
                    f"QPushButton {{ background: {C_CARD}; color: {C_TEXT_MUTED};"
                    f" border: none; border-bottom: 3px solid transparent;"
                    f" border-radius: 0; font-size: 13px; font-weight: normal; padding: 0 16px; }}"
                    f"QPushButton:hover {{ color: {C_TEXT}; background: {C_CARD_HOVER}; }}"
                )
            btn.setChecked(active)
        self.tab_switched.emit(index)


# ─────────────────────────── ГЛАВНОЕ ОКНО ──────────────────────────────── #

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.state = AppState()
        self.setWindowTitle("Drinkit — Умная касса и KDS кофейни")
        self.setMinimumSize(1240, 760)
        self.resize(1380, 840)
        self.setStyleSheet(f"QMainWindow {{ background: {C_BG}; }}")
        self._init_ui()

    def _init_ui(self):
        central = QWidget()
        central.setStyleSheet(f"background: {C_BG};")
        self.setCentralWidget(central)

        main_lay = QVBoxLayout(central)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)

        self.tabbar = TopTabBar(["🛒  Терминал заказа", "👨‍🍳  Экран бариста (KDS)"])
        self.tabbar.tab_switched.connect(self._on_tab_change)
        main_lay.addWidget(self.tabbar)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background: {C_BG};")

        self.order_screen   = OrderTerminalScreen(self.state)
        self.barista_screen = BaristKDSScreen(self.state)

        self.stack.addWidget(self.order_screen)
        self.stack.addWidget(self.barista_screen)

        main_lay.addWidget(self.stack, 1)

    def _on_tab_change(self, index: int):
        self.stack.setCurrentIndex(index)


# ──────────────────────────── ТОЧКА ВХОДА ──────────────────────────────── #

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    palette = QPalette()
    bg = QColor(C_BG)
    palette.setColor(QPalette.ColorRole.Window, bg)
    palette.setColor(QPalette.ColorRole.WindowText, QColor(C_TEXT))
    palette.setColor(QPalette.ColorRole.Base, QColor(C_CARD))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(C_CARD))
    palette.setColor(QPalette.ColorRole.Text, QColor(C_TEXT))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(C_TEXT))
    palette.setColor(QPalette.ColorRole.Button, QColor(C_CARD))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(C_ACCENT))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
