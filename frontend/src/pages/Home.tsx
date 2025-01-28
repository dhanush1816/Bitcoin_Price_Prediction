import React, { useState, useEffect } from 'react';
import { TrendingUp, AlertCircle, Loader2 } from 'lucide-react';
import PriceChart from '../components/PriceChart';

interface Prediction {
  Date: string;
  Predicted_Price: number;
}

interface PredictionResponse {
  success: boolean;
  predictions: Prediction[];
  plot_url: string;
  message?: string;
}

const Home = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [plotUrl, setPlotUrl] = useState<string>('');
  const [currentPage, setCurrentPage] = useState(0);
  const itemsPerPage = 8;

  useEffect(() => {
    const fetchPredictions = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/predictions');
        const data: PredictionResponse = await response.json();

        if (data.success) {
          setPredictions(data.predictions);
          setPlotUrl(`http://localhost:5000${data.plot_url}`);
        } else {
          setError(data.message || 'Failed to fetch predictions');
        }
      } catch (err) {
        setError('Error connecting to the server');
      } finally {
        setLoading(false);
      }
    };

    fetchPredictions();
  }, []);

  // Calculate total pages
  const totalPages = Math.ceil(predictions.length / itemsPerPage);
  
  // Get current items
  const getCurrentItems = () => {
    const start = currentPage * itemsPerPage;
    const end = start + itemsPerPage;
    return predictions.slice(start, end);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center space-y-4">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto" />
          <p className="text-xl font-semibold text-red-500">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold mb-4">Bitcoin Price Predictions</h1>
        <p className="text-gray-300 max-w-2xl mx-auto">
          Advanced machine learning algorithms analyze historical data to predict Bitcoin's price movements
          over the next 60 days with our hybrid LSTM-Random Forest model.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        {/* Graph Section */}
        <div className="bg-gray-800 rounded-lg p-6 shadow-xl md:col-span-2 lg:col-span-1">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <TrendingUp className="mr-2 text-green-500" />
            Price Prediction Graph
          </h2>
          <div className="aspect-[2/1] bg-gray-700 rounded-lg overflow-hidden">
            <PriceChart predictions={predictions} />
          </div>
        </div>

        {/* Table Section */}
        <div className="bg-gray-800 rounded-lg p-6 shadow-xl md:col-span-2 lg:col-span-1">
          <h2 className="text-xl font-semibold mb-4">Predicted Prices</h2>
          <div className="flex">
            {/* Table with custom scrollbar */}
            <div className="flex-grow pr-2 custom-scrollbar" style={{ maxHeight: '400px', overflowY: 'auto' }}>
              <table className="w-full">
                <thead className="sticky top-0 bg-gray-800 z-10">
                  <tr className="border-b border-gray-700">
                    <th className="px-4 py-2 text-left">Date</th>
                    <th className="px-4 py-2 text-right">Predicted Price (USD)</th>
                  </tr>
                </thead>
                <tbody>
                  {predictions.map((data, index) => (
                    <tr key={index} className="border-b border-gray-700 hover:bg-gray-700/50 transition-colors">
                      <td className="px-4 py-2">
                        {new Date(data.Date).toLocaleDateString()}
                      </td>
                      <td className="px-4 py-2 text-right">
                        ${data.Predicted_Price.toLocaleString(undefined, {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        })}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <style jsx>{`
            .custom-scrollbar::-webkit-scrollbar {
              width: 8px;
            }

            .custom-scrollbar::-webkit-scrollbar-track {
              background: #374151;
              border-radius: 4px;
            }

            .custom-scrollbar::-webkit-scrollbar-thumb {
              background: #4B5563;
              border-radius: 4px;
              transition: background-color 0.2s;
            }

            .custom-scrollbar::-webkit-scrollbar-thumb:hover {
              background: #6B7280;
            }

            /* For Firefox */
            .custom-scrollbar {
              scrollbar-width: thin;
              scrollbar-color: #4B5563 #374151;
            }
          `}</style>
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg p-6 mt-8">
        <div className="flex items-start space-x-2">
          <AlertCircle className="text-yellow-500 mt-1 flex-shrink-0" />
          <div>
            <h3 className="font-semibold mb-2">Disclaimer</h3>
            <p className="text-gray-300 text-sm">
              The predictions shown are based on historical data and machine learning models.
              Cryptocurrency markets are highly volatile and these predictions should not be
              considered as financial advice. Always do your own research before making investment
              decisions.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Home;