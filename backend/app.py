# Import necessary libraries
import numpy as np
import pandas as pd                                 # For data manipulation
import joblib                                       # For loading the serialized model
from flask import Flask, request, jsonify           # For creating the Flask API

# Initialize the Flask application
superkart_api = Flask("SuperKart Sales Predictor")

# Load the trained machine learning pipeline (preprocessing + model)
model = joblib.load("superkart_model.joblib")

# Features expected by the model, in the order used during training
FEATURES = [
    "Product_Weight",
    "Product_Sugar_Content",
    "Product_Allocated_Area",
    "Product_MRP",
    "Store_Size",
    "Store_Location_City_Type",
    "Store_Type",
    "Product_Id_char",
    "Store_Age_Years",
    "Product_Type_Category",
]


# Health-check endpoint (GET request)
@superkart_api.get('/')
def home():
    """
    Handles GET requests to the root URL and returns a welcome message,
    confirming that the API is running.
    """
    return "Welcome to the SuperKart Sales Prediction API!"


# Endpoint for online (single record) prediction
@superkart_api.post('/v1/predict')
def predict_sales():
    """
    Handles POST requests to '/v1/predict'.
    Expects a JSON payload with the product and store attributes and returns
    the predicted total sales for that product-store combination.
    """
    # Read the JSON payload sent by the client
    product_data = request.get_json()

    # Extract the expected features from the payload
    sample = {
        'Product_Weight': product_data['Product_Weight'],
        'Product_Sugar_Content': product_data['Product_Sugar_Content'],
        'Product_Allocated_Area': product_data['Product_Allocated_Area'],
        'Product_MRP': product_data['Product_MRP'],
        'Store_Size': product_data['Store_Size'],
        'Store_Location_City_Type': product_data['Store_Location_City_Type'],
        'Store_Type': product_data['Store_Type'],
        'Product_Id_char': product_data['Product_Id_char'],
        'Store_Age_Years': product_data['Store_Age_Years'],
        'Product_Type_Category': product_data['Product_Type_Category'],
    }

    # Convert the extracted data into a single-row DataFrame
    input_data = pd.DataFrame([sample])

    # Generate the prediction
    prediction = model.predict(input_data)[0]

    # Cast the NumPy float to a native Python float, since jsonify cannot
    # serialize NumPy data types
    prediction = round(float(prediction), 2)

    return jsonify({'Predicted Sales (in dollars)': prediction})


# Endpoint for batch prediction
@superkart_api.post('/v1/predictbatch')
def predict_sales_batch():
    """
    Handles POST requests to '/v1/predictbatch'.
    Expects a CSV file upload containing one row per product-store combination
    and returns the predicted sales for every row as a JSON response.
    """
    # Read the uploaded CSV file into a DataFrame
    file = request.files['file']
    input_data = pd.read_csv(file)

    # Keep only the columns the model expects
    input_data = input_data[FEATURES]

    # Generate predictions for all rows
    predictions = model.predict(input_data)

    # Round and convert to native Python floats for JSON serialization
    predictions = [round(float(p), 2) for p in predictions]

    # Return the predictions keyed by row index
    output = pd.Series(predictions, index=input_data.index).to_dict()

    return jsonify(output)


# Local execution entry point (inside Docker, gunicorn starts the app instead)
if __name__ == '__main__':
    superkart_api.run(host='0.0.0.0', port=7860, debug=True)
