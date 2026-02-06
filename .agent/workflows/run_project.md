---
description: Run the Krishi Sakhi Web Application
---
# Run Project Workflow

This workflow outlines the steps to set up and run the Krishi Sakhi web application (backend and frontend).

## Prerequisites
- **Python 3.9+** installed and added to PATH.
- **Git** (optional, for cloning).

## Workflow Steps

1.  **Environment Setup**
    Ensure you have a virtual environment. If not, create one:
    ```powershell
    python -m venv venv
    ```

2.  **Activate Virtual Environment**
    Powershell:
    ```powershell
    .\venv\Scripts\Activate.ps1
    ```
    
    *Note: If you encounter execution policy errors, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` first.*

3.  **Install Dependencies**
    Install the required packages from `requirements.txt`:
    ```powershell
    pip install -r requirements.txt
    ```

4.  **Environment Configuration**
    Ensure a `.env` file exists in the root directory with the following keys:
    - `FLASK_DEBUG` (optional)
    - `SECRET_KEY`
    - `WEATHER_API_KEY`
    - `GEMINI_API_KEY`

5.  **Run the Application**
    Start the Flask server:
    
    // turbo
    ```powershell
    $env:PYTHONPATH="."
    python backend/app.py
    ```

    The application will be accessible at: [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Quick Start (Turbo)
If you have already set up the environment, you can simply run the "Run the Application" step.
