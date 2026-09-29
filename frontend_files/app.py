import streamlit as st
import pandas as pd
import requests


# Base URL of the Flask backend
BACKEND_URL = "http://superkart-backend:7860" # This should be the service name if using Docker Compose or K8s.

# Streamlit UI for Superkart Sales Prediction
st.title("Superkart Store Sales Prediction App")
st.write("This app predicts the total sales revenue for a given product in a specific store.")
st.write("Adjust the features below to get a sales prediction.")

# --- Input Widgets for Features ---

st.subheader("Product Features")
product_weight = st.slider("Product Weight (kg)", 4.0, 22.0, 12.0, 0.1)
product_allocated_area = st.slider("Product Allocated Area (ratio)", 0.00, 0.30, 0.05, 0.001)
product_mrp = st.slider("Product MRP ($)", 30.0, 270.0, 150.0, 1.0)

product_sugar_content = st.selectbox(
    "Product Sugar Content",
    ['Low Sugar', 'Regular', 'No Sugar']
)

product_type_category = st.selectbox(
    "Product Type Category",
    [
        'Fruits and Vegetables', 'Snack Foods', 'Frozen Foods', 'Dairy', 'Household',
        'Baking Goods', 'Canned', 'Health and Hygiene', 'Meat', 'Soft Drinks', 'Others'
    ]
)

st.subheader("Store Features")
store_age_years = st.slider("Store Age (Years)", 15, 37, 20, 1)

store_size = st.selectbox(
    "Store Size",
    ['Medium', 'High', 'Small']
)

store_location_city_type = st.selectbox(
    "Store Location City Type",
    ['Tier 1', 'Tier 2', 'Tier 3']
)

store_type = st.selectbox(
    "Store Type",
    ['Supermarket Type1', 'Supermarket Type2', 'Departmental Store', 'Food Mart']
)


# --- One-Hot Encode Categorical Inputs for the API Payload ---
input_payload_raw = {
    'Product_Weight': product_weight,
    'Product_Allocated_Area': product_allocated_area,
    'Product_MRP': product_mrp,
    'Store_Age_Years': store_age_years,

    # Product_Sugar_Content
    'Product_Sugar_Content_No Sugar': bool(product_sugar_content == 'No Sugar'),
    'Product_Sugar_Content_Regular': bool(product_sugar_content == 'Regular'),

    # Store_Size
    'Store_Size_Medium': bool(store_size == 'Medium'),
    'Store_Size_Small': bool(store_size == 'Small'),

    # Store_Location_City_Type
    'Store_Location_City_Type_Tier 2': bool(store_location_city_type == 'Tier 2'),
    'Store_Location_City_Type_Tier 3': bool(store_location_city_type == 'Tier 3'),

    # Store_Type
    'Store_Type_Food Mart': bool(store_type == 'Food Mart'),
    'Store_Type_Supermarket Type1': bool(store_type == 'Supermarket Type1'),
    'Store_Type_Supermarket Type2': bool(store_type == 'Supermarket Type2'),

    # Product_Type_Category (Boolean flags for each category, 'Baking Goods' is implicitly the base/dropped one)
    'Product_Type_Category_Canned': bool(product_type_category == 'Canned'),
    'Product_Type_Category_Dairy': bool(product_type_category == 'Dairy'),
    'Product_Type_Category_Frozen Foods': bool(product_type_category == 'Frozen Foods'),
    'Product_Type_Category_Fruits and Vegetables': bool(product_type_category == 'Fruits and Vegetables'),
    'Product_Type_Category_Health and Hygiene': bool(product_type_category == 'Health and Hygiene'),
    'Product_Type_Category_Household': bool(product_type_category == 'Household'),
    'Product_Type_Category_Meat': bool(product_type_category == 'Meat'),
    'Product_Type_Category_Others': bool(product_type_category == 'Others'),
    'Product_Type_Category_Snack Foods': bool(product_type_category == 'Snack Foods'),
    'Product_Type_Category_Soft Drinks': bool(product_type_category == 'Soft Drinks')
}

# Ensure the order of features matches the model's expectation from backend_files/app.py
final_payload = {}
expected_features_backend = [
    'Product_Weight', 'Product_Allocated_Area', 'Product_MRP', 'Store_Age_Years',
    'Product_Sugar_Content_No Sugar', 'Product_Sugar_Content_Regular',
    'Store_Size_Medium', 'Store_Size_Small',
    'Store_Location_City_Type_Tier 2', 'Store_Location_City_Type_Tier 3',
    'Store_Type_Food Mart', 'Store_Type_Supermarket Type1', 'Store_Type_Supermarket Type2',
    'Product_Type_Category_Canned', 'Product_Type_Category_Dairy',
    'Product_Type_Category_Frozen Foods', 'Product_Type_Category_Fruits and Vegetables',
    'Product_Type_Category_Health and Hygiene', 'Product_Type_Category_Household',
    'Product_Type_Category_Meat', 'Product_Type_Category_Others',
    'Product_Type_Category_Snack Foods', 'Product_Type_Category_Soft Drinks'
]

for feature in expected_features_backend:
    final_payload[feature] = input_payload_raw.get(feature, False) # Default to False for boolean if not present


if st.button("Predict Sales", type='primary'):
    try:
        response = requests.post(
            f"{BACKEND_URL}/v1/predict",
            json=final_payload
        )

        if response.status_code == 200:
            result = response.json()
            predicted_sales = result["Predicted_Sales"]
            st.success(f"📈 Predicted Product-Store Sales: **${predicted_sales:.2f}**")
        else:
            st.error(f"Error in API request: {response.status_code} - {response.text}")
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the backend API. Please ensure the backend is running and accessible.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")


# Batch Prediction
st.subheader("Batch Prediction (Upload CSV)")
st.info("The uploaded CSV should contain columns matching the model's input features after preprocessing. Columns like 'Product_Id', 'Store_Id', 'Product_Type', 'Store_Establishment_Year' should be *excluded* and one-hot encoded features should be present (e.g., 'Product_Sugar_Content_No Sugar', 'Store_Size_Medium', etc.).")

uploaded_file = st.file_uploader("Upload CSV file for batch prediction", type=["csv"])

if uploaded_file is not None:
    if st.button("Predict Batch Sales", type='primary'):
        try:
            # Send the file directly as is, assuming it's already preprocessed
            # and contains the correct one-hot encoded columns.
            # The backend expects the CSV to be preprocessed already.
            response = requests.post(
                f"{BACKEND_URL}/v1/predictbatch",
                files={"file": uploaded_file.getvalue()} # getvalue() returns bytes
            )

            if response.status_code == 200:
                batch_results = response.json()
                st.header("Batch Prediction Results")
                st.dataframe(pd.DataFrame(batch_results))
            else:
                st.error(f"Error in batch API request: {response.status_code} - {response.text}")
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the backend API for batch prediction. Please ensure the backend is running and accessible.")
        except Exception as e:
            st.error(f"An unexpected error occurred during batch prediction: {e}")
