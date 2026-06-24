from flask import Flask, render_template, request, jsonify
import joblib
import valuation_logic

app = Flask(__name__)

try:
    saved = joblib.load("./exported/car_model.pkl")

    valuation_logic.rf = saved["rf"]
    valuation_logic.encoder1 = saved["encoder1"]
    valuation_logic.encoder2 = saved["encoder2"]

    valuation_logic.cat_cols1 = saved["cat_cols1"]
    valuation_logic.cat_cols2 = saved["cat_cols2"]

    valuation_logic.model_counts = saved["model_counts"]
    valuation_logic.model_curves = saved["model_curves"]

    valuation_logic.KM_PER_YEAR = saved["KM_PER_YEAR"]

    # Dropdown data
    makes = saved["makes"]
    models = saved["models"]

    fuels = saved["fuels"]
    bodies = saved["bodies"]

    governorates = saved["governorates"]
    transmissions = saved["transmissions"]
    most_reliable_cars = [
        {
            "Make": "Hyundai",
            "Model": "Elantra HD",
            "annual_retention_pct": 96.757433,
            "median_age_diff": 4.0,
            "sample_size": 54,
            "VRS": 97.978606,
        },
        {
            "Make": "Hyundai",
            "Model": "Accent RB",
            "annual_retention_pct": 96.181850,
            "median_age_diff": 8.0,
            "sample_size": 69,
            "VRS": 93.182080,
        },
        {
            "Make": "Chery",
            "Model": "Tiggo 3",
            "annual_retention_pct": 95.650620,
            "median_age_diff": 5.0,
            "sample_size": 78,
            "VRS": 88.755171,
        },
        {
            "Make": "Nissan",
            "Model": "Sentra",
            "annual_retention_pct": 95.367131,
            "median_age_diff": 8.0,
            "sample_size": 89,
            "VRS": 86.392761,
        },
        {
            "Make": "Chery",
            "Model": "Tiggo 7",
            "annual_retention_pct": 95.265493,
            "median_age_diff": 3.0,
            "sample_size": 58,
            "VRS": 85.545776,
        },
        {
            "Make": "Chevrolet",
            "Model": "Optra",
            "annual_retention_pct": 94.909959,
            "median_age_diff": 7.0,
            "sample_size": 195,
            "VRS": 82.582994,
        },
        {
            "Make": "Nissan",
            "Model": "Sunny",
            "annual_retention_pct": 94.722408,
            "median_age_diff": 5.0,
            "sample_size": 255,
            "VRS": 81.020070,
        },
        {
            "Make": "Mercedes",
            "Model": "C 180",
            "annual_retention_pct": 94.053630,
            "median_age_diff": 5.0,
            "sample_size": 194,
            "VRS": 75.446919,
        },
        {
            "Make": "MG",
            "Model": "5",
            "annual_retention_pct": 93.874741,
            "median_age_diff": 4.0,
            "sample_size": 113,
            "VRS": 73.956175,
        },
        {
            "Make": "Kia",
            "Model": "Cerato",
            "annual_retention_pct": 93.755801,
            "median_age_diff": 8.0,
            "sample_size": 144,
            "VRS": 72.965008,
        },
    ]
except FileNotFoundError:
    print(
        "Error: car_model.pkl not found. Please ensure the model file is in the 'exported' directory."
    )
    exit(1)
except Exception as e:
    print(f"Error loading model or assets: {e}")
    exit(1)


class ValidationError(Exception):
    pass


@app.route("/")
def home():

    return render_template(
        "index.html",
        makes=makes,
        models=models,
        fuels=fuels,
        bodies=bodies,
        governorates=governorates,
        transmissions=transmissions,
        most_reliable_cars=most_reliable_cars,
    )


@app.route("/predict", methods=["POST"])
def predict():

    try:
        data = request.get_json()
        if not data:
            raise ValidationError("Invalid JSON data provided.")

        required_fields = [
            "year",
            "mileage",
            "listing_price",
            "make",
            "model",
            "fuel",
            "body",
            "gov",
            "trans",
        ]
        for field in required_fields:
            if field not in data or data[field] is None:
                raise ValidationError(f"Missing required field: {field}")

        try:
            year = int(data["year"])
            if not (1900 <= year <= 2026):  # Assuming current year is 2026
                raise ValidationError("Year must be between 1900 and 2026.")
            age = 2026 - year
        except ValueError:
            raise ValidationError("Year must be a valid integer.")

        try:
            mileage = int(data["mileage"])
            if mileage < 0:
                raise ValidationError("Mileage cannot be negative.")
        except ValueError:
            raise ValidationError("Mileage must be a valid integer.")

        try:
            listing_price = float(data["listing_price"])
            if listing_price < 0:
                raise ValidationError("Listing price cannot be negative.")
        except ValueError:
            raise ValidationError("Listing price must be a valid number.")

        make = data["make"]
        model = data["model"]
        fuel = data["fuel"]
        body = data["body"]
        gov = data["gov"]
        trans = data["trans"]

        if make not in makes:
            raise ValidationError(f"Invalid Make: {make}")
        if model not in models.get(make, []):
            raise ValidationError(f"Invalid Model: {model} for Make: {make}")
        if fuel not in fuels:
            raise ValidationError(f"Invalid Fuel Type: {fuel}")
        if body not in bodies:
            raise ValidationError(f"Invalid Body Type: {body}")
        if gov not in governorates:
            raise ValidationError(f"Invalid Governorate: {gov}")
        if trans not in transmissions:
            raise ValidationError(f"Invalid Transmission: {trans}")

        prediction = valuation_logic.predict_price(
            make=make,
            model=model,
            age=age,
            mileage=mileage,
            fuel=fuel,
            body=body,
            gov=gov,
            trans=trans,
        )

        investment = valuation_logic.investment_rating(
            make=make,
            model=model,
            listing_price=listing_price,
            age=age,
            mileage=mileage,
            fuel=fuel,
            body=body,
            gov=gov,
            trans=trans,
        )

        future = valuation_logic.future_value(
            make=make,
            model=model,
            current_age=age,
            mileage_now=mileage,
            fuel=fuel,
            body=body,
            gov=gov,
            trans=trans,
        )
        explain = valuation_logic.explain(make, model)
        return (
            jsonify(
                {
                    "success": True,
                    "prediction": prediction,
                    "investment": investment,
                    "future_values": future,
                    "explanation": explain,
                }
            ),
            200,
        )

    except ValidationError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        # Log the exception for debugging purposes
        app.logger.error(f"An unexpected error occurred: {e}")
        return (
            jsonify(
                {
                    "success": False,
                    "error": "An internal server error occurred. Please try again later.",
                }
            ),
            500,
        )


if __name__ == "__main__":
    app.run(debug=True)
