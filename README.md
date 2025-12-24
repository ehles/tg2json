# Telegram Chat Export Parser

A Python script to convert Telegram Desktop HTML chat exports into structured JSON format.

## Purpose

Converts exported Telegram chat HTML files (`messages*.html`) into a clean JSON format for data analysis, archiving, or processing.

## Installation

1. Install dependencies:
```bash
pip install beautifulsoup4
```

## Usage

1. Export your Telegram chat:
   - Open Telegram Desktop
   - Select chat → Menu (⋮) → Export chat history
   - Choose format: HTML
   - Save files in the script directory

2. Run the script:
```bash
python extract_chat.py
```

## Output

Creates two files:
- `chat_export.json` - compact JSON for processing
- `chat_export_pretty.json` - formatted JSON for reading

## Features

- Parses multiple HTML files automatically
- Extracts: message text, timestamps, senders, media info, replies, reactions
- Sorts messages chronologically
- Provides message statistics

## Example Output JSON

```json
{
  "source_files": ["messages.html", "messages1.html"],
  "total_messages": 3,
  "messages": [
    {
      "from": "John Doe",
      "timestamp": "2024-01-15T10:30:00",
      "text": "Hello everyone!"
    },
    {
      "from": "Jane Smith",
      "timestamp": "2024-01-15T10:32:15",
      "text": "Hi John! How are you?",
      "reply_to": 1,
      "reactions": ["👍"]
    },
    {
      "from": "John Doe",
      "timestamp": "2024-01-15T10:35:00",
      "text": "Sending a photo from my trip",
      "media": {
        "type": "photo",
        "details": "Photo (1.2 MB)"
      }
    }
  ]
}
```
