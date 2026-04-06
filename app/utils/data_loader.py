import pandas as pd
import numpy as np
import os
from typing import List, Tuple, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLoader:
    _instance = None
    _df = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataLoader, cls).__new__(cls)
        return cls._instance

    def load_data(self, file_path: str = "all_stocks_5yr.csv"):
        """Load the CSV file if not already loaded."""
        if self._df is None:
            if not os.path.exists(file_path):
                # Try relative to the script location if not found in CWD
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                file_path = os.path.join(base_dir, "all_stocks_5yr.csv")
            
            logger.info(f"Loading stock data from {file_path}...")
            try:
                self._df = pd.read_csv(file_path)
                self._df['date'] = pd.to_datetime(self._df['date'])
                logger.info("Data loaded successfully.")
            except Exception as e:
                logger.error(f"Error loading data: {e}")
                raise e
        return self._df

    def get_portfolio_metrics(self, num_assets: int = 10) -> Tuple[List[str], np.ndarray, np.ndarray]:
        """
        Get expected returns and covariance matrix for the top N assets.
        Returns: (tickers, mean_returns, covariance_matrix)
        """
        df = self.load_data()
        
        # To make it simple and robust, we'll pick the top N tickers with the most data points
        ticker_counts = df['Name'].value_counts()
        selected_tickers = ticker_counts.head(num_assets).index.tolist()
        
        # Pivot the data to get closing prices
        pivot_df = df[df['Name'].isin(selected_tickers)].pivot(index='date', columns='Name', values='close')
        
        # Calculate daily returns
        returns_df = pivot_df.pct_change().dropna()
        
        # Calculate mean daily returns and covariance matrix
        mean_returns = returns_df.mean().values
        cov_matrix = returns_df.cov().values
        
        return selected_tickers, mean_returns, cov_matrix

    def get_cumulative_returns(self, tickers: List[str], num_days: int = 252) -> Tuple[List[str], np.ndarray]:
        """
        Get normalized cumulative price trends for the given assets over num_days.
        Useful for backtesting trajectories in the dashboard.
        """
        df = self.load_data()
        
        # Pivot and REORDER columns to match the tickers list exactly
        pivot_df = df[df['Name'].isin(tickers)].pivot(index='date', columns='Name', values='close')
        pivot_df = pivot_df[tickers].tail(num_days)
        
        # Use forward fill for NaNs
        prices = pivot_df.ffill().bfill().values
        
        # Normalize to 100% basis (1.0)
        normalized_prices = prices / prices[0]
        dates = [d.strftime('%Y-%m-%d') for d in pivot_df.index]
        
        return dates, normalized_prices

    def get_monte_carlo_samples(self, tickers: List[str], mean_returns: np.ndarray, cov_matrix: np.ndarray, num_samples: int = 500) -> List[Dict[str, float]]:
        """
        Generate N random portfolio points for Monte Carlo simulation.
        Uses a concentrated sampling technique to avoid clustering.
        """
        num_assets = len(tickers)
        samples = []
        
        for i in range(num_samples):
            # To avoid the 'Law of Large Numbers' clustering in the center:
            # We vary the concentration (sparsity) of weights.
            if i % 3 == 0:
                # Sparse portfolio (only few assets)
                weights = np.zeros(num_assets)
                num_active = np.random.randint(2, min(5, num_assets + 1))
                active_indices = np.random.choice(num_assets, num_active, replace=False)
                weights[active_indices] = np.random.exponential(1.0, num_active)
            else:
                # Dense but varied weights (exponential distribution)
                weights = np.random.exponential(1.0, num_assets)
            
            weights /= np.sum(weights)
            
            # Calculate annualized return and risk
            ret = np.dot(weights, mean_returns) * 252
            risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
            
            samples.append({
                "risk": round(float(risk) * 100, 4),
                "return": round(float(ret) * 100, 4)
            })
            
        return samples

# Singleton instance
data_loader = DataLoader()
