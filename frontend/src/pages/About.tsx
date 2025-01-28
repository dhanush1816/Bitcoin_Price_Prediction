import React from 'react';
import { Brain, GitBranch, BarChart2, Shield } from 'lucide-react';

const About = () => {
  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">About Our Prediction Model</h1>
        <p className="text-gray-300">
          Learn about our advanced hybrid prediction system that combines LSTM neural networks
          and Random Forest algorithms to forecast Bitcoin prices.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center mb-4">
            <Brain className="text-blue-500 mr-2" />
            <h2 className="text-xl font-semibold">Machine Learning</h2>
          </div>
          <p className="text-gray-300">
            Our system utilizes a sophisticated hybrid model combining Long Short-Term Memory (LSTM)
            neural networks with Random Forest regression to capture both long-term patterns and
            short-term market dynamics.
          </p>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center mb-4">
            <GitBranch className="text-green-500 mr-2" />
            <h2 className="text-xl font-semibold">Data Processing</h2>
          </div>
          <p className="text-gray-300">
            We process historical Bitcoin price data using advanced normalization techniques and
            feature engineering to ensure our models receive high-quality input data for accurate
            predictions.
          </p>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center mb-4">
            <BarChart2 className="text-purple-500 mr-2" />
            <h2 className="text-xl font-semibold">Prediction Pipeline</h2>
          </div>
          <p className="text-gray-300">
            Our automated pipeline fetches real-time market data, processes it through our hybrid
            model, and generates 60-day price predictions that are updated daily to maintain accuracy.
          </p>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center mb-4">
            <Shield className="text-red-500 mr-2" />
            <h2 className="text-xl font-semibold">Model Reliability</h2>
          </div>
          <p className="text-gray-300">
            While our model achieves high accuracy on historical data, cryptocurrency markets are
            inherently volatile. Our predictions should be used as one of many tools in your
            research process.
          </p>
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg p-6 mt-8">
        <h2 className="text-2xl font-semibold mb-4">Technical Details</h2>
        <div className="space-y-4 text-gray-300">
          <p>
            The prediction system implements a BTCPredictionPipeline class that handles data
            fetching, preprocessing, and model inference. Key features include:
          </p>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li>Real-time data updates using the yfinance API</li>
            <li>Automated data preprocessing and feature engineering</li>
            <li>Hybrid model combining LSTM and Random Forest predictions</li>
            <li>60-day rolling prediction window</li>
            <li>Automated model retraining and validation</li>
            <li>Comprehensive error handling and logging</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default About;