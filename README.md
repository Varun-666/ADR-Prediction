---
title: ADR Prediction
emoji: 🏨
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# 🏨 ADR Prediction System

> **A Machine Learning powered web application for predicting Hotel Average Daily Rate (ADR) using historical booking information.**

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-Random%20Forest-orange?logo=scikitlearn)
![Docker](https://img.shields.io/badge/Docker-Deployed-blue?logo=docker)
![HuggingFace](https://img.shields.io/badge/HuggingFace-Spaces-yellow)

---

## 📌 Project Overview

The **ADR Prediction System** is a Machine Learning web application designed to estimate the **Average Daily Rate (ADR)** of hotel bookings based on reservation details.

The project combines:

- Machine Learning
- Feature Engineering
- FastAPI
- Docker
- Hugging Face Spaces

to provide a complete end-to-end deployment of an ML model.

Instead of only training a model inside a notebook, this project demonstrates the complete ML lifecycle—from preprocessing and model development to deployment as a production-ready web application.

---

# 🚀 Live Demo

**Hugging Face Space**

👉 **[Add Your Hugging Face Space URL Here]**

---

# 📷 Application Preview

> *(Add screenshots here after deployment)*

### Home Page

```
Screenshot
```

### Prediction Result

```
Screenshot
```

---

# ✨ Features

- Predict Hotel ADR in real time
- Responsive Web Interface
- FastAPI Backend
- Random Forest Regression Model
- Automatic Feature Engineering
- Docker Deployment
- Hosted on Hugging Face Spaces
- Interactive Prediction Form
- Clean User Interface

---

# 🧠 Machine Learning Pipeline

The project follows a complete ML workflow.

```
Dataset
      │
      ▼
Data Cleaning
      │
      ▼
Exploratory Data Analysis
      │
      ▼
Feature Engineering
      │
      ▼
Data Preprocessing
      │
      ▼
Random Forest Regressor
      │
      ▼
Model Serialization
      │
      ▼
FastAPI Backend
      │
      ▼
Docker
      │
      ▼
Hugging Face Spaces
```

---

# 📊 Dataset Features

The model predicts ADR using booking information such as:

- Hotel Type
- Lead Time
- Arrival Date
- Meal Plan
- Country
- Market Segment
- Distribution Channel
- Room Type
- Deposit Type
- Customer Type
- Adults
- Children
- Babies
- Previous Bookings
- Previous Cancellations
- Parking Requirement
- Special Requests
- Booking Changes
- Waiting List Days

---

# ⚙️ Feature Engineering

Additional features are generated before prediction.

| Engineered Feature | Description |
|-------------------|-------------|
| Total Guests | Adults + Children + Babies |
| Total Nights | Weekend + Week Nights |
| Family Booking | Detects family reservations |
| Customer History | Previous bookings + cancellations |
| Weekend Stay | Whether booking includes weekend |
| Long Stay | Stay greater than 5 nights |
| Season | Derived from arrival month |

These engineered features are recreated during inference to ensure consistency with training.

---

# 🧩 Tech Stack

| Category | Technology |
|-----------|------------|
| Language | Python |
| Backend | FastAPI |
| Machine Learning | Scikit-Learn |
| Data Processing | Pandas, NumPy |
| Model Storage | Joblib |
| Frontend | HTML, CSS, JavaScript |
| Deployment | Docker |
| Hosting | Hugging Face Spaces |

---

# 📁 Project Structure

```
ADR-Prediction/
│
├── app/
│   ├── model/
│   │   └── ADR_Prediction_Model.pkl
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   ├── templates/
│   ├── main.py
│   ├── predictor.py
│   └── schemas.py
│
├── Dockerfile
├── requirements.txt
├── README.md
└── .gitignore
```

---

# 🛠 Installation

Clone the repository

```bash
git clone https://github.com/<your-username>/ADR-Prediction.git
```

Move into the project

```bash
cd ADR-Prediction
```

Create virtual environment

```bash
python -m venv venv
```

Activate

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run

```bash
uvicorn app.main:app --reload
```

Open

```
http://127.0.0.1:8000
```

---

# 📈 Model Information

**Algorithm**

- Random Forest Regressor

The model was trained after preprocessing and feature engineering using a Scikit-Learn pipeline.

Prediction output:

```
Average Daily Rate (ADR)
```

---

# 🌍 Deployment

The application is containerized using Docker and deployed on Hugging Face Spaces.

Deployment includes:

- FastAPI backend
- Static frontend
- Local model loading
- Docker runtime
- Git LFS model management

---

# 🔮 Future Improvements

- XGBoost / LightGBM comparison
- Hyperparameter optimization
- Explainable AI using SHAP
- Batch prediction support
- REST API documentation improvements
- Prediction confidence intervals
- User authentication
- Historical prediction logs
- Model monitoring dashboard

---

# 👨‍💻 Author

**Varun**

Artificial Intelligence & Machine Learning Student

---

# ⭐ If you like this project

Consider giving the repository a ⭐ on GitHub.

It helps support future development and makes the project easier for others to discover.

---

# 📜 License

This project is licensed under the MIT License.
