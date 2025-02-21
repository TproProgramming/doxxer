import requests
import time
import re
import argparse
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import logging
from ratelimit import limits, sleep_and_retry

# ASCII Art Banner with color support
BANNER = r"""

      $$\                                                   
      $$ |                                                  
 $$$$$$$ | $$$$$$\  $$\   $$\ $$\   $$\  $$$$$$\   $$$$$$\  
$$  __$$ |$$  __$$\ \$$\ $$  |\$$\ $$  |$$  __$$\ $$  __$$\ 
$$ /  $$ |$$ /  $$ | \$$$$  /  \$$$$  / $$$$$$$$ |$$ |  \__|
$$ |  $$ |$$ |  $$ | $$  $$   $$  $$  $$   ____|$$ |      
\$$$$$$$ |\$$$$$$  |$$  /\$$\ $$  /\$$\ \$$$$$$$\ $$ |      
 \_______| \______/ \__/  \__|\__/  \__| \_______|\__|      
                                                              
               IP Geolocation Lookup Tool
"""

VERSION = "1.1"

def print_banner():
    """Print the banner with version and current time"""
    print(BANNER)
    print(f"\033[36mVersion: {VERSION}")
    print(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\033[0m")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('doxxer.log'),
        logging.StreamHandler()
    ]
)

class Geolocator:
    """Class to handle IP geolocation lookups"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "http://ip-api.com/json"
        # Premium API endpoint if API key is provided
        if api_key:
            self.base_url = "http://pro.ip-api.com/json"
        
        # Create output directory if it doesn't exist
        Path("output").mkdir(exist_ok=True)

    @sleep_and_retry
    @limits(calls=45, period=60)  # Rate limiting decorator
    def get_ip_geolocation(self, ip: str) -> Dict:
        """Fetch geolocation data with automatic rate limiting"""
        url = f"{self.base_url}/{ip}"
        params = {"key": self.api_key} if self.api_key else {}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching data for {ip}: {str(e)}")
            return {"status": "fail", "query": ip, "message": str(e)}

    def bulk_lookup(self, ips: List[str], max_workers: int = 5) -> List[Dict]:
        """Perform concurrent bulk lookups with progress bar"""
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.get_ip_geolocation, ip.strip()) 
                      for ip in ips if self.validate_input(ip.strip())]
            
            for future in tqdm(futures, desc="Processing IPs", unit="IP"):
                results.append(future.result())
        
        return results

    @staticmethod
    def validate_input(ip: str) -> bool:
        """Validate if input is IP or domain"""
        ip_pattern = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        domain_pattern = re.compile(r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        return bool(ip_pattern.match(ip) or domain_pattern.match(ip))

    def save_results(self, data: Union[Dict, List[Dict]], 
                    format: str = "json", 
                    filename: Optional[str] = None) -> str:
        """Save results with automatic filename generation"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"output/geolocation_results_{timestamp}.{format}"

        try:
            if format == "json":
                with open(filename, "w") as f:
                    json.dump(data, f, indent=4)
            elif format == "csv":
                if isinstance(data, dict):
                    data = [data]
                with open(filename, "w", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
            elif format == "txt":
                with open(filename, "w") as f:
                    if isinstance(data, dict):
                        data = [data]
                    for entry in data:
                        f.write("\n--- IP Geolocation Info ---\n")
                        for key, value in entry.items():
                            f.write(f"{key}: {value}\n")
                        f.write("\n")
            
            logging.info(f"Results saved to {filename}")
            return filename
        except Exception as e:
            logging.error(f"Error saving results: {str(e)}")
            raise

def parse_args():
    """Enhanced argument parser"""
    parser = argparse.ArgumentParser(
        description="IP Geolocation Lookup Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-i", "--ip", help="Single IP address or domain to lookup")
    parser.add_argument("-b", "--bulk", help="File containing multiple IPs/domains (one per line)")
    parser.add_argument("-o", "--output", help="Save output to a file")
    parser.add_argument("-f", "--format", choices=["json", "csv", "txt"], 
                       default="json", help="Output format")
    parser.add_argument("-k", "--api-key", help="API key for premium features")
    parser.add_argument("-w", "--workers", type=int, default=5,
                       help="Number of worker threads for bulk lookup")
    parser.add_argument("-m", "--manual", action="store_true", help="Show the manual")
    return parser.parse_args()

def show_manual():
    """Display the manual for Doxxer."""
    manual_text = """
    Doxxer - IP Geolocation Lookup Tool

    USAGE:
      python doxxer.py [OPTIONS]

    OPTIONS:
      -i, --ip      Perform a lookup for a single IP address or domain.
      -b, --bulk    Perform a bulk lookup from a file (one IP/domain per line).
      -o, --output  Save the results to a specified file.
      -f, --format  Specify output format (json, csv, or txt). Default is json.
      -k, --api-key API key for premium features.
      -w, --workers Number of worker threads for bulk lookup (default: 5).
      -m, --manual  Show this manual.
    
    DESCRIPTION:
      Doxxer allows users to fetch geolocation data for IP addresses or domains.
      It supports both single and bulk lookups with concurrent processing.
      Results can be saved in JSON, CSV, or TXT format.
    
    EXAMPLES:
      Lookup a single IP:
        python doxxer.py -i 8.8.8.8
      
      Bulk lookup from a file:
        python doxxer.py -b ips.txt
      
      Save output in CSV format:
        python doxxer.py -i 8.8.8.8 -o results.csv -f csv
      
      Use premium API:
        python doxxer.py -i 8.8.8.8 -k YOUR_API_KEY

    NOTES:
      - Free tier allows 45 requests per minute (rate limiting applied)
      - Results are automatically saved in the 'output' directory
      - Logs are saved to 'doxxer.log'
    """
    print(manual_text)

def interactive_menu(geolocator):
    """Enhanced interactive menu"""
    while True:
        print("\nDoxxer - IP Geolocation Menu:")
        print("1. Lookup single IP/domain")
        print("2. Bulk lookup")
        print("3. Show manual")
        print("4. Exit")
        
        try:
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == "1":
                ip = input("Enter IP address or domain: ").strip()
                if geolocator.validate_input(ip):
                    result = geolocator.get_ip_geolocation(ip)
                    if result["status"] == "success":
                        print("\n--- IP Geolocation Info ---")
                        for key, value in result.items():
                            print(f"{key}: {value}")
                        
                        if input("\nSave results? (y/n): ").lower() == 'y':
                            format = input("Enter format (json/csv/txt): ").lower()
                            if format in ['json', 'csv', 'txt']:
                                geolocator.save_results(result, format)
                else:
                    print("Error: Invalid IP address or domain.")
            
            elif choice == "2":
                ips = input("Enter IPs/domains (comma-separated): ").strip().split(',')
                results = geolocator.bulk_lookup(ips)
                if input("\nSave results? (y/n): ").lower() == 'y':
                    format = input("Enter format (json/csv/txt): ").lower()
                    if format in ['json', 'csv', 'txt']:
                        geolocator.save_results(results, format)
            
            elif choice == "3":
                show_manual()
            
            elif choice == "4":
                print("Goodbye! Thanks for using Doxxer.")
                break
            
            else:
                print("Invalid choice. Please enter 1-4.")
                
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            break
        except Exception as e:
            logging.error(f"Error in menu operation: {str(e)}")

def main():
    print_banner()
    args = parse_args()
    
    try:
        geolocator = Geolocator(api_key=args.api_key)
        
        if args.manual:
            show_manual()
        elif args.ip:
            if not geolocator.validate_input(args.ip):
                logging.error(f"Invalid IP or domain: {args.ip}")
                return
            
            result = geolocator.get_ip_geolocation(args.ip)
            if result["status"] == "success":
                print("\n--- IP Geolocation Info ---")
                for key, value in result.items():
                    print(f"{key}: {value}")
                
                if args.output:
                    geolocator.save_results(result, args.format, args.output)
            else:
                logging.error(f"Lookup failed: {result.get('message')}")
                
        elif args.bulk:
            try:
                with open(args.bulk, "r") as f:
                    ips = f.read().splitlines()
                results = geolocator.bulk_lookup(ips, max_workers=args.workers)
                if args.output:
                    geolocator.save_results(results, args.format, args.output)
            except FileNotFoundError:
                logging.error(f"Bulk input file not found: {args.bulk}")
        else:
            interactive_menu(geolocator)
            
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()