# Automation Hub

Automation Hub is a desktop application built with Python that combines multiple practical tools in one place.  
The goal of this project is to apply real-world automation techniques such as web requests, file handling, scraping, and GUI development.

---

## Features

The application currently includes:

- Quick Search  
  Search directly on Google, YouTube, GitHub, or Google Maps.

- Social Shortcuts  
  One-click access to commonly used websites like LinkedIn, GitHub, Instagram, Facebook, and Twitter.

- Weather Tool  
  Retrieve current weather information for a city.

- Web Downloader  
  Download:
  - Full HTML pages
  - All links from a page
  - Images from a page

- Link Checker  
  Scan a webpage and detect broken links (404 errors).

---

## Project Structure

Automation_hub/
│
├── app.py
├── config.json
├── requirements.txt
├── README.md
│
└── tools/
    ├── base.py
    ├── quick_search.py
    ├── social_shortcuts.py
    ├── weather.py
    ├── web_downloader.py
    └── link_checker.py

---

## Installation

Install dependencies:

python -m pip install -r requirements.txt

---

## How to Run

From the project folder:

python app.py

The graphical interface will open automatically.

---

## Configuration

You can edit config.json to customize:

- Social media shortcuts
- Search engines
- Default download folder

Example:

{
  "socials": {
    "GitHub": "https://github.com",
    "LinkedIn": "https://linkedin.com"
  }
}

---

## Requirements

Python 3.10 or newer recommended  
Internet connection required for web tools

Libraries used:
- requests
- beautifulsoup4
- tkinter (built into Python)

---

## Purpose of the Project

This project was created to practice and demonstrate:

- Modular program design
- GUI development with Tkinter
- HTTP requests and web scraping
- File handling and downloads
- Clean project structure

---

## Author

Lautaro Cuello  
Python Developer
