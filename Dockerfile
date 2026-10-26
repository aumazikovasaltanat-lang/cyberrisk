FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libegl1 \
    libglib2.0-0 \
    libfontconfig1 \
    libfreetype6 \
    libxrender1 \
    libxext6 \
    libxkbcommon-x11-0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-xfixes0 \
    libxcb-cursor0 \
    libdbus-1-3 \
    libpulse0 \
    libkrb5-3 \
    libasound2 \
    alsa-utils \
    fonts-dejavu-core \
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    gstreamer1.0-plugins-good \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "coffee_kds.py"]
