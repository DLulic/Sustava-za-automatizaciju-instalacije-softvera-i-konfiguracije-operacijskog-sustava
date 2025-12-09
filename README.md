# System for Automating Software Installation and OS Configuration

## About

This project is a Python-based application designed to automate the setup process of a new Windows machine. The system enables software installation, information gathering, Windows settings configuration, Group Policy management, and bloatware removal, all managed through a centralized MySQL database.

## Features

-   **Graphical User Interface (GUI):** A modern interface built using `ttkbootstrap` (tkinter).
-   **MySQL Integration:** Fetch configurations, software lists, and settings from a remote database.
-   **Automation:**
    -   Software installation (using Winget and custom scripts).
    -   Software uninstallation (bloatware removal).
    -   Group Policy Object configuration.
    -   Windows settings application.
    -   Python library/dependency installation.
-   **Initial Configuration:** Set computer name and input Windows product key.
-   **Security:** Requires administrative privileges to operate.

## Prerequisites

-   Windows 10 or Windows 11 operating system.
-   Internet connection (for downloading packages and database access).
-   Access to a MySQL database with the appropriate schema.

## Installation & Usage

The project includes a `Start.bat` script that automatically handles prerequisites (installs Python and necessary libraries) and launches the application.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/DLulic/Sustava-za-automatizaciju-instalacije-softvera-i-konfiguracije-operacijskog-sustava.git
    cd Sustava-za-automatizaciju-instalacije-softvera-i-konfiguracije-operacijskog-sustava
    ```

2.  **Run the application:**
    Simply run the `Start.bat` file as an administrator (the script will request privileges if they are not already granted).

    > **Note:** `Start.bat` will automatically install Python 3.13 (via Winget) and the required Python packages (`ttkbootstrap`, `mysql-connector-python`) before launching the app.

3.  **Database Configuration:**
    On the first run, the application will prompt you for MySQL connection details (Host, Port, User, Password, Database).

## Project Structure

-   `main.py`: The main entry point of the application.
-   `Start.bat`: Script for dependency installation and launching.
-   `Display/`: Contains UI components and pages (e.g., `MainPage.py`, `mysqlPage.py`, `InstallProgramsPage.py`).
-   `Controller/`: Logic for database communication and configuration management.
-   `Functions/`: Implementation of core functionalities (installation, scripts).
-   `Storage/`: Directory for local data storage.
-   `utils/`: Helper scripts (e.g., logging).

## Technologies

-   **Python 3.13**
-   **Tkinter & ttkbootstrap**: For the graphical user interface.
-   **MySQL Connector**: For database communication.
-   **Winget**: Windows Package Manager for software installation.
