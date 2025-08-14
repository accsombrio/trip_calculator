import csv
from datetime import datetime
import json
import logging
import math
import os


def haversine(lat1, lon1, lat2, lon2):
    """
    Calculates the distance between two points on Earth using the Haversine formula.

    Args:
        lat1: Latitude of the first point in degrees.
        lon1: Longitude of the first point in degrees.
        lat2: Latitude of the second point in degrees.
        lon2: Longitude of the second point in degrees.

    Returns:
        Distance (km) between two points.
    """
    R = 6371  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(lambda x: math.radians(float(x)), (lat1, lon1, lat2, lon2))
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance


def generate_trip_csv(data_list):
    """
    Processes clean data points to generate trip files and geojson summary.

    Args:
        data_list (list): list of data points to be processed.
    """
    data_list.sort(key=lambda x: x[3])

    file_no = 1
    current_init_row = data_list[0]
    previous_row = data_list[0]
    geojson_dict = {}
    coordinates_list = []

    #set trip json details
    total_distance = 0
    total_duration = 0
    max_kph = 0
    current_kph = 0

    current_file = open(f"trip_{file_no}.csv", 'w', newline='', encoding='utf-8')
    current_writer = csv.writer(current_file)
    current_writer.writerow(['device_id', 'lat', 'lon', 'timestamp'])

    #write trip.geojson
    geojson_dict['type'] = 'FeatureCollection'
    geojson_dict['features'] = []

    for row in data_list:

        lat1 = current_init_row[1]
        long1 = current_init_row[2]
        tstamp1 = current_init_row[3]

        lat2 = row[1]
        long2 = row[2]
        tstamp2 = row[3]

        time_difference = datetime.fromisoformat(tstamp2) - datetime.fromisoformat(tstamp1)
        minutes_difference = time_difference.total_seconds() / 60

        segment_distance = haversine(previous_row[1], previous_row[2], lat2, long2)
        segment_time_difference = datetime.fromisoformat(tstamp2) - datetime.fromisoformat(previous_row[3])
        segment_minutes_difference = segment_time_difference.total_seconds() / 60

        if segment_minutes_difference > 0:
            current_kph = 60*(segment_distance / segment_minutes_difference)

        if haversine(lat1, long1, lat2, long2) > 2 or minutes_difference > 25:
            current_writer.writerow(row)
            coordinates_list.append([row[1],row[2]])

            if current_kph > max_kph:
                max_kph = current_kph
            
            total_distance += segment_distance
            total_duration += segment_minutes_difference

            #calculate trip json details
            data = {
                "total_distance": total_distance,
                "total_duration": total_duration,
                "avg_speed_kmh": 60*total_distance/total_duration,
                "max_speed_kmh": max_kph
            }
            file_path = f"trip_{file_no}.json"
            with open(file_path, 'w') as json_file:
                json.dump(data, json_file, indent=4)

            #process geojson file
            hex_value = file_no % 0xFFFFFF

            feature_dict = {}
            feature_dict['type'] = 'Feature' 
            feature_dict['properties'] = {'name': f"Trip {file_no}", 'color': f"#{hex_value:06X}"}
            feature_dict['geometry'] = {}
            feature_dict['geometry']['type'] = 'LineString'
            feature_dict['geometry']['coordinates'] = coordinates_list

            geojson_dict['features'].append(feature_dict)

            if current_file:
                current_file.close()

            #create new file
            if data_list[-1][3] != row[3]:
                
                total_distance = 0
                total_duration = 0
                max_kph = 0
                current_kph = 0

                segment_distance = 0
                segment_time_difference = 0
                segment_minutes_difference = 0
                coordinates_list = []

                file_no += 1
                current_file = open(f"trip_{file_no}.csv", 'w', newline='', encoding='utf-8')
                current_writer = csv.writer(current_file)
                current_writer.writerow(['device_id', 'lat', 'lon', 'timestamp'])
                current_init_row = row

        if data_list[-1][3] != row[3]:
            current_writer.writerow(row)
            coordinates_list.append([row[1],row[2]])

            #set trip json details
            if current_kph > max_kph:
                max_kph = current_kph

            total_distance += segment_distance
            total_duration += segment_minutes_difference

        previous_row = row

    if current_file:
        current_file.close()

    #write geojson file
    with open("trips.geojson", 'w') as geojson_file:
        json.dump(geojson_dict, geojson_file, indent=4)


def generate_trip_data(input_csv):
    """
    Generates Trip using CSV files, trip details using JSON,
    and log file for invalid records.

    Args:
        input_csv (str): File Name of CSV to be processed.
    """
    logging.basicConfig(
        filename='rejects.log',
        filemode='w',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    with open(input_csv, mode='r', newline='') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)

        clean_data = []

        for row in csv_reader:
            lat = row[1]
            long = row[2]
            tstamp = row[3]

            try:
                lat_float = float(lat)
                if lat_float < -90 or lat_float > 90:
                    logging.error(
                        f'Error record at line {csv_reader.line_num}: '
                        'Latitude data out of range.'
                    )
                    continue
            except ValueError:
                logging.error(
                    f'Error record at line {csv_reader.line_num}: '
                    'Invalid Latitude data.'
                )
                continue

            try:
                long_float = float(long)
                if long_float < -180 or long_float > 180:
                    logging.error(
                        f'Error record at line {csv_reader.line_num}: '
                        'Longitude data out of range.'
                    )
                    continue
            except ValueError:
                logging.error(
                    f'Error record at line {csv_reader.line_num}: '
                    'Invalid Longitude data.'
                )
                continue

            try:
                datetime.fromisoformat(tstamp)
            except ValueError:
                logging.error(
                    f'Error record at line {csv_reader.line_num}: '
                    'Invalid Timestamp data.'
                )
                continue

            clean_data.append(row)

        generate_trip_csv(clean_data)


if __name__ == '__main__':
    input_csv_file = input("Input CSV filename: ")
    generate_trip_data(input_csv_file)