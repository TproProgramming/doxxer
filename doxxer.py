import requests
import time
import re
import argparse
import json
import csv
from tqdm import tqdm

# ASCII Art Banner
ascii_banner = r"""
  
      $$\                                                   
      $$ |                                                  
 $$$$$$$ | $$$$$$\  $$\   $$\ $$\   $$\  $$$$$$\   $$$$$$\  
$$  __$$ |$$  __$$\ \$$\ $$  |\$$\ $$  |$$  __$$\ $$  __$$\ 
$$ /  $$ |$$ /  $$ | \$$$$  /  \$$$$  / $$$$$$$$ |$$ |  \__|
$$ |  $$ |$$ |  $$ | $$  $$<   $$  $$<  $$   ____|$$ |      
\$$$$$$$ |\$$$$$$  |$$  /\$$\ $$  /\$$\ \$$$$$$$\ $$ |      
 \_______| \______/ \__/  \__|\__/  \__| \_______|\__|      
                                                              
               IP Geolocation Lookup Tool
"""
print(ascii_banner)
print("Welcome to Doxxer1.0!\n")
print("Usage: Enter an IP address or domain to retrieve its geolocation details.\n"
      "You can perform a single lookup or a bulk lookup by providing multiple IPs/domains.\n"
      "Enter 3 to see the manual or exit and run python doxxer.py -m")

# Rate limit delay (free tier allows 45 requests per minute)
RATE_LIMIT_DELAY = 1  # 1 second delay between requests

def is_valid_ip(ip):
    """Validate an IP address."""
    ip_pattern = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
    return ip_pattern.match(ip)

def is_valid_domain(domain):
    """Validate a domain name."""
    domain_pattern = re.compile(r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    return domain_pattern.match(domain)

def validate_input(ip):
    """Validate if the input is an IP or domain."""
    return is_valid_ip(ip) or is_valid_domain(ip)

def save_to_file(data, filename, format="json"):
    """Save geolocation data to a file."""
    if format == "json":
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
    elif format == "csv":
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(data.keys())
            writer.writerow(data.values())
    print(f"Data saved to {filename}")

def get_ip_geolocation(ip, save_format=None, filename=None):
    """Fetch geolocation data for a given IP or domain."""
    url = f"http://ip-api.com/json/{ip}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        
        if data["status"] == "success":
            print("\n--- IP Geolocation Info ---")
            print(f"IP Address: {data['query']}")
            print(f"Country: {data['country']}")
            print(f"Region: {data['regionName']}")
            print(f"City: {data['city']}")
            print(f"ZIP Code: {data['zip']}")
            print(f"Latitude: {data['lat']}, Longitude: {data['lon']}")
            print(f"ISP: {data['isp']}")
            
            if save_format and filename:
                save_to_file(data, filename, save_format)
        else:
            print(f"Error: {data.get('message', 'Invalid IP address or domain.')}")
    except requests.exceptions.RequestException as e:
        print(f"Error: Unable to fetch data. {e}")

def bulk_lookup(ips, save_format=None, filename=None):
    """Perform geolocation lookup for multiple IPs or domains."""
    for i, ip in enumerate(tqdm(ips, desc="Processing IPs", unit="IP"), 1):
        print(f"\nProcessing {i}/{len(ips)}: {ip}")
        if validate_input(ip.strip()):
            get_ip_geolocation(ip.strip(), save_format, filename)
            time.sleep(RATE_LIMIT_DELAY)
        else:
            print(f"Error: {ip} is not a valid IP address or domain.")

def main_menu():
    """Display the menu and handle user choices."""
    while True:
        print("\nMenu:")
        print("1. Lookup an IP Address or Domain")
        print("2. Bulk Lookup (Multiple IPs/Domains)")
        print("3. Manual")
        print("4. Exit")

        choice = input("\nEnter your choice (1-3): ").strip()

        if choice == "1":
            ip = input("Enter an IP address or domain: ").strip()
            if validate_input(ip):
                get_ip_geolocation(ip)
            else:
                print("Error: Invalid IP address or domain.")
        
        elif choice == "2":
            ips = input("Enter multiple IPs or domains (comma-separated): ").strip().split(',')
            bulk_lookup(ips)
        elif choice == "3":
            show_manual()
        elif choice == "4":
            print("Goodbye! Thanks for using Doxxer.")
            break
        
        else:
            print("Invalid choice, please enter 1, 2, or 3.")

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
      -f, --format  Specify output format (json or csv). Default is json.
      -m, --manual  Show this manual.
    
    DESCRIPTION:
      Doxxer allows users to fetch geolocation data for IP addresses or domains.
      It supports both single and bulk lookups. Results can be saved in JSON or CSV format.
    
    EXAMPLES:
      Lookup a single IP:
        python doxxer.py -i 8.8.8.8
      
      Bulk lookup from a file:
        python doxxer.py -b ips.txt
      
      Save output in CSV format:
        python doxxer.py -i 8.8.8.8 -o results.csv -f csv

    NOTES:
      - The tool uses ip-api.com for fetching geolocation data.
      - Free tier allows 45 requests per minute; rate limiting is applied.

    """
    print(manual_text)
    
def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="IP Geolocation Lookup Tool")
    parser.add_argument("-i", "--ip", help="Single IP address or domain to lookup")
    parser.add_argument("-b", "--bulk", help="File containing multiple IPs or domains (one per line)")
    parser.add_argument("-o", "--output", help="Save output to a file")
    parser.add_argument("-f", "--format", choices=["json", "csv"], default="json", help="Output format")
    parser.add_argument("-m", "--manual", action="store_true", help="Show the manual")

    return parser.parse_args()
    
def main():
    args = parse_args()

    if args.manual:
        show_manual()
    elif args.ip:
        get_ip_geolocation(args.ip, args.format, args.output)
    elif args.bulk:
        with open(args.bulk, "r") as f:
            ips = f.read().splitlines()
        bulk_lookup(ips, args.format, args.output)
    else:
        main_menu()

if __name__ == "__main__":
    main()