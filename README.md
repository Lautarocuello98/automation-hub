# Automation Hub

Python desktop automation toolkit with GUI, modular tools, logging, and history tracking.

A modular desktop automation application built with Python and Tkinter that integrates multiple practical tools in a single interface.  
The goal of this project is to apply real-world automation techniques such as web requests, file handling, scraping, and GUI development.

---

## Screenshots

### Quick Search  
![Quick Search](screenshots/01_quick_search.png)

### Social Shortcuts  
![Social Shortcuts](screenshots/02_social_shortcuts.png)

### Weather  
![Weather](screenshots/03_weather.png)

### Web Downloader  
![Web Downloader](screenshots/04_web_downloader.png)

### Link Checker  
![Link Checker](screenshots/05_link_checker.png)

### History  
![History](screenshots/06_history.png)

---

## Features

### Quick Search
Search instantly using configured engines such as:
- Google  
- YouTube  
- GitHub  
- Google Maps  

### Social Shortcuts
Open frequently used platforms with one click.  
Configurable through `config.json`.

### Weather Tool
Retrieve current weather information for a city.

### Web Downloader
Download:
- Full HTML pages  
- All links from a page  
- Images from a page  

### Link Checker
Scan a webpage and detect broken links (404 errors).

### History System
The application automatically:
- Stores executed actions
- Saves results and parameters
- Allows deleting individual entries or clearing history

### Keyboard Workflow
- Press **Enter** to execute actions
- Press **Delete** in History to remove selected entries

---

## Technologies Used

- Python  
- Tkinter  
- Requests  
- BeautifulSoup  
- JSON  
- Logging  
- Dataclasses  

---

## Project Architecture

The application is structured to separate responsibilities:

```
GUI Layer (app.py)
        ↓
Tool Interface
        ↓
Individual Tools (tools/)
```

Each tool:
- Implements a common interface  
- Returns standardized results  
- Handles its own logic independently  

This allows:
- Easy extension  
- Clean debugging  
- Scalable design  

---

## Project Structure

```
automation_hub/
│
├── screenshots/          # Application screenshots
│
├── tools/
│   ├── __init__.py
│   ├── base.py
│   ├── errors.py
│   ├── types.py
│   ├── quick_search.py
│   ├── social_shortcuts.py
│   ├── weather.py
│   ├── web_downloader.py
│   └── link_checker.py
│
├── app.py                # Main GUI application
├── config.json           # User configuration
├── history.json          # Execution history
├── app.log               # Runtime logs
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Installation

Install dependencies:

```
python -m pip install -r requirements.txt
```

---

## How to Run

```
python app.py
```

The graphical interface will open automatically.

---

## Configuration

You can edit `config.json` to customize:

- Social media shortcuts  
- Search engines  
- Default download folder  

Example:

```json
{
  "socials": {
    "GitHub": "https://github.com",
    "LinkedIn": "https://linkedin.com"
  }
}
```

---

## Logging

The application generates a log file:

```
app.log
```

Used for:
- Debugging  
- Error tracking  
- Execution records  

---

## Key Concepts Demonstrated

- Modular program design  
- GUI development with Tkinter  
- HTTP requests and web scraping  
- File handling and downloads  
- Configuration management  
- Handling user history and logging  
- Structuring a multi-module Python application  

---

## Author

Lautaro Cuello  
Python Developer  

GitHub:  
https://github.com/Lautarocuello98
