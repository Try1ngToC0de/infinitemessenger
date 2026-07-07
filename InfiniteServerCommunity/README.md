# infinite server

это исходный код сервера infinite. messenger.

проект на ранней стадии. основная задача сейчас — дописать сервер и стабилизировать API.

---

## структура проекта

```
InfiniteServerCommunity
│   .env.example           # шаблон ключей
│   .gitignore
│   jsonbox.py             # загрузка ключей JsonBox
│   README.md
│   start.py               # запуск публичного сервера
│   windows_tunnel.py      # запуск туннеля (Windows, используется в start.py)
│
└───messenger_server
    │   main.py            # запуск Flask сервера
    │   requirements.txt   # зависимости
    │   server.py          # точка входа Flask
    │
    ├───config
    │       settings.py    # конфигурация проекта
    │       __init__.py    # init
    │
    ├───core
    │       crypto.py      # шифрование (AES, PBKDF2)
    │       init_db.py     # инициализация SQLite
    │       jwt_auth.py    # работа с JWT-токенами
    │       models.py      # модели
    │       storage.py     # работа с SQLite
    │       __init__.py    # init
    │
    ├───data               # датабаза + файлы
	│   └───files
    │
    └───handlers
            auth.py        # аутентификация
            chats.py       # работа с чатами
            files.py       # работа с файлами
            invitations.py # работа с приглашениями
            messages.py    # работа с сообщениями
            __init__.py    # init
```

---

## запуск

### windows (infinitestart)

если ты на windows, просто запусти `infinitestart` в терминале из корня проекта:

```bash
infinitestart
```

этот файл запускает туннель и сервер одновременно.

### другие ос (linux / macos)

если ты на linux или macos, используй `start.py`:

```bash
python start.py
```

этот скрипт:
- запускает туннель через `windows_tunnel.py` (адаптируй под свою ос, если нужно)
- через 5 секунд запускает `messenger_server/main.py`

если нужен отдельный запуск туннеля — используй `windows_tunnel.py` или `cloudpub` напрямую.

---

## установка зависимостей

перед запуском установи зависимости:

```bash
pip install -r requirements.txt
```

---

## настройка .env

создай файл `.env` по образцу `.env.example`:

```env
JWT_SECRET_KEY=твой_секретный_ключ
JWT_REFRESH_SECRET=твой_секретный_ключ_для_refresh
JSONBOX_API_KEY=твой_ключ_от_jsonbox
JSONBOX_URL=https://jsonbox.ru/api.php?action=store
```

---

## внешние зависимости

для работы сервера нужны:

- cloudpub (туннель) — скачай `clo.exe` (для Windows, если стоит другая ОС - запускайте туннель по своему,
  на странице cloudpub.ru есть инструкции) с cloudpub.ru, авторизуйся и запусти туннель на порт 7089
- jsonbox.ru — зарегистрируйся и получи токен для `.env`

---

## особенности (текущие)

- E2EE шифрование (RSA) — в разработке
- JWT-аутентификация (access + refresh)
- PBKDF2 хеширование паролей
- SQLite вместо JSON
- загрузка файлов — в разработке

---

## контакты

по вопросам и предложениям: delta8.mail001@gmail.com

---

## лицензия

MIT
