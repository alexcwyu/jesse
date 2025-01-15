from typing import Union
import numpy as np
from numba import njit
from jesse.helpers import get_candle_source, same_length, slice_candles


@njit
def _dpo(source, period):
    # Calculate the X/2 + 1 shift
    shift = period // 2 + 1

    # Calculate SMA using numpy's cumsum for better performance
    sma = np.zeros_like(source)
    temp = np.zeros(len(source) + 1)
    temp[1:] = source
    cumsum = np.zeros(len(source) + 1)
    for i in range(1, len(cumsum)):
        cumsum[i] = cumsum[i-1] + temp[i]
    sma[period-1:] = (cumsum[period:] - cumsum[:-period]) / period

    # Shift the price series and subtract SMA
    shifted_source = np.roll(source, shift)
    dpo = shifted_source - sma

    # First (period-1 + shift) elements will be invalid due to the rolling calculations
    dpo[:period-1+shift] = np.nan

    return dpo


def dpo(candles: np.ndarray, period: int = 5, source_type: str = "close", sequential: bool = False) -> Union[float, np.ndarray]:
    """
    DPO - Detrended Price Oscillator

    Formula: Price {X/2 + 1} periods ago less the X-period simple moving average

    :param candles: np.ndarray
    :param period: int - default: 5
    :param source_type: str - default: "close"
    :param sequential: bool - default: False

    :return: float | np.ndarray
    """
    candles = slice_candles(candles, sequential)
    source = get_candle_source(candles, source_type=source_type)
    res = _dpo(source, period)

    return same_length(candles, res) if sequential else res[-1]
