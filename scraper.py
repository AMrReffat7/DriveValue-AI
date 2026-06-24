import requests
from bs4 import BeautifulSoup
import csv
from time import sleep
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

total_counter = 0


# Function to create a session with retry mechanism
def create_session():
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))
    session.mount("http://", HTTPAdapter(max_retries=retries))
    return session


# Open a CSV file in write mode
with open(
    "./data/hatla2ee_scraped_data.csv", "w", newline="", encoding="utf-8"
) as csvfile:
    # Define fieldnames for the CSV file
    fieldnames = [
        "Name",
        "Price",
        "Color",
        "Mileage",
        "Make",
        "Model",
        "City",
        "Date Displayed",
        "Automatic Transmission",
        "Air Conditioner",
        "Power Steering",
        "Remote Control",
        "Item URL",
    ]

    # Initialize a CSV writer object
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # Write the header row
    writer.writeheader()

    session = create_session()

    for i in range(1, 1000):
        url = f"https://eg.hatla2ee.com/en/car/page/{i}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }

        try:
            # Send a GET request to the URL using the session
            response = session.get(url, headers=headers)
            response.raise_for_status()  # Raises HTTPError for bad responses

            # Parse the HTML content
            soup = BeautifulSoup(response.content, "html.parser")

            # Find all car cards
            car_cards = soup.find_all("div", class_="newCarListUnit_contain")
            if not car_cards:
                break

            counter = 0

            # Iterate over each car card
            for card in car_cards:
                car_data = {
                    "Name": None,
                    "Price": None,
                    "Color": None,
                    "Mileage": None,
                    "Make": None,
                    "Model": None,
                    "City": None,
                    "Date Displayed": None,
                    "Automatic Transmission": "No",
                    "Air Conditioner": "No",
                    "Power Steering": "No",
                    "Remote Control": "No",
                    "Item URL": None,
                }

                try:
                    car_data["Name"] = card.find(
                        "div", class_="newCarListUnit_header"
                    ).text.strip()
                except AttributeError:
                    pass

                try:
                    car_data["Price"] = card.find(
                        "div", class_="main_price"
                    ).text.strip()
                    if car_data["Price"] == "-":
                        car_data["Price"] = None
                except AttributeError:
                    pass

                try:
                    meta_tags = card.find_all("span", class_="newCarListUnit_metaTag")
                    car_data["Color"] = meta_tags[0].text.strip()
                    car_data["Mileage"] = meta_tags[-1].text.strip()
                    if car_data["Mileage"] == "- Km":
                        car_data["Mileage"] = None
                except (AttributeError, IndexError):
                    pass

                try:
                    meta_links = card.find(
                        "div", class_="newCarListUnit_metaTags"
                    ).find_all("span", class_="newCarListUnit_metaLink")
                    car_data["Make"] = meta_links[0].text.strip()
                    car_data["Model"] = meta_links[1].text.strip()
                    car_data["City"] = meta_links[-1].text.strip()
                except (AttributeError, IndexError):
                    pass

                try:
                    car_data["Date Displayed"] = (
                        card.find("div", class_="otherData_Date")
                        .find("span")
                        .text.strip()
                    )
                except AttributeError:
                    pass

                try:
                    icons_element = card.find("div", class_="otherData_carType")
                    if icons_element.find("i", {"title": "Automatic"}):
                        car_data["Automatic Transmission"] = "Yes"
                    if icons_element.find("i", {"title": "Air Conditioner"}):
                        car_data["Air Conditioner"] = "Yes"
                    if icons_element.find("i", {"title": "Power Steering"}):
                        car_data["Power Steering"] = "Yes"
                    if icons_element.find("i", {"title": "Remote Control"}):
                        car_data["Remote Control"] = "Yes"
                except AttributeError:
                    pass

                try:
                    car_data["Item URL"] = (
                        f"https://eg.hatla2ee.com{card.find('div', class_='newMainImg').find('a').get('href')}"
                    )
                except AttributeError:
                    pass

                # Write the row to the CSV file
                writer.writerow(car_data)
                counter += 1

            print(f"***** Page {i} Scrapped Successfully with {counter} Items *****")
            total_counter += counter
            sleep(5)
        except requests.RequestException as e:
            print(f"Error occurred while scraping page {i}: {e}")
            sleep(30)

print(f"\n***** Total Number of the Scrapped Items is {total_counter} *****\n")
