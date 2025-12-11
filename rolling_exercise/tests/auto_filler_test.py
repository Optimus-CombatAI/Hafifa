import pandas as pd
import utils.utils as utils_function


def test():
    column_names = ['PM2.5', 'NO2', 'CO2']
    df = pd.DataFrame(columns=column_names, index=range(5))
    print(f"before:\n{df}")
    utils_function.fill_weather_report_by_internet_data(df)
    print(f"after:\n{df}")

    df = pd.DataFrame(columns=column_names, index=range(5))
    print(f"before:\n{df}")
    utils_function.fill_weather_report_by_dataset_data(df)
    print(f"after:\n{df}")


if __name__ == '__main__':
    test()
