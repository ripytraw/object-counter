from io import BytesIO

from flask import Flask, request, jsonify

from counter import config

def create_app():
    
    app = Flask(__name__)
    
    count_action = config.get_count_action()
    prediction_action = config.get_prediction_action()
    
    @app.route('/object-count', methods=['POST'])
    def object_detection():
        
        threshold = float(request.form.get('threshold', 0.5))
        uploaded_file = request.files['file']
        image = BytesIO()
        uploaded_file.save(image)
        count_response = count_action.execute(image, threshold)
        return jsonify(count_response)
    
    @app.route('/list-predictions', methods=['POST'])
    def list_predictions():
        """
        Endpoint to return filtered object detection predictions greater than
        the confidence threshold

        Expects:
            - Multipart form-data
            - 'file': image file (JPG or PNG)
            - 'threshold': float confidence threshold (optional, default=0.5)

        Returns:
            - 200 OK with list of predictions above threshold
            - 400 Bad Request if validation fails
        """
        # ---- Validate threshold ----
        threshold_value = request.form.get('threshold', 0.5)
        try:
            threshold = float(threshold_value)
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid threshold value"}), 400

        # ---- Validate file existence ----
        if 'file' not in request.files:
            return jsonify({"error": "File is required"}), 400
        
        uploaded_file = request.files['file']
        if uploaded_file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        # ---- Validate file type (MIME-based) ----
        if uploaded_file.mimetype not in ('image/jpeg', 'image/png'):
            return jsonify({"error": "Only JPG and PNG files are allowed"}), 400

        # ---- Convert file to in-memory image ----
        image = BytesIO()
        uploaded_file.save(image)

        # ---- Delegate to domain layer ----
        predictions_response = prediction_action.execute(image, threshold)

        return jsonify(predictions_response), 200
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run('0.0.0.0', debug=True)