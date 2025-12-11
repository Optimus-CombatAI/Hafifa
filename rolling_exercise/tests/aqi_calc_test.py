import utils.utils as utils_function
from utils.calculate_aqi import calculate_aqi


def test():
    pollutants_data = utils_function._get_all_pollutants_data()
    for pm, no, co in zip(pollutants_data.pm25_vals, pollutants_data.no2_vals, pollutants_data.co2_vals):
        if pm and no and co:
            print(f"pm2.5: {pm} no2: {no}, co2: {co}")
            overall_aqi, aqi_level = calculate_aqi(pm, no, co)
            print(f"overall_aqi: {overall_aqi}, aqi_level: {aqi_level}")


if __name__ == '__main__':
    test()
