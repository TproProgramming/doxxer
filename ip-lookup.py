import requests
import time

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
print("Welcome to Doxxer!\n")

def get_ip_geolocation(ip):
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
        else:
            print(f"Error: {data.get('message', 'Invalid IP address or domain.')}")
    except requests.exceptions.RequestException as e:
        print(f"Error: Unable to fetch data. {e}")

def main_menu():
    """Display the menu and handle user choices."""
    while True:
        print("\nMenu:")
        print("1. Lookup an IP Address or Domain")
        print("2. Bulk Lookup (Multiple IPs/Domains)")
        print("3. Exit")

        choice = input("\nEnter your choice (1-3): ").strip()

        if choice == "1":
            ip = input("Enter an IP address or domain: ").strip()
            if ip:
                get_ip_geolocation(ip)
            else:
                print("Error: No input provided.")
        
        elif choice == "2":
            ips = input("Enter multiple IPs or domains (comma-separated): ").strip().split(',')
            for ip in ips:
                get_ip_geolocation(ip.strip())
                time.sleep(1)  # To prevent hitting API rate limits
            
        elif choice == "3":
            print("Goodbye! Thanks for using Doxxer.")
            break
        
        else:
            print("Invalid choice, please enter 1, 2, or 3.")

if __name__ == "__main__":
    main_menu()
