# DriveValue AI: Egyptian Car Value Analyzer

## Overview

An application designed to estimate the fair market value, investment potential, and future depreciation of cars in the Egyptian market. Leveraging machine learning models, it provides users with comprehensive insights, including a Vehicle Retention Score (VRS), investment grade, fair value estimates, and future value forecasts.

https://github.com/user-attachments/assets/61571aa9-6c5b-46df-b3a3-9e5413d3ff68

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
- **Value Retention Score (VRS)**: Evaluates investment potential by calculating the annual geometric price retention of specific models. The base retention rate is computed cross-sectionally across different age bands using the formula:
  
  $$\text{Annual Retention (\%)} = \left( \frac{\text{Price}_{\text{old}}}{\text{Price}_{\text{young}}} \right)^{\frac{1}{\text{Age}_{\text{diff}}}} \times 100$$
  
  This percentage is then normalized to a 0–100 scale (using 85% and 97% retention as the low and high market anchors) and translated into grades ranging from "A+ Elite Retention" down to "D High Depreciation Risk".
- **Future Value Estimation**: Predicts the depreciation curve and estimated resale value of a vehicle over a designated future ownership period.
- **User-Friendly Interface**: A sleek, modern dark-mode design with intuitive input fields and clear result visualization.
- **Responsive Design**: Optimized for seamless experience across desktop and mobile devices.
- **Robust Backend**: Built with Flask, featuring model loading, prediction logic, and comprehensive error handling for reliable performance.

## Model Performance & Methodology

The core valuation engine utilizes a **Random Forest Regressor** (700 estimators) trained on over 10,000 cleaned listings, predicting the logarithmic price `log(price)`. Based on a 10% hold-out test set, the model achieves the following metrics:
- **Mean Absolute Error (MAE):** ~315,975 EGP
- **MAPE (Average % Error):** 20.86%
- **R² Score (Variance Explained):** 0.6656
- **Confidence Intervals:** The engine utilizes the spread across individual decision trees (10th to 90th percentiles) to establish a low/high pricing band, achieving an **84.97% interval coverage rate** on unseen data.
*Note: High market volatility and the nominal EGP devaluation heavily influence the nominal price predictions and VRS scoring, meaning a high score reflects resistance to both depreciation and inflation.*

## Technologies Used

- **Frontend**: HTML, CSS, JavaScript (for dynamic UI and API interaction), Font Awesome (icons), Google Fonts (Inter, Rajdhani).
- **Backend**: Python, Flask (web framework), joblib (for model persistence).
- **Machine Learning**: Random Forest.
