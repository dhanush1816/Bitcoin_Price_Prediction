import yfinance as yf
import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta
import pytz
import time
import logging
import os
from flask import Flask, jsonify, send_file, request
from flask_cors import CORS
from pathlib import Path

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": [
    "http://localhost:5173",
    "http://localhost:10001",
    "https://btc-predictor-frontend.onrender.com"
]}})

class BTCPredictionPipeline:
    def __init__(self):
        """Initialize the prediction pipeline with model paths and parameters"""
        # Use Render.com's persistent disk
        if os.environ.get('RENDER'):
            base_path = Path('/opt/render/project/src')
        else:
            base_path = Path(__file__).parent

        self.base_dir = base_path
        self.models_dir = base_path / 'models'
        self.data_dir = base_path / 'data'
        self.static_dir = base_path / 'static'
        self.logs_dir = base_path / 'logs'

        # Create directories
        for dir_path in [self.models_dir, self.data_dir, self.static_dir, self.logs_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Model paths
        self.lstm_model_path = self.models_dir / 'lstm_model.h5'
        self.rf_model_path = self.models_dir / 'combined_model.pkl'
        self.scaler_path = self.models_dir / 'scaler.pkl'
        self.data_path = self.data_dir / 'btc_data.csv'
        
        # Setup logging with absolute path
        log_file = self.logs_dir / 'btc_prediction.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        # Initialize models
        try:
            self.rf_model = joblib.load(self.rf_model_path)
            logging.info("Models loaded successfully")
        except FileNotFoundError:
            logging.warning("Models not found, initializing new ones")
            self.rf_model = self._initialize_models()
            
        # Load existing data if available
        self.load_historical_data()

    def _initialize_models(self):
        """Initialize new models if not found"""
        rf_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        # Save the initialized models
        joblib.dump(rf_model, self.rf_model_path)
        return rf_model

    def load_historical_data(self):
        """
        Load existing historical data or create new dataset
        """
        try:
            if os.path.exists(self.data_path):
                self.data = pd.read_csv(self.data_path)
                # Convert Date column to datetime if it exists
                if 'Date' in self.data.columns:
                    self.data['Date'] = pd.to_datetime(self.data['Date'])
                    self.data.set_index('Date', inplace=True)
                logging.info("Existing data loaded successfully")
            else:
                self.data = pd.DataFrame()
                logging.info("New dataset created")
        except Exception as e:
            logging.error(f"Error loading historical data: {str(e)}")
            self.data = pd.DataFrame()

    def get_latest_data(self):
        """
        Fetch the latest Bitcoin data and determine if update is needed
        """
        utc_now = datetime.now(pytz.UTC)
        
        try:
            # Always get at least 501 days of data plus extra for predictions
            start_date = utc_now - timedelta(days=max(730, 501 + 60))  # 501 for features + 60 for predictions
            start_date_str = start_date.strftime('%Y-%m-%d')
            end_date_str = utc_now.strftime('%Y-%m-%d')
            
            logging.info(f"Fetching data from {start_date_str} to {end_date_str}")
            new_data = yf.download('BTC-USD', 
                                 start=start_date_str, 
                                 end=end_date_str,
                                 progress=False)
            
            if not new_data.empty and len(new_data) >= 501:
                logging.info(f"Downloaded {len(new_data)} records")
                return new_data
            else:
                logging.error(f"Insufficient data: got {len(new_data) if not new_data.empty else 0} records, need at least 501")
                return None
            
        except Exception as e:
            logging.error(f"Error fetching data: {str(e)}")
            return None

    def update_dataset(self, new_data):
        """
        Update the existing dataset with new data
        """
        if new_data is not None and not new_data.empty:
            try:
                if self.data.empty:
                    self.data = new_data
                    # Force update when we have no existing data
                    self.data.to_csv(self.data_path)
                    logging.info(f"Created new dataset with {len(new_data)} records")
                    return True
                else:
                    # Ensure no duplicate dates
                    combined_data = pd.concat([self.data, new_data])
                    self.data = combined_data[~combined_data.index.duplicated(keep='last')]
                    self.data = self.data.sort_index()
                    
                    # Save updated dataset
                    self.data.to_csv(self.data_path)
                    logging.info(f"Dataset updated successfully with {len(new_data)} new records")
                    return True
                
            except Exception as e:
                logging.error(f"Error updating dataset: {str(e)}")
                return False
        
        if self.data.empty:
            logging.error("No data available and couldn't fetch new data")
            return False
        
        logging.info("No new data to update")
        return False

    def prepare_features(self):
        """
        Prepare features for both LSTM and RF models
        """
        try:
            if self.data.empty:
                raise ValueError("No data available for feature preparation")
            
            data = self.data[['Close']].values
            scaled_data = self.scaler.transform(data)
            
            # Prepare LSTM features
            data_reshaped = data.reshape(data.shape[0], data.shape[1], 1)
            lstm_features = data_reshaped[:, -1, 0]
            
            # Prepare RF features with correct size
            X_rf, Y_rf = [], []
            for i in range(len(scaled_data) - 500):  # Removed the -1
                X_rf.append(scaled_data[i:(i + 500), 0])
                Y_rf.append(scaled_data[i + 500 - 1, 0])  # Adjusted index
            
            X_rf, Y_rf = np.array(X_rf), np.array(Y_rf)
            X_rf = X_rf.reshape(X_rf.shape[0], -1)
            
            return scaled_data, lstm_features, X_rf, Y_rf
            
        except Exception as e:
            logging.error(f"Error preparing features: {str(e)}")
            raise

    def make_predictions(self, scaled_data):
        """
        Generate 60-day predictions using the Random Forest model
        """
        try:
            # Prepare current input data with correct size
            X_current = scaled_data[-501:].reshape(1, -1)  # Use 501 features
            
            # Generate predictions
            predictions = []
            current_input = X_current.copy()
            
            for _ in range(60):
                prediction = self.rf_model.predict(current_input)
                predictions.append(prediction[0])
                
                # Update input for next prediction
                current_input = np.roll(current_input, -1)
                current_input[0, -1] = prediction[0]
            
            # Inverse transform predictions
            predictions = self.scaler.inverse_transform(
                np.array(predictions).reshape(-1, 1)
            )
            
            return predictions
            
        except Exception as e:
            logging.error(f"Error making predictions: {str(e)}")
            raise

    def save_predictions(self, predictions):
        """
        Save predictions with timestamps
        """
        dates = pd.date_range(
            start=datetime.now(), 
            periods=len(predictions), 
            freq='D'
        )
        
        pred_df = pd.DataFrame({
            'Date': dates,
            'Predicted_Price': predictions.flatten()
        })
        
        # Save to CSV with absolute path
        predictions_file = self.data_dir / f'predictions_{datetime.now().strftime("%Y%m%d")}.csv'
        pred_df.to_csv(predictions_file)
        logging.info(f"Predictions saved to {predictions_file}")
        
        return pred_df

    def plot_predictions(self, predictions):
        """
        Plot the predictions and save to static folder
        """
        plt.figure(figsize=(12, 6))
        plt.plot(predictions, label='Predicted Price')
        plt.title('Bitcoin Price Predictions - Next 60 Days')
        plt.xlabel('Days')
        plt.ylabel('Price (USD)')
        plt.legend()
        
        # Save to static folder with absolute path
        plot_file = self.static_dir / f'predictions_plot_{datetime.now().strftime("%Y%m%d")}.png'
        plt.savefig(plot_file)
        plt.close()
        
        logging.info(f"Plot saved to {plot_file}")
        return plot_file

    def run_pipeline(self):
        """
        Run the complete prediction pipeline
        """
        logging.info("Starting prediction pipeline")
        
        try:
            # Get latest data
            new_data = self.get_latest_data()
            if new_data is None:
                raise ValueError("Failed to fetch market data")
            
            # Update dataset
            self.data = new_data  # Always use fresh data
            
            # Ensure we have enough data (501 points for features + extra for predictions)
            if len(self.data) < 501:
                raise ValueError(f"Insufficient data: need at least 501 days, got {len(self.data)}")
            
            # Prepare features
            scaled_data, lstm_features, X_rf, Y_rf = self.prepare_features()
            
            # Generate predictions
            predictions = self.make_predictions(scaled_data)
            
            # Save and plot results
            pred_df = self.save_predictions(predictions)
            plot_file = self.plot_predictions(predictions)
            
            logging.info("Pipeline completed successfully")
            return pred_df, plot_file
            
        except Exception as e:
            logging.error(f"Pipeline error: {str(e)}")
            return None, None

# Initialize the pipeline
pipeline = BTCPredictionPipeline()

@app.route('/api/predictions', methods=['GET'])
def get_predictions():
    try:
        pred_df, plot_file = pipeline.run_pipeline()
        
        if pred_df is not None and plot_file is not None:
            predictions = pred_df.to_dict(orient='records')
            plot_url = f'/api/plot/{os.path.basename(plot_file)}'
            
            return jsonify({
                'success': True,
                'predictions': predictions,
                'plot_url': plot_url,
                'last_updated': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to generate predictions. Please try again.'
            }), 500
            
    except Exception as e:
        logging.error(f"API error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@app.route('/api/plot/<filename>', methods=['GET'])
def get_plot(filename):
    try:
        return send_file(f'static/{filename}', mimetype='image/png')
    except Exception as e:
        logging.error(f"Error serving plot: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error loading plot'
        }), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)