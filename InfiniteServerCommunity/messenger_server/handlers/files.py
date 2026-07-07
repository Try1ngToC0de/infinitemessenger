from flask import request, jsonify
import requests
import uuid
import datetime
import os
from core.storage import load_chat
from config.settings import FILES_DIR

#######################################################
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
# TODO: надо заменить яндекс клауд на папку FILES_DIR #
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
#######################################################

# ========== КОНФИГУРАЦИЯ ==========
STORAGE_URL = 'https://storage.yandexcloud.net/infinitemessenger/'
FILESTORAGE_PATH = 'filestorage/'

def generate_file_id():
    """Генерирует уникальный ID для файла"""
    return str(uuid.uuid4())

def upload_file(login):
    """
    Загрузка файла в Yandex Cloud (защищённый эндпоинт).
    login — текущий пользователь (из JWT).
    Ожидает multipart/form-data с полем 'file'.
    """
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "Empty filename"}), 400
        
        chat_id = request.form.get('chat_id')
        if not chat_id:
            return jsonify({"error": "chat_id required"}), 400
        
        chat_data = load_chat(chat_id)
        if not chat_data:
            return jsonify({"error": "Chat not found"}), 404
        
        if login not in chat_data.get('participants', []):
            return jsonify({"error": "User is not a participant of this chat"}), 403
        
        file_id = generate_file_id()
        original_filename = file.filename or 'file'
        
        extension = 'bin'
        if '.' in original_filename:
            extension = original_filename.split('.')[-1] or 'bin'
        
        storage_filename = f"{file_id}.{extension}"
        storage_url = f"{STORAGE_URL}{FILESTORAGE_PATH}{storage_filename}"
        
        file_content = file.read()
        # TODO: надо заменить яндекс клауд на папку FILES_DIR
        response = requests.put(
            storage_url,
            data=file_content,
            headers={
                'Content-Type': file.content_type or 'application/octet-stream'
            }
        )
        
        if response.status_code != 200:
            return jsonify({"error": f"Upload failed: {response.status_code}"}), 500
        
        file_info = {
            "id": file_id,
            "name": original_filename,
            "url": storage_url,
            "type": file.content_type or 'application/octet-stream',
            "size": len(file_content),
            "uploaded_by": login,
            "uploaded_at": datetime.datetime.now().isoformat()
        }
        
        return jsonify({
            "success": True,
            "file": file_info
        }), 201
        
    except Exception as e:
        return jsonify({"error": f"Upload error: {str(e)}"}), 500

def download_file(file_id):
    """
    Скачивание файла из Yandex Cloud (защищённый эндпоинт).
    """
    try:
        from core.storage import CHATS_DIR
        
        found_file = None
        
        for filename in os.listdir(CHATS_DIR):
            if filename.endswith('.json'):
                chat_data = load_chat(filename[:-5])
                if not chat_data:
                    continue
                
                for message in chat_data.get('messages', []):
                    file_info = message.get('file')
                    if file_info and file_info.get('id') == file_id:
                        found_file = file_info
                        break
                
                if found_file:
                    break
        
        if not found_file:
            return jsonify({"error": "File not found"}), 404
        
        response = requests.get(found_file['url'])
        if response.status_code != 200:
            return jsonify({"error": "File download failed"}), 500
        
        # Создаём ответ с файлом
        from flask import Response
        return Response(
            response.content,
            status=200,
            headers={
                'Content-Type': found_file.get('type', 'application/octet-stream'),
                'Content-Disposition': f'attachment; filename="{found_file.get("name", "file")}"'
            }
        )
        
    except Exception as e:
        return jsonify({"error": f"Download error: {str(e)}"}), 500

def get_file_info(file_id):
    """
    Получение информации о файле (без скачивания).
    """
    try:
        from core.storage import CHATS_DIR
        
        for filename in os.listdir(CHATS_DIR):
            if filename.endswith('.json'):
                chat_data = load_chat(filename[:-5])
                if not chat_data:
                    continue
                
                for message in chat_data.get('messages', []):
                    file_info = message.get('file')
                    if file_info and file_info.get('id') == file_id:
                        return jsonify({
                            "success": True,
                            "file": file_info
                        }), 200
        
        return jsonify({"error": "File not found"}), 404
        
    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"}), 500
