HEADER = "date,city,PM2.5,NO2,CO2"


def csv_row(date: str = "2024-11-19", city: str = "Haifa", pm25: str = "12", no2: str = "40", co2: str = "3") -> str:
    return f"{date},{city},{pm25},{no2},{co2}"


def to_csv(*rows: str) -> bytes:
    return "\n".join([HEADER, *rows]).encode()
