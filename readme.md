# Doxxer - IP Geolocation Lookup Tool

## Overview
Doxxer is a command-line tool for retrieving geolocation information for IP addresses and domain names. It supports both single and bulk lookups, automatic rate limiting, and multiple output formats (JSON, CSV, TXT).

## Features
- Single IP/domain lookup
- Bulk lookup from a file
- Rate limiting (45 requests per minute)
- Save results in JSON, CSV, or TXT format
- Interactive menu for ease of use
- Logging support

## Installation
Ensure you have Python installed, then install the required dependencies:
```sh
pip install -r requirements.txt
```

## Usage
### Single IP Lookup:
```sh
python doxxer.py -i 8.8.8.8
```

### Bulk Lookup:
```sh
python doxxer.py -b ips.txt
```

### Save Results:
```sh
python doxxer.py -i 8.8.8.8 -o results.json -f json
```

### Using an API Key:
```sh
python doxxer.py -i 8.8.8.8 -k YOUR_API_KEY
```

### Interactive Mode:
```sh
python doxxer.py
```

### Show Manual:
```sh
python doxxer.py -m
```

## Output Formats
- JSON
- CSV
- TXT

## Logging
Doxxer saves logs to `doxxer.log` for debugging and tracking requests.

## Notes
- Free API tier allows 45 requests per minute (rate limiting is applied automatically).
- Results are saved in the `output` directory.

## License
MIT License

