# Lesson & Finance Tracker

A Python-based desktop application designed to manage course schedules, track student details, and monitor related finances. The application features a graphical user interface (GUI) and utilizes a local SQLite database for lightweight, reliable data storage.

## Features

* **Main Interface (`interface.py`):** The central dashboard for navigating the application.
* **Student/Lesson Details (`details_window.py`):** View, add, and manage specific information about lessons and students.
* **Finance Management (`finance_window.py`):** Track payments, outstanding balances, and overall financial records related to the courses.
* **Local Database (`database.py`):** Seamless data management using a pre-configured SQLite database (`ders_takip_v2.db`).

## Project Structure

```text
├── database.py          # Database connection and query execution methods
├── ders_takip_v2.db     # SQLite database file
├── details_window.py    # GUI module for detailed record viewing
├── finance_window.py    # GUI module for financial tracking
├── interface.py         # Core user interface layouts
└── main.py              # Application entry point