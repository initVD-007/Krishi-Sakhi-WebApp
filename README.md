<div align="center">

# 🌿 Krishi Sakshi (कृषि साक्षी)
### SIH 2025 - Smart India Hackathon

**An AI-powered digital companion for farmers, providing instant, context-aware agricultural advice.**

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-lightgrey?style=for-the-badge&logo=flask&logoColor=white)
![Gemini](https://img.shields.io/badge/Google%20Gemini-LLM-orange?style=for-the-badge&logo=google&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-Lite-orange?style=for-the-badge&logo=tensorflow&logoColor=white)
![Three.js](https://img.shields.io/badge/Three.js-3D-black?style=for-the-badge&logo=three.js&logoColor=white)

</div>

---

## 🚩 Problem Statement
**Target:** Smallholder farmers in Kerala  
**The Challenge:** Generic advisories are often ineffective. Farmers lack access to timely, personalized guidance that accounts for their specific **location**, **crop**, **weather**, and **soil conditions**.

## ✨ Our Solution: Krishi Sakshi
**Krishi Sakhi** (meaning "Farming's Friend") is a multi-featured web application acting as a digital companion. It bridges the knowledge gap by combining a fine-tuned **Computer Vision** model for disease diagnosis with a powerful **Large Language Model (LLM)** for complex queries.

> "Empowering farmers with on-demand support, enhancing productivity, and automating first-level support for government agricultural departments."

---

## ✅ Features Implemented

| Feature | Status | Description |
| :--- | :---: | :--- |
| **Farmer & Farm Profiling** | ✅ | Registration with location, land size, crop, soil type, and irrigation method. |
| **Conversational Interface** | ✅ | Text and Voice interaction (Malayalam support) for high accessibility. |
| **Activity Tracking** | ✅ | Auto-save diagnoses and questions to a personal Activity Log. |
| **Personalized Advisory** | ✅ | Real-time location-based weather advice and AI pest warnings. |
| **Reminders & Alerts** | ✅ | Crop calendar with timely nudges for sowing and operations. |
| **Knowledge Engine** | ✅ | Dual-AI: Vision model for disease + LLM (Gemini) for expert advice. |

---

## 🛠️ Technology Stack

### **Backend**
* ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white) **Core Logic**
* ![Flask](https://img.shields.io/badge/-Flask-000000?logo=flask&logoColor=white) **Web Framework**
* ![TensorFlow](https://img.shields.io/badge/-TensorFlow%20Lite-FF6F00?logo=tensorflow&logoColor=white) **AI Model Inference**
* ![Google Gemini](https://img.shields.io/badge/-Google%20Gemini-4285F4?logo=google&logoColor=white) **Large Language Model API**
* ![SQLite](https://img.shields.io/badge/-SQLite-003B57?logo=sqlite&logoColor=white) **Local Database**
* ⏰ **APScheduler** (Background reminder tasks)

### **Frontend**
* ![HTML5](https://img.shields.io/badge/-HTML5-E34F26?logo=html5&logoColor=white) ![CSS3](https://img.shields.io/badge/-CSS3-1572B6?logo=css3&logoColor=white) ![JavaScript](https://img.shields.io/badge/-JavaScript-F7DF1E?logo=javascript&logoColor=black)
* **Three.js** (3D Graphics & Visuals)

---

## 🚀 Getting Started

Follow these steps to set up and run the project on your local machine.

### Prerequisites
* Python 3.8+
* Git

### Installation

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/your-username/Krishi-Sakhi-WebApp.git](https://github.com/your-username/Krishi-Sakhi-WebApp.git)
    cd Krishi-Sakhi-WebApp
    ```

2.  **Create and Activate Virtual Environment**
    ```bash
    # For Windows
    python -m venv venv
    venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Requirements**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure API Keys**
    Open `app.py` and replace the placeholders:
    * Replace `'YOUR_GEMINI_API_KEY'` with your Google Gemini API key.
    * Replace `'YOUR_OPENWEATHERMAP_API_KEY'` with your OpenWeatherMap API key.

5.  **Run the Application**
    ```bash
    python app.py
    ```
    Open your browser and navigate to: `http://127.0.0.1:5000`

---

<div align="center">

Made with ❤️ for **Smart India Hackathon 2025**

</div>
