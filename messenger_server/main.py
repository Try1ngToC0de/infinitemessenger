from server import create_app
from config.settings import SERVER_HOST, SERVER_PORT, DEBUG

app = create_app()

if __name__ == '__main__':
    print(f"🚀 Запуск Infinite Messenger API на {SERVER_HOST}:{SERVER_PORT}")
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=DEBUG)