import pandas as pd
import numpy as np

# to be tested
def efficiency_ratio(df, period):
    """
    Calculates noise level over period
    The less result the higher noise level
    """

    df['price_diff'] = df['Close'].diff(periods=period).abs()
    
    df['price_diff_per_candle'] = df['Close'].diff().abs()
    
    sum_price_diff_per_candle = df['price_diff_per_candle'].rolling(window=period).sum()
    
    efficiency = df['price_diff'] / sum_price_diff_per_candle
    
    return efficiency


def sample_error(df):
    """
    Calculates whether amount of data is sufficient
    The less result the better 
    """   
    return 1 / np.sqrt(len(df))
