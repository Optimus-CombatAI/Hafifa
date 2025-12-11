from dataclasses import dataclass

import pandas as pd


@dataclass
class PollutantsDataFrame:
    pm25_vals: pd.DataFrame
    no2_vals: pd.DataFrame
    co2_vals: pd.DataFrame
