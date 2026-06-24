# DriveValue AI: Egyptian Car Value Analyzer

## Overview

An application designed to estimate the fair market value, investment potential, and future depreciation of cars in the Egyptian market. Leveraging machine learning models, it provides users with comprehensive insights, including a Vehicle Retention Score (VRS), investment grade, fair value estimates, and future value forecasts.

## Project Architecture

The repository consists of five main components, covering the entire lifecycle from data ingestion to model deployment:

- **`scraper.py`**: A robust web scraper utilizing `requests` and `BeautifulSoup` with built-in retry mechanisms to extract car listings from the Hatla2ee marketplace. It collects critical features such as Make, Model, Price, Mileage, transmission type, and location.
- **`EDA.ipynb`**: A comprehensive Jupyter Notebook dedicated to data cleaning and Exploratory Data Analysis. It visualizes market trends, establishes brand price tiers, and prepares the scraped dataset (`hatla2ee_scraped_data_cleaned.csv`) for modeling.
- **`valuation_engine.ipynb`**: The core machine learning pipeline. It trains a `RandomForestRegressor` on the cleaned data, computes the Value Retention Score (VRS) based on cross-sectional market data, and exports the finalized models and categorical encoders via `joblib` into a `car_model.pkl` artifact.
- **`valuation_logic.py`**: The business logic module. It contains functions to generate accurate price predictions, classify investment ratings, map future value estimates, and construct human-readable explanations (in both English and Arabic) based on the model's inferences.
- **`app.py`**: A Flask web application serving as the interface for the valuation engine. It loads the exported `car_model.pkl` artifact and exposes REST endpoints (e.g., returning JSON responses with predictions, investment scores, and bilingual commentary).

## Features

- **Fair Value Estimation**: Predicts a car's market value based on various parameters.
- **Investment Rating**: Provides an investment grade (e.g., A+, B, C) and a detailed explanation of the car's retention characteristics.
- **Value Retention Score (VRS)**: Calculates the annual geometric price retention of models to evaluate investment potential, assigning grades from "A+ Elite Retention" down to "D High Depreciation Risk".
- **Future Value Estimation**: Predicts the depreciation curve and estimated resale value of a vehicle over a designated future ownership period.
- **User-Friendly Interface**: A sleek, modern dark-mode design with intuitive input fields and clear result visualization.
- **Responsive Design**: Optimized for seamless experience across desktop and mobile devices.
- **Robust Backend**: Built with Flask, featuring model loading, prediction logic, and comprehensive error handling for reliable performance.

## Technologies Used

- **Frontend**: HTML, CSS, JavaScript (for dynamic UI and API interaction), Font Awesome (icons), Google Fonts (Inter, Rajdhani).
- **Backend**: Python, Flask (web framework), joblib (for model persistence).
- **Machine Learning**: Random Forest.
