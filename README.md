# cyberriskexe

# Docker және WSLg арқылы PyQt6 десктоптық қосымшаларын іске қосу

Бұл жобада Python (PyQt6) фреймворкімен жасалған екі графикалық дербес десктоптық қосымша ұсынылған: Smart Coffee POS & KDS және Lo-Fi Focus & Audio Companion. Екі бағдарлама да оқшауланған Docker контейнеріне жинақталған және Windows жүйесінде WSLg графигі мен PulseAudio дыбыстық жүйесі арқылы іске қосылады.

---

## 📌 Жобаның мазмұны

1. Smart Coffee POS & KDS (coffee_kds.py) — заманауи Drinkit кофеханаларының стиліндегі ақылды кофе кассасы мен бариста экраны.
   * Сусын түрлерін таңдау және толық баптау (көлемі: S/M/L, сүт түрлері: сиыр, сұлы, кокос, бадам, сироптар мөлшері).
   * Бағаны теңгемен (₸) автоматты түрде қайта есептеу.
   * Баристаның дисплейіне тапсырыстарды реттік нөмірмен жіберу және дайындалу уақытын таймермен қадағалау.

2. Lo-Fi Focus & Audio Companion (lofi_companion.py) — жұмыс немесе оқу барысында зейінді жинақтауға арналған атмосфералық медиа-станция.
   * 4 арналы процедуралық дыбыс микшері (жаңбыр дыбысы, от жалыны, винил сытыры, кофехана гуілі).
   * Нақты уақытта динамикалық түрде ырғалатын эквалайзер мен аудио-визуализатор.
   * Жұмыс пен тынығуды реттейтін кіріктірілген Pomodoro фокус-таймері.

---

## 🛠 Жүйелік талаптар

* ОЖ: Windows 10 (19044+ құрастырылымы) немесе Windows 11 (орнатылған WSLg қолдауымен).
* Docker Desktop: Windows-та орнатылған және баптауларында WSL 2 интеграциясы қосылған (Settings -> Resources -> WSL Integration).
* WSL 2: Ubuntu немесе кез келген басқа Debian негізіндегі дистрибутив.

---

## 🚀 Орнату және іске қосу нұсқаулығы

1-қадам. Репозиторийді клондау және папкаға өту:
git clone <РЕПОЗИТОРИЙ_СІЛТЕМЕСІ>
cd project01

2-қадам. Docker-бейнені (image) жинау:
docker build -t desktop-apps .

(Бұл қадам интернет жылдамдығына байланысты 1–2 минут алады және бір-ақ рет орындалады).

---

## 🖥 Қосымшаларды экранға шығару

### 1. Ақылды кофе кассасын іске қосу (coffee_kds.py)

```bash
docker run -it --rm \
    --user $(id -u):$(id -g) \
    -e DISPLAY=\$DISPLAY \
    -e WAYLAND_DISPLAY=\$WAYLAND_DISPLAY \
    -e QT_X11_NO_MITSHM=1 \
    -e QT_QPA_PLATFORM=xcb \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v /mnt/wslg:/mnt/wslg \
    desktop-apps python coffee_kds.py
```

### 2. Lo-Fi фокус-станциясын дыбыспен іске қосу (lofi_companion.py)

```bash
docker run -it --rm \
    --user $(id -u):$(id -g) \
    -e DISPLAY=\$DISPLAY \
    -e WAYLAND_DISPLAY=\$WAYLAND_DISPLAY \
    -e QT_X11_NO_MITSHM=1 \
    -e QT_QPA_PLATFORM=xcb \
    -e PULSE_SERVER=unix:/mnt/wslg/PulseServer \
    -e PULSE_COOKIE=/mnt/wslg/PulseCookie \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v /mnt/wslg:/mnt/wslg \
    --device /dev/snd \
    --group-add audio \
    desktop-apps python lofi_companion.py
```

---

## 📂 Жоба құрылымы

project01/
├── Dockerfile           # Графикалық (X11/EGL) және дыбыстық (PulseAudio) пакеттері бар образ құрылымы
├── requirements.txt     # Python кітапханалары (PyQt6, numpy, psutil, pygame)
├── coffee_kds.py        # Кофе кассасы мен бариста экранының коды
├── lofi_companion.py    # Lo-Fi станциясы мен визуализатордың коды
├── .gitignore           # Уақытша файлдар мен кэшті жасыру ережелері
└── README.md            # Толық құжаттама мен іске қосу нұсқаулығы

---

## ⚙️ Техникалық ерекшеліктер

* Оқшаулану: Негізгі жүйеге (Windows-қа) Python немесе PyQt6 орнатудың қажеті жоқ. Барлық тәуелділіктер контейнер ішінде ғана орындалады.
* Дыбысты жеткізу: PULSE_SERVER=unix:/mnt/wslg/PulseServer және PULSE_COOKIE=/mnt/wslg/PulseCookie параметрлері арқылы контейнер дыбыстық сигналдарды Windows-тың ішкі WSLg жүйесіне еш кідіріссіз жеткізеді.
* Тұрақты графика: QT_X11_NO_MITSHM=1 және QT_QPA_PLATFORM=xcb баптаулары контейнер мен Windows мониторы арасындағы ортақ жад қателерін болдырмай, тұрақты тегіс рендерді қамтамасыз етеді.
* Жүйені таза ұстау: --rm жалаушасы терезені жапқан бойда контейнерді жедел жадтан автоматты түрде өшіріп, жүйе ресурстарын үнемдейді.
