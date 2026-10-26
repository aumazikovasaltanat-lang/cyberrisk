"""
Lo-Fi Focus & Audio Companion
Retrofuturistic Hi-Fi Desktop Application
Autonomous, procedural audio generation and pomodoro session timer.
"""

import sys
import math
import time
import numpy as np

from PyQt6.QtCore import (
    Qt, QThread, QTimer, pyqtSignal, QRectF, QPointF, QSize, QMutex, QMutexLocker
)
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QLinearGradient, QRadialGradient,
    QFont, QPainterPath, QIcon, QAction, QKeySequence, QPalette
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QSlider, QCheckBox, QFrame,
    QGraphicsDropShadowEffect, QSizePolicy, QToolTip
)
from PyQt6.QtMultimedia import QAudioFormat, QAudioSink, QMediaDevices

# ==============================================================================
# COLOR PALETTE & RETRO HI-FI CONSTANTS
# ==============================================================================
COLOR_BG            = "#16171A"  # Deep matte graphite
COLOR_CARD          = "#212328"  # Noble dark grey
COLOR_CARD_HOVER    = "#272A31"  # Slightly lighter card hover
COLOR_CARD_BORDER   = "#2D313A"  # Subtle brushed border
COLOR_ORANGE        = "#FF6B35"  # Warm analog orange accent
COLOR_ORANGE_HOVER  = "#FF8252"  # Lighter warm orange
COLOR_ORANGE_DIM    = "#7A351B"  # Muted orange for idle borders
COLOR_MINT          = "#4ECCA3"  # Neon mint accent
COLOR_MINT_BRIGHT   = "#9BFFDE"  # Bright mint peak highlight
COLOR_MINT_DARK     = "#194537"  # Deep teal base
COLOR_TEXT_PRIMARY  = "#EDEDED"  # Soft white
COLOR_TEXT_MUTED    = "#8E929B"  # Muted grey
COLOR_LCD_BG        = "#0C0D10"  # Recessed 80s LCD display background
COLOR_LCD_BORDER    = "#1C1E24"  # Inset screen bezel


# ==============================================================================
# PROCEDURAL AUDIO SYNTHESIZERS (ZERO EXTERNAL FILES)
# ==============================================================================
class ProceduralAudioEngine:
    """
    Mathematical synthesis of ambient lo-fi soundscapes:
    - Rain with raindrops and wind modulation
    - Night forest with campfire rumble, spark crackles, and crickets
    - Vinyl record with surface noise, 33.3 RPM cyclic bump, and dust clicks
    - Coffee shop with warm analog drone chord, distant crowd murmur, and cup pings
    - Meditative Solfeggio bell chime for session completion
    """
    def __init__(self, sample_rate=44100):
        self.sr = sample_rate
        self.time_phase = 0
        
        # State filters
        self.rain_lp = 0.0
        self.fire_lp = 0.0
        self.vinyl_rot_phase = 0.0
        
        # Precomputed filter kernels for vectorized speed
        k_size = 24
        self.rain_kernel = np.exp(-np.linspace(0, 3, k_size))
        self.rain_kernel /= np.sum(self.rain_kernel)
        
        self.fire_kernel = np.exp(-np.linspace(0, 4, 32))
        self.fire_kernel /= np.sum(self.fire_kernel)

        self.crowd_kernel = np.exp(-np.linspace(0, 2.5, 20))
        self.crowd_kernel /= np.sum(self.crowd_kernel)

    def generate_rain(self, n):
        """Warm rain: pinkish filtered noise + slow wind swells + raindrop taps"""
        t = (self.time_phase + np.arange(n)) / self.sr
        # White noise through convolution low-pass
        w = np.random.uniform(-0.8, 0.8, n)
        rain_base = np.convolve(w, self.rain_kernel, mode='same')
        
        # Wind swell (0.09 Hz slow wave)
        wind = 0.75 + 0.25 * np.sin(2 * np.pi * 0.09 * t)
        
        # Discrete raindrop impacts on glass (sporadic damped sines)
        drops = np.zeros(n, dtype=np.float32)
        drop_indices = np.where(np.random.random(n) > 0.9972)[0]
        for idx in drop_indices:
            length = min(180, n - idx)
            ct = np.arange(length) / self.sr
            freq = np.random.uniform(1400, 2400)
            tone = np.sin(2 * np.pi * freq * ct) * np.exp(-ct * 180) * np.random.uniform(0.2, 0.5)
            drops[idx:idx + length] += tone
            
        return (rain_base * 2.2 + drops) * wind

    def generate_fire(self, n):
        """Campfire & night forest: low wood rumble + ember crackles + soft night crickets"""
        t = (self.time_phase + np.arange(n)) / self.sr
        # Low rumble of burning logs
        w = np.random.uniform(-0.9, 0.9, n)
        rumble = np.convolve(w, self.fire_kernel, mode='same') * 1.8
        
        # Popping embers and wood crackles
        crackles = np.zeros(n, dtype=np.float32)
        crackle_indices = np.where(np.random.random(n) > 0.9955)[0]
        for idx in crackle_indices:
            length = min(90, n - idx)
            decay = np.exp(-np.linspace(0, 7, length))
            crackles[idx:idx + length] += np.random.uniform(-1.0, 1.0, length) * decay * np.random.uniform(0.3, 0.8)
            
        # Distant peaceful night crickets (rhythmic 4.2 kHz chirp pulse)
        chirp_mod = (np.sin(2 * np.pi * 14 * t) > 0.7).astype(np.float32)
        cricket = np.sin(2 * np.pi * 4200 * t) * chirp_mod * 0.045
        
        return rumble + crackles + cricket

    def generate_vinyl(self, n):
        """Vinyl record: soft groove friction hiss + 33.3 RPM revolution bump + dust clicks"""
        t = (self.time_phase + np.arange(n)) / self.sr
        # Subtle surface hiss
        hiss = np.random.uniform(-0.07, 0.07, n)
        
        # 33.3 RPM rotation warp/groove bump (period = 1.8018 seconds)
        bump = (np.sin(2 * np.pi * 0.555 * t) ** 24) * 0.16
        
        # Sporadic dust clicks and micro-scratches
        pops = np.zeros(n, dtype=np.float32)
        pop_indices = np.where(np.random.random(n) > 0.9982)[0]
        for idx in pop_indices:
            length = min(60, n - idx)
            decay = np.exp(-np.linspace(0, 8, length))
            pops[idx:idx + length] += np.random.uniform(-0.85, 0.85) * decay
            
        return hiss + bump + pops

    def generate_coffee(self, n):
        """Coffee shop: warm Rhodes/pad drone chord + distant muffled chatter + cup pings"""
        t = (self.time_phase + np.arange(n)) / self.sr
        # Warm analog drone chord (A2 110Hz, E3 164.8Hz, C#3 138.6Hz) with gentle tape chorus
        drone = (
            np.sin(2 * np.pi * 110.0 * t) * 0.22 +
            np.sin(2 * np.pi * 164.81 * t + 0.3) * 0.16 +
            np.sin(2 * np.pi * 138.59 * t + 0.7) * 0.12 +
            np.sin(2 * np.pi * 220.0 * t + 1.1) * 0.08
        )
        
        # Distant room murmur (filtered speech-range noise)
        w = np.random.uniform(-0.15, 0.15, n)
        murmur = np.convolve(w, self.crowd_kernel, mode='same') * 1.5
        
        # Rare ceramic cup / saucer clink (2.5 kHz ping)
        clinks = np.zeros(n, dtype=np.float32)
        clink_indices = np.where(np.random.random(n) > 0.9997)[0]
        for idx in clink_indices:
            length = min(1200, n - idx)
            ct = np.arange(length) / self.sr
            clink = np.sin(2 * np.pi * 2550 * ct) * np.exp(-ct * 38) * 0.35
            clinks[idx:idx + length] += clink
            
        return drone + murmur + clinks

    @staticmethod
    def generate_chime(sample_rate=44100, duration=2.6):
        """Meditative Solfeggio 528 Hz singing bowl chime on timer completion"""
        n = int(sample_rate * duration)
        t = np.linspace(0, duration, n, endpoint=False)
        tone = (
            np.sin(2 * np.pi * 528.0 * t) * np.exp(-t * 1.4) * 0.50 +
            np.sin(2 * np.pi * 1056.0 * t) * np.exp(-t * 2.2) * 0.25 +
            np.sin(2 * np.pi * 1584.0 * t) * np.exp(-t * 3.5) * 0.15 +
            np.sin(2 * np.pi * 2112.0 * t) * np.exp(-t * 5.0) * 0.08
        )
        return tone.astype(np.float32)


# ==============================================================================
# AUDIO WORKER THREAD (Continuous, Glitch-Free QAudioSink Streaming)
# ==============================================================================
class AudioPlaybackWorker(QThread):
    spectrumReady = pyqtSignal(list, float, float)  # 32 bands, left RMS, right RMS

    def __init__(self, sample_rate=44100, chunk_size=2048):
        super().__init__()
        self.sr = sample_rate
        self.chunk_size = chunk_size
        self.running = True
        self.mutex = QMutex()
        
        # Channel configurations: [enabled, volume (0.0-1.0), smoothed_vol]
        self.channels = {
            "rain":   {"on": False, "vol": 0.65, "cur": 0.0},
            "fire":   {"on": False, "vol": 0.60, "cur": 0.0},
            "vinyl":  {"on": False, "vol": 0.55, "cur": 0.0},
            "coffee": {"on": False, "vol": 0.50, "cur": 0.0},
        }
        self.master_vol = 0.8
        self.is_muted = False
        
        # Pending one-shot sounds (chimes)
        self.pending_chimes = []
        
        self.dsp = ProceduralAudioEngine(self.sr)
        
        # FFT logarithmic band edges (32 bands from 50 Hz to 16000 Hz)
        self.freq_edges = np.logspace(np.log10(50), np.log10(16000), 33)
        self.rfft_freqs = np.fft.rfftfreq(self.chunk_size, 1.0 / self.sr)
        self.fft_window = np.hanning(self.chunk_size)

    def set_channel(self, name, enabled=None, volume=None):
        with QMutexLocker(self.mutex):
            if name in self.channels:
                if enabled is not None:
                    self.channels[name]["on"] = enabled
                if volume is not None:
                    self.channels[name]["vol"] = max(0.0, min(1.0, volume))

    def set_master_volume(self, volume):
        with QMutexLocker(self.mutex):
            self.master_vol = max(0.0, min(1.0, volume))

    def set_muted(self, muted):
        with QMutexLocker(self.mutex):
            self.is_muted = muted

    def trigger_chime(self):
        with QMutexLocker(self.mutex):
            chime_buf = ProceduralAudioEngine.generate_chime(self.sr)
            self.pending_chimes.append([chime_buf, 0])

    def stop(self):
        self.running = False
        self.wait(1000)

    def run(self):
        # Configure output format: 44.1 kHz, 16-bit Stereo PCM
        audio_format = QAudioFormat()
        audio_format.setSampleRate(self.sr)
        audio_format.setChannelCount(2)
        audio_format.setSampleFormat(QAudioFormat.SampleFormat.Int16)

        default_device = QMediaDevices.defaultAudioOutput()
        sink = QAudioSink(default_device, audio_format)
        sink.setBufferSize(self.sr * 4)  # ~1 second hardware buffer
        io_out = sink.start()

        if not io_out:
            print("Failed to start audio sink.")
            return

        chunk_bytes = self.chunk_size * 2 * 2  # 2 channels * 2 bytes/sample

        while self.running:
            # Check how much free space the sound card buffer has
            free_bytes = sink.bytesFree()
            if free_bytes >= chunk_bytes:
                # Generate mixed chunk
                left_ch, right_ch = self._generate_audio_chunk()
                
                # Interleave stereo 16-bit
                stereo = np.column_stack((left_ch, right_ch)).flatten()
                pcm = (stereo * 32000.0).astype(np.int16)
                
                io_out.write(pcm.tobytes())
                
                # Advance time phase
                self.dsp.time_phase += self.chunk_size
                
                # Compute FFT spectrum for visualizer
                mono = (left_ch + right_ch) * 0.5
                bands = self._calculate_spectrum(mono)
                l_rms = float(np.sqrt(np.mean(left_ch ** 2)))
                r_rms = float(np.sqrt(np.mean(right_ch ** 2)))
                self.spectrumReady.emit(bands, l_rms, r_rms)
            else:
                self.msleep(8)

        sink.stop()

    def _generate_audio_chunk(self):
        n = self.chunk_size
        mix = np.zeros(n, dtype=np.float32)

        with QMutexLocker(self.mutex):
            # Smooth volume transitions to avoid digital clicks
            smooth_factor = 0.08
            master = 0.0 if self.is_muted else self.master_vol
            
            # Channel 1: Rain
            ch = self.channels["rain"]
            target = ch["vol"] if ch["on"] else 0.0
            ch["cur"] += smooth_factor * (target - ch["cur"])
            if ch["cur"] > 0.001:
                mix += self.dsp.generate_rain(n) * ch["cur"]

            # Channel 2: Fire
            ch = self.channels["fire"]
            target = ch["vol"] if ch["on"] else 0.0
            ch["cur"] += smooth_factor * (target - ch["cur"])
            if ch["cur"] > 0.001:
                mix += self.dsp.generate_fire(n) * ch["cur"]

            # Channel 3: Vinyl
            ch = self.channels["vinyl"]
            target = ch["vol"] if ch["on"] else 0.0
            ch["cur"] += smooth_factor * (target - ch["cur"])
            if ch["cur"] > 0.001:
                mix += self.dsp.generate_vinyl(n) * ch["cur"]

            # Channel 4: Coffee
            ch = self.channels["coffee"]
            target = ch["vol"] if ch["on"] else 0.0
            ch["cur"] += smooth_factor * (target - ch["cur"])
            if ch["cur"] > 0.001:
                mix += self.dsp.generate_coffee(n) * ch["cur"]

            # Apply Master Volume
            mix *= master

            # Mix any active chime signals
            active_chimes = []
            for chime_data, pos in self.pending_chimes:
                rem = len(chime_data) - pos
                take = min(n, rem)
                mix[:take] += chime_data[pos:pos + take] * 0.95
                if pos + take < len(chime_data):
                    active_chimes.append([chime_data, pos + take])
            self.pending_chimes = active_chimes

        # Analog Soft Saturation Limiter (warm tape compression, zero digital clipping)
        mix = np.tanh(mix * 1.1)

        # Subtle stereo width: slight delay/filter variance between L and R
        left = mix
        right = np.roll(mix, 12)  # 12 samples ~0.27ms psychoacoustic stereo widening
        return left, right

    def _calculate_spectrum(self, mono):
        """Calculates 32 logarithmic frequency bands via numpy FFT"""
        windowed = mono * self.fft_window
        fft_vals = np.abs(np.fft.rfft(windowed)) / self.chunk_size
        
        bands = []
        for i in range(32):
            low, high = self.freq_edges[i], self.freq_edges[i + 1]
            mask = (self.rfft_freqs >= low) & (self.rfft_freqs < high)
            if np.any(mask):
                energy = float(np.mean(fft_vals[mask]))
                # Scale logarithmically for visually pleasing meter response
                meter_val = min(1.0, math.sqrt(energy) * 8.5)
            else:
                meter_val = 0.0
            bands.append(meter_val)
        return bands


# ==============================================================================
# CUSTOM RETRO HI-FI WIDGETS
# ==============================================================================

class AnalogKnob(QWidget):
    """
    Tactile circular rotary knob with brushed metallic finish, illuminated arc,
    and smooth vertical drag / mouse wheel control.
    """
    valueChanged = pyqtSignal(int)

    def __init__(self, value=70, parent=None, accent_color=COLOR_ORANGE):
        super().__init__(parent)
        self.setFixedSize(56, 56)
        self.value = value  # 0 to 100
        self.accent_color = QColor(accent_color)
        self._dragging = False
        self._last_y = 0
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(f"Громкость: {self.value}%\n(Потяните вверх/вниз или прокрутите колесико)")

    def setValue(self, val):
        val = max(0, min(100, int(val)))
        if val != self.value:
            self.value = val
            self.setToolTip(f"Громкость: {self.value}%")
            self.valueChanged.emit(self.value)
            self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._last_y = event.position().y()
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            event.accept()

    def mouseMoveEvent(self, event):
        if self._dragging:
            delta_y = self._last_y - event.position().y()
            self._last_y = event.position().y()
            step = int(delta_y * 0.9)
            if step != 0:
                self.setValue(self.value + step)
            event.accept()

    def wheelEvent(self, event):
        delta = event.angleDelta().y() // 24
        self.setValue(self.value + delta)
        event.accept()

    def mouseDoubleClickEvent(self, event):
        self.setValue(70)  # Reset to standard 70%
        event.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(5, 5, 46, 46)
        center = rect.center()
        radius = 21.0

        # Background track arc (from 225° clockwise -270°)
        bg_pen = QPen(QColor("#2C2F38"), 3.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(bg_pen)
        painter.drawArc(rect, int(225 * 16), int(-270 * 16))

        # Active value illuminated arc
        frac = self.value / 100.0
        if frac > 0.005:
            active_pen = QPen(self.accent_color, 3.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            painter.setPen(active_pen)
            span = int(-270.0 * frac * 16)
            painter.drawArc(rect, int(225 * 16), span)

        # Inner knob body (brushed metal gradient)
        inner_rect = QRectF(center.x() - 15, center.y() - 15, 30, 30)
        grad = QLinearGradient(inner_rect.topLeft(), inner_rect.bottomRight())
        grad.setColorAt(0.0, QColor("#353842"))
        grad.setColorAt(0.5, QColor("#22242B"))
        grad.setColorAt(1.0, QColor("#18191E"))
        painter.setPen(QPen(QColor("#3E424D"), 1.2))
        painter.setBrush(QBrush(grad))
        painter.drawEllipse(inner_rect)

        # Concentric notch ring for texture
        painter.setPen(QPen(QColor("#18191E"), 0.8))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(inner_rect.adjusted(3, 3, -3, -3))

        # Pointer indicator dot/line
        angle_deg = 225.0 - frac * 270.0
        rad = math.radians(angle_deg)
        pt_x = center.x() + (radius - 9.0) * math.cos(rad)
        pt_y = center.y() - (radius - 9.0) * math.sin(rad)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self.accent_color))
        painter.drawEllipse(QPointF(pt_x, pt_y), 2.2, 2.2)

        # Subtle value percentage in center
        painter.setPen(QColor(COLOR_TEXT_PRIMARY))
        font = QFont("Segoe UI", 7, QFont.Weight.DemiBold)
        painter.setFont(font)
        painter.drawText(inner_rect, Qt.AlignmentFlag.AlignCenter, f"{self.value}%")


class RetroLED(QWidget):
    """Analog Hi-Fi LED indicator with authentic warm glow halo."""
    def __init__(self, color=COLOR_ORANGE, size=12, parent=None):
        super().__init__(parent)
        self.setFixedSize(size + 8, size + 8)
        self.base_color = QColor(color)
        self.active = False

    def setActive(self, is_on):
        if self.active != is_on:
            self.active = is_on
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        center = QPointF(self.width() / 2.0, self.height() / 2.0)
        r = (self.width() - 8) / 2.0

        if self.active:
            # Glow halo
            halo_grad = QRadialGradient(center, r + 4)
            halo_grad.setColorAt(0.0, QColor(self.base_color.red(), self.base_color.green(), self.base_color.blue(), 140))
            halo_grad.setColorAt(1.0, QColor(self.base_color.red(), self.base_color.green(), self.base_color.blue(), 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(halo_grad))
            painter.drawEllipse(center, r + 4, r + 4)

            # Core bulb
            bulb_grad = QRadialGradient(center.x() - 1, center.y() - 1, r)
            bulb_grad.setColorAt(0.0, QColor("#FFFFFF"))
            bulb_grad.setColorAt(0.4, self.base_color)
            bulb_grad.setColorAt(1.0, self.base_color.darker(140))
            painter.setBrush(QBrush(bulb_grad))
            painter.setPen(QPen(self.base_color.darker(160), 0.8))
            painter.drawEllipse(center, r, r)
        else:
            # Unlit LED
            painter.setPen(QPen(QColor("#1A1B20"), 1.0))
            painter.setBrush(QBrush(QColor("#2A2C34")))
            painter.drawEllipse(center, r, r)


class ChannelCardWidget(QFrame):
    """
    Atmosphere channel strip card:
    - Stylized Icon and genre badge
    - Channel Name & descriptive subtitle
    - Retro illuminated Toggle Button with LED
    - Tactile rotary knob
    - Dynamic mini 6-segment activity level meter
    """
    channelToggled = pyqtSignal(str, bool)
    volumeChanged = pyqtSignal(str, float)

    def __init__(self, channel_id, title, subtitle, icon_symbol, initial_vol=70, parent=None):
        super().__init__(parent)
        self.channel_id = channel_id
        self.is_active = False
        self.volume_level = initial_vol
        self.meter_activity = 0.0

        self.setObjectName("ChannelCard")
        self.setStyleSheet(f"""
            QFrame#ChannelCard {{
                background-color: {COLOR_CARD};
                border: 1px solid {COLOR_CARD_BORDER};
                border-radius: 10px;
            }}
            QFrame#ChannelCard:hover {{
                border: 1px solid #3A3E4A;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(12)

        # Left: Icon & LED badge
        icon_box = QVBoxLayout()
        icon_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.icon_label = QLabel(icon_symbol)
        self.icon_label.setStyleSheet(f"""
            font-size: 24px;
            background-color: #1A1C22;
            border: 1px solid #2B2E37;
            border-radius: 20px;
            padding: 4px;
        """)
        self.icon_label.setFixedSize(42, 42)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.led = RetroLED(color=COLOR_ORANGE, size=8)
        icon_box.addWidget(self.icon_label)
        icon_box.addSpacing(4)
        icon_box.addWidget(self.led, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(icon_box)

        # Middle: Title, Subtitle, Toggle button, and mini VU meter
        info_box = QVBoxLayout()
        info_box.setSpacing(4)
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 13px; font-weight: bold;")
        
        sub_lbl = QLabel(subtitle)
        sub_lbl.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 10px;")

        # Toggle Button
        self.toggle_btn = QPushButton("ВЫКЛ")
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setFixedHeight(26)
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._update_button_style(False)
        self.toggle_btn.toggled.connect(self._on_toggle)

        info_box.addWidget(title_lbl)
        info_box.addWidget(sub_lbl)
        info_box.addSpacing(2)
        info_box.addWidget(self.toggle_btn)
        layout.addLayout(info_box, stretch=1)

        # Right: Rotary Knob for volume
        knob_box = QVBoxLayout()
        knob_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        knob_box.setSpacing(2)

        self.knob = AnalogKnob(value=initial_vol, accent_color=COLOR_ORANGE)
        self.knob.valueChanged.connect(self._on_knob_changed)

        vol_caption = QLabel("LEVEL")
        vol_caption.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 8px; font-weight: bold; letter-spacing: 1px;")
        vol_caption.setAlignment(Qt.AlignmentFlag.AlignCenter)

        knob_box.addWidget(self.knob, alignment=Qt.AlignmentFlag.AlignCenter)
        knob_box.addWidget(vol_caption, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(knob_box)

    def _update_button_style(self, active):
        if active:
            self.toggle_btn.setText("ВКЛ • LIVE")
            self.toggle_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLOR_ORANGE};
                    color: #FFFFFF;
                    font-size: 10px;
                    font-weight: bold;
                    border: none;
                    border-radius: 5px;
                    padding: 2px 8px;
                }}
                QPushButton:hover {{
                    background-color: {COLOR_ORANGE_HOVER};
                }}
            """)
            self.led.setActive(True)
            self.icon_label.setStyleSheet(f"""
                font-size: 24px;
                background-color: #241E1C;
                border: 1px solid {COLOR_ORANGE};
                border-radius: 20px;
                padding: 4px;
            """)
        else:
            self.toggle_btn.setText("ВЫКЛ")
            self.toggle_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #1A1C22;
                    color: {COLOR_TEXT_MUTED};
                    font-size: 10px;
                    font-weight: bold;
                    border: 1px solid #2E323D;
                    border-radius: 5px;
                    padding: 2px 8px;
                }}
                QPushButton:hover {{
                    background-color: #232630;
                    color: {COLOR_TEXT_PRIMARY};
                }}
            """)
            self.led.setActive(False)
            self.icon_label.setStyleSheet(f"""
                font-size: 24px;
                background-color: #1A1C22;
                border: 1px solid #2B2E37;
                border-radius: 20px;
                padding: 4px;
            """)

    def _on_toggle(self, checked):
        self.is_active = checked
        self._update_button_style(checked)
        self.channelToggled.emit(self.channel_id, checked)

    def _on_knob_changed(self, value):
        self.volume_level = value
        self.volumeChanged.emit(self.channel_id, value / 100.0)

    def setChannelState(self, enabled, volume):
        self.toggle_btn.setChecked(enabled)
        self.knob.setValue(int(volume * 100))


# ==============================================================================
# LIVE AUDIO VISUALIZER (32-Band Spectrum Analyzer & Oscilloscope)
# ==============================================================================
class SpectrumVisualizer(QWidget):
    """
    Hi-Fi Graphic Equalizer:
    - 32 animated vertical bars responding dynamically to audio energy
    - Floating peak-hold markers with gravity decay (classic 80s Hi-Fi rack style)
    - Smooth mathematical sine wave modulation creating living organic motion
    - Fades to a flat neon resting line when all channels are silent
    - Frequency axis markings (63Hz to 16kHz) and dB scale
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(170)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)

        self.num_bars = 32
        self.current_levels = np.zeros(self.num_bars, dtype=np.float32)
        self.target_levels = np.zeros(self.num_bars, dtype=np.float32)
        self.peak_caps = np.zeros(self.num_bars, dtype=np.float32)

        self.stereo_l = 0.0
        self.stereo_r = 0.0
        self.phase = 0.0
        self.idle_phase = 0.0

        # Frequency scale labels
        self.freq_labels = [
            (1, "63"), (5, "125"), (9, "250"), (13, "500"),
            (17, "1k"), (21, "2k"), (25, "4k"), (29, "8k"), (31, "16k")
        ]

        # 50 FPS smooth render timer (~20 ms)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_frame)
        self.timer.start(20)

    def update_spectrum(self, bands, l_rms, r_rms):
        """Called from audio worker with fresh FFT data"""
        for i in range(min(len(bands), self.num_bars)):
            self.target_levels[i] = bands[i]
        self.stereo_l = l_rms
        self.stereo_r = r_rms

    def _update_frame(self):
        self.phase += 0.08
        self.idle_phase += 0.03
        
        # Calculate active energy
        active_sum = float(np.sum(self.target_levels))
        is_playing = active_sum > 0.04

        for i in range(self.num_bars):
            # Target energy with mathematical organic sine modulation
            if is_playing:
                sine_wave = (
                    0.09 * math.sin(self.phase * 2.2 + i * 0.35) +
                    0.05 * math.cos(self.phase * 1.4 - i * 0.22)
                )
                target = max(0.04, self.target_levels[i] + sine_wave * min(1.0, active_sum * 1.5))
            else:
                # Fades gracefully into a subtle resting neon line
                idle_breath = 0.015 + 0.008 * math.sin(self.idle_phase + i * 0.2)
                target = idle_breath

            # Attack / Release physics
            if target > self.current_levels[i]:
                self.current_levels[i] += 0.35 * (target - self.current_levels[i])
            else:
                self.current_levels[i] += 0.09 * (target - self.current_levels[i])

            # Peak hold caps with gravity decay
            if self.current_levels[i] > self.peak_caps[i]:
                self.peak_caps[i] = self.current_levels[i]
            else:
                self.peak_caps[i] = max(0.0, self.peak_caps[i] - 0.012)

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        # Outer bezel card background
        card_rect = QRectF(0, 0, w, h)
        painter.setPen(QPen(QColor(COLOR_CARD_BORDER), 1.0))
        painter.setBrush(QBrush(QColor(COLOR_LCD_BG)))
        painter.drawRoundedRect(card_rect, 10, 10)

        # Hi-Fi Analyzer Header
        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        painter.setPen(QColor(COLOR_TEXT_MUTED))
        painter.drawText(16, 22, "SPECTRUM ANALYZER // 32-BAND FFT DISPLAY")

        # Stereo VU Meters in top-right corner
        self._draw_stereo_meters(painter, w - 170, 12, 154, 14)

        # Plot area geometry
        margin_x = 22.0
        margin_top = 34.0
        margin_bottom = 26.0
        plot_w = w - 2.0 * margin_x
        plot_h = h - margin_top - margin_bottom
        baseline_y = margin_top + plot_h

        # Subtle horizontal dB grid lines
        painter.setPen(QPen(QColor("#1A1D24"), 1, Qt.PenStyle.DashLine))
        for db_frac in [0.25, 0.50, 0.75]:
            gy = margin_top + plot_h * (1.0 - db_frac)
            painter.drawLine(int(margin_x), int(gy), int(w - margin_x), int(gy))

        # Bar layout math
        bar_slot = plot_w / float(self.num_bars)
        bar_w = max(2.5, bar_slot * 0.72)
        gap = bar_slot - bar_w

        # Draw 32 Spectrum Bars
        for i in range(self.num_bars):
            bx = margin_x + i * bar_slot + gap * 0.5
            val = min(1.0, max(0.015, float(self.current_levels[i])))
            bar_height = val * plot_h
            by = baseline_y - bar_height

            # Gradient: Deep Teal -> Neon Mint -> Bright Mint Peak
            grad = QLinearGradient(bx, baseline_y, bx, by)
            grad.setColorAt(0.0, QColor(COLOR_MINT_DARK))
            grad.setColorAt(0.7, QColor(COLOR_MINT))
            grad.setColorAt(1.0, QColor(COLOR_MINT_BRIGHT))

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(grad))
            painter.drawRoundedRect(QRectF(bx, by, bar_w, bar_height), 2, 2)

            # Peak hold cap (floating bright line above bar)
            peak_val = min(1.0, max(0.02, float(self.peak_caps[i])))
            peak_y = baseline_y - peak_val * plot_h - 2.0
            painter.setPen(QPen(QColor(COLOR_MINT_BRIGHT), 1.6))
            painter.drawLine(int(bx), int(peak_y), int(bx + bar_w), int(peak_y))

        # Neon resting baseline
        painter.setPen(QPen(QColor(COLOR_MINT_DARK), 1.5))
        painter.drawLine(int(margin_x), int(baseline_y), int(w - margin_x), int(baseline_y))

        # Subtle Oscilloscope Waveform overlay
        self._draw_oscilloscope_wave(painter, margin_x, baseline_y, plot_w, plot_h)

        # Frequency Axis Labels
        painter.setFont(QFont("Segoe UI", 7, QFont.Weight.Normal))
        painter.setPen(QColor(COLOR_TEXT_MUTED))
        for bar_idx, label in self.freq_labels:
            if bar_idx < self.num_bars:
                lx = margin_x + bar_idx * bar_slot + bar_w * 0.5
                painter.drawText(QRectF(lx - 16, baseline_y + 4, 32, 16),
                                 Qt.AlignmentFlag.AlignCenter, label)

    def _draw_oscilloscope_wave(self, painter, start_x, base_y, width, height):
        """Subtle glowing oscilloscope waveform line moving across the display"""
        active_sum = float(np.sum(self.current_levels))
        if active_sum < 0.05:
            # Idle baseline with soft glow
            painter.setPen(QPen(QColor(78, 204, 163, 60), 1.2))
            painter.drawLine(int(start_x), int(base_y - 2), int(start_x + width), int(base_y - 2))
            return

        path = QPainterPath()
        points = 64
        dx = width / float(points - 1)
        
        amplitude = min(height * 0.45, active_sum * 12.0)
        center_y = base_y - height * 0.45

        for j in range(points):
            px = start_x + j * dx
            frac = j / float(points)
            # Harmonic wave function
            wave = (
                math.sin(self.phase * 3.5 + frac * 12.0) * 0.6 +
                math.sin(self.phase * 1.8 - frac * 6.0) * 0.3 +
                math.cos(self.phase * 5.2 + frac * 20.0) * 0.1
            )
            # Windowing envelope at sides
            env = math.sin(frac * math.pi)
            py = center_y + wave * amplitude * env
            if j == 0:
                path.moveTo(px, py)
            else:
                path.lineTo(px, py)

        # Glow line
        painter.setPen(QPen(QColor(78, 204, 163, 70), 3.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

        # Core bright trace
        painter.setPen(QPen(QColor("#B8FFE8"), 1.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawPath(path)

    def _draw_stereo_meters(self, painter, x, y, width, height):
        """Retro Hi-Fi Stereo Level Indicator (Left / Right)"""
        bar_h = 5.0
        labels = ["L", "R"]
        levels = [min(1.0, self.stereo_l * 5.0), min(1.0, self.stereo_r * 5.0)]

        painter.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
        for idx in range(2):
            by = y + idx * 7
            painter.setPen(QColor(COLOR_TEXT_MUTED))
            painter.drawText(int(x), int(by + 5), labels[idx])

            meter_x = x + 14
            meter_w = width - 14
            # Background
            painter.fillRect(QRectF(meter_x, by, meter_w, bar_h), QColor("#1C1E26"))
            # Lit segments
            fill_w = meter_w * levels[idx]
            if fill_w > 1:
                painter.fillRect(QRectF(meter_x, by, fill_w, bar_h), QColor(COLOR_MINT))


# ==============================================================================
# 80s DIGITAL CLOCK & FOCUS TIMER DISPLAY
# ==============================================================================
class RetroDigitalClockWidget(QWidget):
    """
    Iconic 80s VFD/LCD style digital clock display:
    - Inset bezel frame with recessed dark screen
    - Ghost unlit segments (88:88) beneath the active time digits
    - Glowing warm analog orange numerals with blinking colon
    - Integrated circular / linear session progress indicator
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(130)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        self.time_seconds = 25 * 60  # Default 25 min
        self.initial_seconds = 25 * 60
        self.is_running = False
        self.mode_name = "СЕАНС: ФОКУС"
        self.colon_visible = True

    def setTime(self, seconds, initial=None):
        self.time_seconds = max(0, seconds)
        if initial:
            self.initial_seconds = initial
        self.update()

    def setRunning(self, running):
        self.is_running = running
        self.update()

    def setMode(self, name):
        self.mode_name = name
        self.update()

    def setColonBlink(self, visible):
        self.colon_visible = visible
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        # Recessed display bezel
        bezel_rect = QRectF(0, 0, w, h)
        painter.setPen(QPen(QColor(COLOR_LCD_BORDER), 1.5))
        painter.setBrush(QBrush(QColor(COLOR_LCD_BG)))
        painter.drawRoundedRect(bezel_rect, 10, 10)

        # Mode title tag
        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        painter.setPen(QColor(COLOR_TEXT_MUTED))
        painter.drawText(16, 22, f"// {self.mode_name.upper()}")

        # Time formatting
        mins = self.time_seconds // 60
        secs = self.time_seconds % 60
        colon = ":" if (self.colon_visible or not self.is_running) else " "
        time_str = f"{mins:02d}{colon}{secs:02d}"

        clock_rect = QRectF(0, 20, w, h - 38)

        # 1. Ghost unlit digits (88:88)
        clock_font = QFont("Consolas", 46, QFont.Weight.Bold)
        clock_font.setStyleHint(QFont.StyleHint.Monospace)
        painter.setFont(clock_font)
        painter.setPen(QColor(255, 107, 53, 24))  # Very faint orange ghost
        painter.drawText(clock_rect, Qt.AlignmentFlag.AlignCenter, "88:88")

        # 2. Glowing Active Digits
        # Outer glow pass
        painter.setPen(QColor(255, 107, 53, 60))
        painter.drawText(clock_rect.adjusted(-1, 0, -1, 0), Qt.AlignmentFlag.AlignCenter, time_str)
        painter.drawText(clock_rect.adjusted(1, 0, 1, 0), Qt.AlignmentFlag.AlignCenter, time_str)

        # Crisp core digits
        painter.setPen(QColor(COLOR_ORANGE))
        painter.drawText(clock_rect, Qt.AlignmentFlag.AlignCenter, time_str)

        # Progress bar at bottom of LCD screen
        prog_margin = 18.0
        prog_w = w - 2.0 * prog_margin
        prog_y = h - 14.0
        prog_h = 4.0

        # Progress track
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("#1B1D25")))
        painter.drawRoundedRect(QRectF(prog_margin, prog_y, prog_w, prog_h), 2, 2)

        # Active progress fill
        if self.initial_seconds > 0:
            fraction = (self.initial_seconds - self.time_seconds) / float(self.initial_seconds)
            fraction = max(0.0, min(1.0, fraction))
            fill_w = prog_w * fraction
            if fill_w > 1:
                painter.setBrush(QBrush(QColor(COLOR_ORANGE)))
                painter.drawRoundedRect(QRectF(prog_margin, prog_y, fill_w, prog_h), 2, 2)


# ==============================================================================
# MAIN WINDOW: RETROFUTURISTIC LO-FI COMPANION
# ==============================================================================
class LoFiCompanionWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lo-Fi Focus & Audio Companion")
        self.resize(1040, 720)
        self.setMinimumSize(900, 640)

        # Session tracking state
        self.timer_seconds_remaining = 25 * 60
        self.timer_preset_seconds = 25 * 60
        self.is_timer_running = False
        self.completed_sessions = 0
        self.total_focus_seconds = 0
        self.current_mode = "focus"  # "focus" or "rest"

        # Visual Flash / Pulse state
        self.is_flashing = False
        self.flash_progress = 0.0
        self.flash_timer = QTimer(self)
        self.flash_timer.timeout.connect(self._update_border_flash)

        # 1-second countdown timer
        self.second_timer = QTimer(self)
        self.second_timer.timeout.connect(self._timer_tick)
        self.second_timer.start(1000)

        # Start procedural audio thread
        self.audio_worker = AudioPlaybackWorker()
        self.audio_worker.start()

        self._setup_ui()
        self._setup_shortcuts()

        # Connect spectrum stream to visualizer
        self.audio_worker.spectrumReady.connect(self.visualizer.update_spectrum)

    def _setup_ui(self):
        # Set overall dark palette
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLOR_BG};
            }}
            QWidget {{
                color: {COLOR_TEXT_PRIMARY};
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
            }}
            QToolTip {{
                background-color: #21242C;
                color: {COLOR_TEXT_PRIMARY};
                border: 1px solid #3B404E;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 11px;
            }}
        """)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(18, 16, 18, 14)
        main_layout.setSpacing(14)

        # ----------------------------------------------------------------------
        # 1. HEADER (Branding, Hardware Indicators, Master Volume)
        # ----------------------------------------------------------------------
        header = QHBoxLayout()
        header.setSpacing(12)

        # Title & Hi-Fi Logo
        title_box = QVBoxLayout()
        title_box.setSpacing(1)
        app_title = QLabel("LO-FI FOCUS // AUDIO COMPANION")
        app_title.setStyleSheet(f"font-size: 16px; font-weight: 800; letter-spacing: 1.5px; color: {COLOR_TEXT_PRIMARY};")
        
        app_sub = QLabel("SOLID-STATE DSP SYNTHESIZER • RETROFUTURISTIC HI-FI")
        app_sub.setStyleSheet(f"font-size: 9px; font-weight: bold; letter-spacing: 1px; color: {COLOR_MINT};")
        title_box.addWidget(app_title)
        title_box.addWidget(app_sub)
        header.addLayout(title_box)

        header.addStretch(1)

        # Master Volume Knob & Mute Control
        master_box = QHBoxLayout()
        master_box.setSpacing(8)
        
        self.mute_btn = QPushButton("🔊 ЗВУК")
        self.mute_btn.setCheckable(True)
        self.mute_btn.setFixedHeight(28)
        self.mute_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.mute_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #21242C;
                color: {COLOR_TEXT_PRIMARY};
                border: 1px solid {COLOR_CARD_BORDER};
                border-radius: 5px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                border-color: {COLOR_ORANGE};
            }}
            QPushButton:checked {{
                background-color: #381A1A;
                color: #FF7B7B;
                border-color: #882222;
            }}
        """)
        self.mute_btn.toggled.connect(self._toggle_mute)

        master_knob_lbl = QLabel("MASTER")
        master_knob_lbl.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 9px; font-weight: bold;")

        self.master_knob = AnalogKnob(value=80, accent_color=COLOR_ORANGE)
        self.master_knob.valueChanged.connect(self._on_master_vol_changed)

        master_box.addWidget(self.mute_btn)
        master_box.addSpacing(6)
        master_box.addWidget(master_knob_lbl)
        master_box.addWidget(self.master_knob)
        header.addLayout(master_box)

        main_layout.addLayout(header)

        # ----------------------------------------------------------------------
        # 2. CENTRAL VISUALIZER (32-Band Spectrum Equalizer)
        # ----------------------------------------------------------------------
        self.visualizer = SpectrumVisualizer(self)
        main_layout.addWidget(self.visualizer)

        # ----------------------------------------------------------------------
        # 3. LOWER SECTION: ATMOSPHERE MIXER (Left) + FOCUS TIMER (Right)
        # ----------------------------------------------------------------------
        content_layout = QHBoxLayout()
        content_layout.setSpacing(14)

        # --- LEFT PANEL: ATMOSPHERE SOUND MIXER ---
        mixer_panel = QFrame()
        mixer_panel.setStyleSheet(f"""
            QFrame {{
                background-color: #191B20;
                border: 1px solid {COLOR_CARD_BORDER};
                border-radius: 10px;
            }}
        """)
        mixer_layout = QVBoxLayout(mixer_panel)
        mixer_layout.setContentsMargins(14, 12, 14, 12)
        mixer_layout.setSpacing(10)

        # Mixer Header
        mixer_head = QHBoxLayout()
        m_title = QLabel("ГЕНЕРАТОР АТМОСФЕРЫ // АУДИОМИКШЕР")
        m_title.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        mixer_head.addWidget(m_title)
        mixer_head.addStretch(1)

        # Quick Mixer Presets
        preset_combo_lbl = QLabel("ПРЕСЕТ:")
        preset_combo_lbl.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 9px; font-weight: bold;")
        mixer_head.addWidget(preset_combo_lbl)

        btn_rain_preset = QPushButton("Дождь")
        btn_fire_preset = QPushButton("Костер")
        btn_lofi_preset = QPushButton("Всё ВКЛ")
        btn_clear_preset = QPushButton("Сброс")

        for b in [btn_rain_preset, btn_fire_preset, btn_lofi_preset, btn_clear_preset]:
            b.setFixedHeight(22)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(f"""
                QPushButton {{
                    background-color: #21242C;
                    color: {COLOR_TEXT_MUTED};
                    font-size: 9px;
                    font-weight: bold;
                    border: 1px solid #2F333E;
                    border-radius: 4px;
                    padding: 1px 6px;
                }}
                QPushButton:hover {{
                    color: {COLOR_TEXT_PRIMARY};
                    border-color: {COLOR_ORANGE};
                }}
            """)

        btn_rain_preset.clicked.connect(lambda: self._apply_mixer_preset("rain"))
        btn_fire_preset.clicked.connect(lambda: self._apply_mixer_preset("fire"))
        btn_lofi_preset.clicked.connect(lambda: self._apply_mixer_preset("all"))
        btn_clear_preset.clicked.connect(lambda: self._apply_mixer_preset("none"))

        mixer_head.addWidget(btn_rain_preset)
        mixer_head.addWidget(btn_fire_preset)
        mixer_head.addWidget(btn_lofi_preset)
        mixer_head.addWidget(btn_clear_preset)
        mixer_layout.addLayout(mixer_head)

        # 4 Independent Channels in 2x2 Grid
        grid = QGridLayout()
        grid.setSpacing(10)

        self.cards = {}
        channels_info = [
            ("rain",   "Дождь за окном",         "Мягкий ливень по стеклу",   "🌧️", 65, 0, 0),
            ("fire",   "Ночной лес и костер",    "Угли, треск и сверчки",     "🔥", 60, 0, 1),
            ("vinyl",  "Треск виниловой пластинки","33⅓ RPM, пыль и шероховатость","📻", 55, 1, 0),
            ("coffee", "Кофейный шум / Гул",     "Теплый дрон и атмосфера кафе","☕", 50, 1, 1),
        ]

        for cid, name, desc, icon, default_vol, row, col in channels_info:
            card = ChannelCardWidget(cid, name, desc, icon, initial_vol=default_vol, parent=self)
            card.channelToggled.connect(self._on_channel_toggled)
            card.volumeChanged.connect(self._on_channel_vol_changed)
            grid.addWidget(card, row, col)
            self.cards[cid] = card

        mixer_layout.addLayout(grid)
        content_layout.addWidget(mixer_panel, stretch=6)

        # --- RIGHT PANEL: FOCUS TIMER (POMODORO) ---
        timer_panel = QFrame()
        timer_panel.setStyleSheet(f"""
            QFrame {{
                background-color: #191B20;
                border: 1px solid {COLOR_CARD_BORDER};
                border-radius: 10px;
            }}
        """)
        timer_layout = QVBoxLayout(timer_panel)
        timer_layout.setContentsMargins(14, 12, 14, 12)
        timer_layout.setSpacing(10)

        # Timer Header
        t_header = QLabel("ФОКУС-ТАЙМЕР // СЕССИИ ПОМОДОРО")
        t_header.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        timer_layout.addWidget(t_header)

        # 80s Retro Digital Display Widget
        self.digital_clock = RetroDigitalClockWidget(self)
        timer_layout.addWidget(self.digital_clock)

        # Presets Buttons: Sprint (25m), Deep Work (50m), Rest (10m)
        presets_layout = QHBoxLayout()
        presets_layout.setSpacing(6)

        self.btn_preset_25 = QPushButton("25 мин (Спринт)")
        self.btn_preset_50 = QPushButton("50 мин (Работа)")
        self.btn_preset_10 = QPushButton("10 мин (Отдых)")

        for btn, mins, mode in [
            (self.btn_preset_25, 25, "focus"),
            (self.btn_preset_50, 50, "focus"),
            (self.btn_preset_10, 10, "rest")
        ]:
            btn.setFixedHeight(28)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLOR_CARD};
                    color: {COLOR_TEXT_PRIMARY};
                    border: 1px solid {COLOR_CARD_BORDER};
                    border-radius: 5px;
                    font-size: 10px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    border-color: {COLOR_ORANGE};
                    background-color: {COLOR_CARD_HOVER};
                }}
            """)
            btn.clicked.connect(lambda checked, m=mins, md=mode: self._set_timer_preset(m, md))
            presets_layout.addWidget(btn)

        timer_layout.addLayout(presets_layout)

        # Timer Controls: Start, Pause, Reset
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(8)

        self.btn_start = QPushButton("▶ СТАРТ")
        self.btn_start.setFixedHeight(34)
        self.btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_start.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_ORANGE};
                color: #FFFFFF;
                font-size: 12px;
                font-weight: 800;
                letter-spacing: 1px;
                border: none;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_ORANGE_HOVER};
            }}
        """)
        self.btn_start.clicked.connect(self._timer_start)

        self.btn_pause = QPushButton("❚❚ ПАУЗА")
        self.btn_pause.setFixedHeight(34)
        self.btn_pause.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pause.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_CARD};
                color: {COLOR_TEXT_PRIMARY};
                border: 1px solid {COLOR_CARD_BORDER};
                border-radius: 6px;
                font-size: 11px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLOR_CARD_HOVER};
                border-color: {COLOR_TEXT_MUTED};
            }}
        """)
        self.btn_pause.clicked.connect(self._timer_pause)

        self.btn_reset = QPushButton("↺ СБРОС")
        self.btn_reset.setFixedHeight(34)
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_CARD};
                color: {COLOR_TEXT_MUTED};
                border: 1px solid {COLOR_CARD_BORDER};
                border-radius: 6px;
                font-size: 11px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                color: {COLOR_TEXT_PRIMARY};
                border-color: {COLOR_TEXT_MUTED};
            }}
        """)
        self.btn_reset.clicked.connect(self._timer_reset)

        controls_layout.addWidget(self.btn_start, stretch=2)
        controls_layout.addWidget(self.btn_pause, stretch=1)
        controls_layout.addWidget(self.btn_reset, stretch=1)
        timer_layout.addLayout(controls_layout)

        # Fine-tune +/- 5 min buttons
        adjust_layout = QHBoxLayout()
        adjust_layout.setSpacing(6)
        btn_minus5 = QPushButton("- 5 мин")
        btn_plus5 = QPushButton("+ 5 мин")
        btn_test_chime = QPushButton("🔔 Тест колокольчика")

        for b in [btn_minus5, btn_plus5, btn_test_chime]:
            b.setFixedHeight(22)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {COLOR_TEXT_MUTED};
                    font-size: 9px;
                    border: 1px solid #2B2E37;
                    border-radius: 4px;
                    padding: 1px 6px;
                }}
                QPushButton:hover {{
                    color: {COLOR_TEXT_PRIMARY};
                    border-color: {COLOR_ORANGE};
                }}
            """)

        btn_minus5.clicked.connect(lambda: self._adjust_timer(-300))
        btn_plus5.clicked.connect(lambda: self._adjust_timer(300))
        btn_test_chime.clicked.connect(self._trigger_completion_effects)

        adjust_layout.addWidget(btn_minus5)
        adjust_layout.addWidget(btn_plus5)
        adjust_layout.addStretch(1)
        adjust_layout.addWidget(btn_test_chime)
        timer_layout.addLayout(adjust_layout)

        content_layout.addWidget(timer_panel, stretch=4)
        main_layout.addLayout(content_layout)

        # ----------------------------------------------------------------------
        # 4. BOTTOM STATUS BAR (Focus Stats & Always On Top Toggle)
        # ----------------------------------------------------------------------
        status_bar = QFrame()
        status_bar.setFixedHeight(38)
        status_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_CARD};
                border: 1px solid {COLOR_CARD_BORDER};
                border-radius: 8px;
            }}
        """)
        sb_layout = QHBoxLayout(status_bar)
        sb_layout.setContentsMargins(14, 0, 14, 0)
        sb_layout.setSpacing(16)

        # Focus stats label
        self.lbl_focus_time = QLabel("⏱ Сегодня в фокусе: 0 мин")
        self.lbl_focus_time.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 11px; font-weight: bold;")

        self.lbl_session_count = QLabel("🎯 Завершено сессий: 0")
        self.lbl_session_count.setStyleSheet(f"color: {COLOR_MINT}; font-size: 11px; font-weight: bold;")

        self.lbl_status = QLabel("СТАТУС: ГОТОВ К РАБОТЕ")
        self.lbl_status.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 10px; font-weight: bold;")

        sb_layout.addWidget(self.lbl_focus_time)
        sb_layout.addWidget(self.lbl_session_count)
        sb_layout.addWidget(self.lbl_status)
        sb_layout.addStretch(1)

        # Always on top checkbox
        self.chk_on_top = QCheckBox("Всегда поверх других окон")
        self.chk_on_top.setCursor(Qt.CursorShape.PointingHandCursor)
        self.chk_on_top.setStyleSheet(f"""
            QCheckBox {{
                color: {COLOR_TEXT_MUTED};
                font-size: 11px;
                font-weight: bold;
                spacing: 6px;
            }}
            QCheckBox:hover {{
                color: {COLOR_TEXT_PRIMARY};
            }}
            QCheckBox::indicator {{
                width: 14px;
                height: 14px;
                border: 1px solid #3B404E;
                border-radius: 3px;
                background-color: #191B20;
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLOR_ORANGE};
                border-color: {COLOR_ORANGE};
            }}
        """)
        self.chk_on_top.toggled.connect(self._toggle_always_on_top)
        sb_layout.addWidget(self.chk_on_top)

        main_layout.addWidget(status_bar)

    def _setup_shortcuts(self):
        # Space: Start/Pause
        space_action = QAction(self)
        space_action.setShortcut(QKeySequence("Space"))
        space_action.triggered.connect(self._toggle_start_pause)
        self.addAction(space_action)

        # Escape: Reset
        esc_action = QAction(self)
        esc_action.setShortcut(QKeySequence("Escape"))
        esc_action.triggered.connect(self._timer_reset)
        self.addAction(esc_action)

        # M: Mute
        m_action = QAction(self)
        m_action.setShortcut(QKeySequence("M"))
        m_action.triggered.connect(lambda: self.mute_btn.toggle())
        self.addAction(m_action)

    # --------------------------------------------------------------------------
    # AUDIO CONTROLS
    # --------------------------------------------------------------------------
    def _on_channel_toggled(self, channel_id, enabled):
        self.audio_worker.set_channel(channel_id, enabled=enabled)

    def _on_channel_vol_changed(self, channel_id, volume):
        self.audio_worker.set_channel(channel_id, volume=volume)

    def _on_master_vol_changed(self, value):
        self.audio_worker.set_master_volume(value / 100.0)

    def _toggle_mute(self, is_muted):
        self.audio_worker.set_muted(is_muted)
        self.mute_btn.setText("🔇 МЬЮТ" if is_muted else "🔊 ЗВУК")

    def _apply_mixer_preset(self, preset):
        presets = {
            "rain":  {"rain": (True, 0.70), "fire": (False, 0.5), "vinyl": (True, 0.35), "coffee": (False, 0.4)},
            "fire":  {"rain": (False, 0.6), "fire": (True, 0.75), "vinyl": (True, 0.40), "coffee": (False, 0.4)},
            "all":   {"rain": (True, 0.60), "fire": (True, 0.55), "vinyl": (True, 0.50), "coffee": (True, 0.45)},
            "none":  {"rain": (False, 0.6), "fire": (False, 0.6), "vinyl": (False, 0.55), "coffee": (False, 0.5)},
        }
        cfg = presets.get(preset, {})
        for cid, (state, vol) in cfg.items():
            if cid in self.cards:
                self.cards[cid].setChannelState(state, vol)
                self.audio_worker.set_channel(cid, enabled=state, volume=vol)

    # --------------------------------------------------------------------------
    # TIMER CONTROLS & LOGIC
    # --------------------------------------------------------------------------
    def _set_timer_preset(self, minutes, mode):
        self.is_timer_running = False
        self.current_mode = mode
        self.timer_seconds_remaining = minutes * 60
        self.timer_preset_seconds = minutes * 60

        mode_name = "СЕАНС: ФОКУС" if mode == "focus" else "ПЕРЕРЫВ: ОТДЫХ"
        self.digital_clock.setMode(f"{mode_name} ({minutes} МИН)")
        self.digital_clock.setTime(self.timer_seconds_remaining, self.timer_preset_seconds)
        self.digital_clock.setRunning(False)

        self.btn_start.setText("▶ СТАРТ")
        self.lbl_status.setText(f"СТАТУС: {mode_name.upper()}")

    def _timer_start(self):
        if not self.is_timer_running and self.timer_seconds_remaining > 0:
            self.is_timer_running = True
            self.digital_clock.setRunning(True)
            self.btn_start.setText("▶ В РАБОТЕ")
            self.lbl_status.setText("СТАТУС: ТАЙМЕР АКТИВЕН")

    def _timer_pause(self):
        if self.is_timer_running:
            self.is_timer_running = False
            self.digital_clock.setRunning(False)
            self.btn_start.setText("▶ ПРОДОЛЖИТЬ")
            self.lbl_status.setText("СТАТУС: ПАУЗА")

    def _toggle_start_pause(self):
        if self.is_timer_running:
            self._timer_pause()
        else:
            self._timer_start()

    def _timer_reset(self):
        self.is_timer_running = False
        self.timer_seconds_remaining = self.timer_preset_seconds
        self.digital_clock.setRunning(False)
        self.digital_clock.setTime(self.timer_seconds_remaining, self.timer_preset_seconds)
        self.btn_start.setText("▶ СТАРТ")
        self.lbl_status.setText("СТАТУС: СБРОШЕН")

    def _adjust_timer(self, delta_seconds):
        self.timer_seconds_remaining = max(60, self.timer_seconds_remaining + delta_seconds)
        self.timer_preset_seconds = max(self.timer_seconds_remaining, self.timer_preset_seconds)
        self.digital_clock.setTime(self.timer_seconds_remaining, self.timer_preset_seconds)

    def _timer_tick(self):
        """Called every 1 second"""
        if self.is_timer_running:
            if self.timer_seconds_remaining > 0:
                self.timer_seconds_remaining -= 1
                
                # Accumulate focus stats if in focus mode
                if self.current_mode == "focus":
                    self.total_focus_seconds += 1
                    self._update_stats_display()

                self.digital_clock.setTime(self.timer_seconds_remaining)
                self.digital_clock.setColonBlink(self.timer_seconds_remaining % 2 == 0)

                # Timer Complete!
                if self.timer_seconds_remaining == 0:
                    self._on_timer_complete()
            else:
                self.is_timer_running = False
                self.digital_clock.setRunning(False)

    def _on_timer_complete(self):
        self.is_timer_running = False
        self.digital_clock.setRunning(False)
        self.btn_start.setText("▶ СТАРТ")

        if self.current_mode == "focus":
            self.completed_sessions += 1
            self.lbl_status.setText("СТАТУС: СЕССИЯ ЗАВЕРШЕНА! ВРЕМЯ ОТДОХНУТЬ")
        else:
            self.lbl_status.setText("СТАТУС: ОТДЫХ ЗАВЕРШЕН! ГОТОВ К ФОКУСУ")

        self._update_stats_display()
        self._trigger_completion_effects()

    def _update_stats_display(self):
        mins = self.total_focus_seconds // 60
        hours = mins // 60
        rem_mins = mins % 60
        if hours > 0:
            time_str = f"{hours} ч {rem_mins} мин"
        else:
            time_str = f"{mins} мин"

        self.lbl_focus_time.setText(f"⏱ Сегодня в фокусе: {time_str}")
        self.lbl_session_count.setText(f"🎯 Завершено сессий: {self.completed_sessions}")

    # --------------------------------------------------------------------------
    # COMPLETION VISUAL FLASH & CHIME ALARM
    # --------------------------------------------------------------------------
    def _trigger_completion_effects(self):
        """Triggers audio chime and glowing border pulse animation"""
        # Play procedure bell chime
        self.audio_worker.trigger_chime()

        # Start glowing screen border animation
        self.is_flashing = True
        self.flash_progress = 0.0
        self.flash_timer.start(25)  # 40 FPS

    def _update_border_flash(self):
        self.flash_progress += 0.02
        if self.flash_progress >= 1.0:
            self.is_flashing = False
            self.flash_timer.stop()
            self.update()
        else:
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        
        # Draw glowing orange border flash when active
        if self.is_flashing:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Pulsing intensity (3 smooth pulses with exponential decay)
            pulse = math.sin(self.flash_progress * math.pi * 6.0)
            alpha_mult = max(0.0, pulse) * (1.0 - self.flash_progress)
            
            if alpha_mult > 0.01:
                rect = QRectF(self.rect())
                layers = 12
                for i in range(layers):
                    layer_alpha = int(alpha_mult * (layers - i) / float(layers) * 190)
                    pen = QPen(QColor(255, 107, 53, layer_alpha), 2.0)
                    painter.setPen(pen)
                    painter.setBrush(Qt.BrushStyle.NoBrush)
                    inset = i * 1.5
                    painter.drawRoundedRect(rect.adjusted(inset, inset, -inset, -inset), 6, 6)

    # --------------------------------------------------------------------------
    # WINDOW CONTROLS & CLEANUP
    # --------------------------------------------------------------------------
    def _toggle_always_on_top(self, checked):
        pos = self.pos()
        size = self.size()
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, checked)
        self.show()
        self.move(pos)
        self.resize(size)

    def closeEvent(self, event):
        """Clean shutdown of audio worker thread and timers"""
        self.second_timer.stop()
        self.flash_timer.stop()
        self.visualizer.timer.stop()
        self.audio_worker.stop()
        event.accept()


# ==============================================================================
# APPLICATION ENTRY POINT
# ==============================================================================
def main():
    # Enable High-DPI scaling
    app = QApplication(sys.argv)
    app.setApplicationName("LoFiFocusCompanion")

    # Set application-wide dark palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(COLOR_BG))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(COLOR_TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Base, QColor(COLOR_CARD))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(COLOR_LCD_BG))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(COLOR_CARD))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(COLOR_TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Text, QColor(COLOR_TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Button, QColor(COLOR_CARD))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(COLOR_TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(COLOR_ORANGE))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
    app.setPalette(palette)

    window = LoFiCompanionWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
