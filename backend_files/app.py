import joblib
import pandas as pd
from flask import Flask, request, jsonify

# Initialize Flask app
app = Flask("Superkart Sales Predictor")

# Load the trained model
model = joblib.load("superkart_model.joblib")

# Define a route for the home page
@app.get('/')
def home():
    return "Welcome to the Superkart store sales predictor app"

# Define an endpoint to predict sales for a single product-store combination
@app.post('/v1/predict')
def predict_sales_single():
    # Get JSON data from the request
    input_data_json = request.get_json()

    # Ensure all expected features are present in the input JSON
    expected_features = [
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

    # Create a DataFrame from the input JSON data
    input_df = pd.DataFrame([input_data_json])

    # Reorder columns to match the training data feature order
    try:
        input_df = input_df[expected_features]
    except KeyError as e:
        return jsonify({'error': f'Missing feature in input: {e}'}), 400

    # Make a prediction using the trained model
    prediction = model.predict(input_df).tolist()[0]

    # Return the prediction as a JSON response
    return jsonify({'Predicted_Sales': prediction})

# Define an endpoint to predict sales for a batch of product-store combinations
@app.post('/v1/predictbatch')
def predict_sales_batch():
    # Get the uploaded CSV file from the request
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and file.filename.endswith('.csv'):
        # Read the file into a DataFrame
        input_data = pd.read_csv(file)

        # Define expected features to ensure correct column order and handling
        expected_features = [
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

        # Check if all expected features are in the uploaded CSV
        missing_features = [f for f in expected_features if f not in input_data.columns]
        if missing_features:
            return jsonify({'error': f'Missing features in uploaded CSV: {missing_features}'}), 400

        # Reorder columns to match the training data feature order
        input_data = input_data[expected_features]

        # Make predictions for the batch data
        predictions = model.predict(input_data).tolist()

        # Add predictions to the DataFrame
        input_data['Predicted_Sales'] = predictions

        # Convert results to dictionary
        result = input_data.to_dict(orient="records")

        return jsonify(result)
    else:
        return jsonify({'error': 'Invalid file type. Please upload a CSV file.'}), 400

# Run the Flask app
if __name__ == '__main__':
    # Use host='0.0.0.0' for external access in containerized environments
    # Set debug=False for production deployment
    app.run(host='0.0.0.0', port=7860, debug=False)
