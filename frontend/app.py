import pandas as pd
import requests
import streamlit as st

# Base URL of the Flask backend, resolved through the Docker network
BACKEND_URL = "http://backend:7860"

# Page title
st.title("SuperKart Sales Forecasting")
st.write(
    "Predicts the total sales revenue of a product in a SuperKart outlet, "
    "using the deployed machine learning model."
)

# ---------------------------------------------------------------- #
# Online (single record) prediction
# ---------------------------------------------------------------- #
st.subheader("Online Prediction")

product_weight = st.number_input("Product Weight", min_value=0.0, max_value=50.0, value=12.66, step=0.01)
product_sugar_content = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
product_allocated_area = st.number_input("Product Allocated Area (ratio)", min_value=0.0, max_value=1.0, value=0.027, step=0.001, format="%.3f")
product_mrp = st.number_input("Product MRP", min_value=0.0, max_value=500.0, value=117.08, step=0.01)
store_size = st.selectbox("Store Size", ["Small", "Medium", "High"])
store_location_city_type = st.selectbox("Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"])
store_type = st.selectbox("Store Type", ["Supermarket Type1", "Supermarket Type2", "Departmental Store", "Food Mart"])
product_id_char = st.selectbox("Product Category Code (FD = Food, DR = Drinks, NC = Non-Consumable)", ["FD", "DR", "NC"])
store_age_years = st.number_input("Store Age (years)", min_value=0, max_value=60, value=16, step=1)
product_type_category = st.selectbox("Product Type Category", ["Perishables", "Non Perishables"])

# Collect the inputs into a single record
input_data = {
    "Product_Weight": product_weight,
    "Product_Sugar_Content": product_sugar_content,
    "Product_Allocated_Area": product_allocated_area,
    "Product_MRP": product_mrp,
    "Store_Size": store_size,
    "Store_Location_City_Type": store_location_city_type,
    "Store_Type": store_type,
    "Product_Id_char": product_id_char,
    "Store_Age_Years": store_age_years,
    "Product_Type_Category": product_type_category,
}

if st.button("Predict", type="primary"):
    try:
        response = requests.post(f"{BACKEND_URL}/v1/predict", json=input_data, timeout=60)
        if response.status_code == 200:
            prediction = response.json()["Predicted Sales (in dollars)"]
            st.success(f"Predicted Sales (in dollars): {prediction}")
        else:
            st.error(f"Prediction failed. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        st.error(f"Unable to connect to the prediction API: {e}")

# ---------------------------------------------------------------- #
# Batch prediction
# ---------------------------------------------------------------- #
st.subheader("Batch Prediction")
st.write("Upload a CSV file containing the same feature columns to score multiple records at once.")

uploaded_file = st.file_uploader("Upload CSV file for batch prediction", type=["csv"])

if uploaded_file is not None:
    batch_data = pd.read_csv(uploaded_file)
    st.write("Preview of the uploaded data:")
    st.write(batch_data.head())

    if st.button("Predict for Batch", type="primary"):
        try:
            uploaded_file.seek(0)
            response = requests.post(
                f"{BACKEND_URL}/v1/predictbatch",
                files={"file": uploaded_file},
                timeout=120,
            )
            if response.status_code == 200:
                predictions = response.json()
                batch_data["Predicted_Sales"] = [predictions[str(i)] for i in range(len(batch_data))]
                st.success("Predictions completed successfully.")
                st.write(batch_data)
                st.download_button(
                    "Download predictions as CSV",
                    batch_data.to_csv(index=False).encode("utf-8"),
                    "superkart_predictions.csv",
                    "text/csv",
                )
            else:
                st.error(f"Batch prediction failed. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            st.error(f"Unable to connect to the prediction API: {e}")
