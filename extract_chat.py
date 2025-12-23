import json
import os
import re
from datetime import datetime
from typing import List, Dict, Any
from bs4 import BeautifulSoup

def parse_html_file(file_path: str) -> List[Dict[str, Any]]:
    """Парсит HTML файл с перепиской и возвращает список сообщений."""
    messages = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    # Находим все сообщения
    message_elements = soup.find_all(class_='message')
    
    for msg in message_elements:
        # Пропускаем служебные сообщения (даты)
        if 'service' in msg.get('class', []):
            continue
        
        message_data = {}
        
        # Извлекаем информацию об отправителе
        from_name_elem = msg.find(class_='from_name')
        if from_name_elem:
            message_data['from'] = from_name_elem.text.strip()
        
        # Извлекаем время сообщения
        date_elem = msg.find(class_='date')
        if date_elem and 'title' in date_elem.attrs:
            # Преобразуем дату в ISO формат
            date_str = date_elem['title'].strip()
            try:
                dt = datetime.strptime(date_str, '%d.%m.%Y %H:%M:%S')
                message_data['timestamp'] = dt.isoformat()
            except ValueError:
                message_data['timestamp'] = date_str
        
        # Извлекаем текст сообщения
        text_elem = msg.find(class_='text')
        if text_elem:
            message_data['text'] = text_elem.text.strip()
        
        # Извлекаем медиа-информацию (фото, видео, голосовые)
        media = msg.find(class_='media')
        if media:
            media_type = 'unknown'
            title_elem = media.find(class_='title')
            if title_elem:
                media_type = title_elem.text.strip().lower()
            
            status_elem = media.find(class_='status')
            media_info = {'type': media_type}
            
            if status_elem:
                media_info['details'] = status_elem.text.strip()
            
            message_data['media'] = media_info
        
        # Извлекаем ответ на сообщение
        reply_elem = msg.find(class_='reply_to')
        if reply_elem and reply_elem.find('a'):
            reply_link = reply_elem.find('a')
            if 'onclick' in reply_link.attrs:
                # Извлекаем ID сообщения из JavaScript функции
                onclick_text = reply_link['onclick']
                match = re.search(r'GoToMessage\((\d+)\)', onclick_text)
                if match:
                    message_data['reply_to'] = int(match.group(1))
        
        # Извлекаем реакции
        reactions = []
        reaction_spans = msg.find_all(class_='reaction')
        for reaction in reaction_spans:
            emoji_elem = reaction.find(class_='emoji')
            if emoji_elem:
                reactions.append(emoji_elem.text.strip())
        
        if reactions:
            message_data['reactions'] = reactions
        
        # Добавляем только если есть текст или медиа
        if 'text' in message_data or 'media' in message_data:
            messages.append(message_data)
    
    return messages

def main():
    # Находим все файлы messages*.html в текущем каталоге
    html_files = []
    for file in os.listdir('.'):
        if file.startswith('messages') and file.endswith('.html'):
            html_files.append(file)
    
    if not html_files:
        print("Не найдено файлов messages*.html в текущем каталоге")
        return
    
    # Сортируем файлы по номеру (если есть)
    def extract_number(filename):
        match = re.search(r'messages(\d+)', filename)
        return int(match.group(1)) if match else 0
    
    html_files.sort(key=extract_number)
    
    print(f"Найдено {len(html_files)} файлов: {html_files}")
    
    # Парсим все файлы и объединяем сообщения
    all_messages = []
    for file in html_files:
        print(f"Обработка файла: {file}")
        try:
            messages = parse_html_file(file)
            all_messages.extend(messages)
            print(f"  Извлечено {len(messages)} сообщений")
        except Exception as e:
            print(f"  Ошибка при обработке {file}: {e}")
    
    # Сортируем сообщения по времени (если есть timestamp)
    def get_timestamp(msg):
        return msg.get('timestamp', '')
    
    all_messages.sort(key=get_timestamp)
    
    # Сохраняем в компактный JSON
    output_data = {
        'source_files': html_files,
        'total_messages': len(all_messages),
        'messages': all_messages
    }
    
    output_file = 'chat_export.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        # Используем минимальное форматирование для уменьшения размера
        json.dump(output_data, f, ensure_ascii=False, separators=(',', ':'))
    
    # Также сохраняем в более читаемом формате для отладки
    with open('chat_export_pretty.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    # Статистика
    print(f"\nВсего извлечено сообщений: {len(all_messages)}")
    print(f"Сохранено в: {output_file}")
    print(f"Человеко-читаемая версия: chat_export_pretty.json")
    
    # Пример компактного вывода первых 3 сообщений
    print("\nПервые 3 сообщения (компактный формат):")
    for i, msg in enumerate(all_messages[:3], 1):
        timestamp = msg.get('timestamp', 'нет времени')
        sender = msg.get('from', 'неизвестно')
        text_preview = msg.get('text', '')[:50] + '...' if msg.get('text', '') else '(медиа/без текста)'
        print(f"  {i}. [{timestamp}] {sender}: {text_preview}")

if __name__ == '__main__':
    main()