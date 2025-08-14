# GPS Trip Calculator

This Python script processes raw GPS data from a CSV file to generate individual trip files, trip statistics, and a visual representation in GeoJSON format. It also logs invalid or malformed records for further inspection.

---

## 📦 Features

- ✅ Validates and filters GPS records (latitude, longitude, timestamp)
- ✅ Splits GPS records into individual trips based on time/distance thresholds
- ✅ Calculates total distance, duration, average and maximum speed for each trip
- ✅ Generates:
  - CSV file per trip
  - JSON file with trip statistics
  - A combined `trips.geojson` for visualization
- ✅ Logs invalid records to `rejects.log`

---

## 📂 Input CSV Format

The input CSV file **must have a header** and the following columns (in this order):

```

device\_id, lat, lon, timestamp

````

- `device_id`: Identifier for the GPS device
- `lat`: Latitude in decimal degrees (`-90` to `90`)
- `lon`: Longitude in decimal degrees (`-180` to `180`)
- `timestamp`: ISO 8601 format (e.g. `2025-08-14T12:34:56`)

---

## 🚀 How It Works

1. The script reads and validates each row:
   - Latitude and longitude must be valid numbers within range
   - Timestamp must be in ISO format
2. Invalid records are logged to `rejects.log` and skipped.
3. Valid points are sorted by timestamp and grouped into "trips" based on:
   - More than **2 km** between consecutive points
   - More than **25 minutes** of time gap
4. For each trip:
   - A CSV file `trip_<n>.csv` is created
   - A JSON file `trip_<n>.json` is generated with stats:
     - `total_distance` (km)
     - `total_duration` (minutes)
     - `avg_speed_kmh`
     - `max_speed_kmh`
   - A colored path is added to `trips.geojson`

---

## 📄 Output Files

After running the script, the following files will be created:

- `trip_1.csv`, `trip_2.csv`, ... : GPS points per trip
- `trip_1.json`, `trip_2.json`, ... : Stats for each trip
- `trips.geojson` : Combined GeoJSON file for all trips
- `rejects.log` : Log of invalid data rows

---

## ▶️ Usage

### Run the script:

```bash
python your_script.py
````

You will be prompted to enter the input CSV filename:

```
Input CSV filename: my_data.csv
```

> Make sure `my_data.csv` exists in the current working directory and follows the correct format.

---

## ⚠️ Requirements

* Python 3.7+
* No external libraries required (uses built-in Python modules)

---

## ✏️ Example

### Input (`data.csv`):

```csv
device_id,lat,lon,timestamp
1234,37.7749,-122.4194,2025-08-14T12:00:00
1234,37.7750,-122.4195,2025-08-14T12:10:00
...
```

### Output:

* `trip_1.csv`
* `trip_1.json`
* `trips.geojson`
* `rejects.log` (if errors)

---

## 🛠️ Customization

You can modify the following values in the script:

* Distance threshold (`> 2 km`)
* Time threshold (`> 25 minutes`)
* Speed calculation logic or units

---

## 📌 License

This project is open-source and available under the MIT License.

---

## 🧭 Credits

* Haversine formula for distance calculation
* GeoJSON standard for spatial visualization

