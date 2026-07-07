import subprocess
import time
import os
import sys
import threading
import argparse
import signal

# ========== ОПРЕДЕЛЕНИЕ ПАПКИ ПРОЕКТА ==========
def get_project_root():
    """Возвращает папку, где находится InfiniteServer"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

PROJECT_ROOT = get_project_root()

# ========== ФЛАГ ДЛЯ ЗАВЕРШЕНИЯ ==========
running = True

def signal_handler(sig, frame):
    global running
    running = False
    print("\n👋 Завершение работы...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# ========== ЗАПУСК ТУННЕЛЯ ==========
def run_tunnel():
    print("🌐 Запускаем CloudPub туннель...")
    process = subprocess.Popen(
        ["python", "windows_tunnel.py"],
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    if process.stdout is not None:
        for line in process.stdout:
            if not running:
                break
            print(f"[TUNNEL] {line.strip()}")
    else:
        print("[TUNNEL] ❌ Не удалось получить вывод процесса")
    
    return process

# ========== ЗАПУСК СЕРВЕРА ==========
def run_server():
    print("🚀 Запускаем Flask сервер...")
    process = subprocess.Popen(
        ["python", "messenger_server/main.py"],
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    if process.stdout is not None:
        for line in process.stdout:
            if not running:
                break
            print(f"[SERVER] {line.strip()}")
    else:
        print("[SERVER] ❌ Не удалось получить вывод процесса")
    
    return process

# ========== ОСТАЛЬНОЙ КОД БЕЗ ИЗМЕНЕНИЙ ==========
def run_gui():
    print("🖥️ Запуск Infinite Messenger с графическим интерфейсом...")
    print("⚠️ Графический интерфейс ещё не реализован. Запускаем в консольном режиме.")
    run_server()

def parse_args():
    parser = argparse.ArgumentParser(description="Infinite Messenger — утилита запуска")
    parser.add_argument('--gui', action='store_true', help='Запустить Infinite Messenger с GUI')
    parser.add_argument('--stop', action='store_true', help='Остановить все процессы')
    return parser.parse_args()

def stop_all():
    print("🛑 Останавливаем Infinite Messenger...")
    try:
        import psutil
    except ImportError:
        print("⚠️ Установи psutil: pip install psutil")
        return
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline'] or [])
            if 'windows_tunnel.py' in cmdline or 'main.py' in cmdline:
                print(f"⏹️ Останавливаем процесс {proc.info['pid']}: {proc.info['name']}")
                proc.terminate()
                proc.wait(timeout=3)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
            pass
    print("✅ Все процессы остановлены.")

if __name__ == "__main__":
    args = parse_args()
    
    if args.stop:
        stop_all()
        sys.exit(0)
    
    if args.gui:
        run_gui()
        sys.exit(0)
    
    print("=" * 50)
    print("🔄 Запуск Infinite Messenger...")
    print("=" * 50)
    
    tunnel_thread = threading.Thread(target=run_tunnel, daemon=True)
    tunnel_thread.start()
    
    print("⏳ Ждём 5 секунд, пока туннель поднимется...")
    time.sleep(5)
    
    try:
        run_server()
    except KeyboardInterrupt:
        print("\n👋 Завершение работы...")
        sys.exit(0)
