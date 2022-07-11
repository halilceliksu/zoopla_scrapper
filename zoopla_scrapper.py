# IMPORT MODULES
import math
import json
import datetime
import csv
import requests
from bs4 import BeautifulSoup


headers={
	'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0'
	}

class ZooplaScrapper:
    def __init__(self,url):
        # create the result sheet
        now = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
        self.filename = "%s.csv" % now
        self.file_details = open("%s" % self.filename,"w",encoding='UTF-8')
        self.writer_details = csv.writer(self.file_details, delimiter=",",lineterminator="\n")
        # insert the headers
        self.writer_details.writerow([
            "Property ID",
            "Property Title",
            "Property Published Date",
            "Bed",
            "Bath",
            "Price",
            "Address",
            "Distances",
            "Property Link"
            ])
        self.base_url = "https://www.zoopla.co.uk"
        self.url = url
        self.get_general_info()

    # gets general info from the listing pages
    def get_general_info(self):
        print(self.url)
        site = requests.get(self.url, headers=headers).text
        soup = BeautifulSoup(site, "html.parser")
        # there is a hidden json data inside of the html
        properties_json = soup.find("script", {"type": "application/json"})
        json_data = json.loads(properties_json.text)
        listings = json_data["props"]["pageProps"]["initialProps"]["regularListingsFormatted"]
        for listing in listings:
            listing_id = listing["listingId"]
            listing_title = listing["title"]
            listing_published_on = listing["publishedOn"]
            
            bed = ""
            bath = ""
            listing_features = listing["features"]
            for feature in listing_features:
                if feature["iconId"] == "bed":
                    bed = feature["content"]
                elif feature["iconId"] == "bath":
                    bath = feature["content"]
            
            transport_dict = {}
            listing_transports = listing["transports"]
            for transport in listing_transports:
                transport_dict[transport["title"]] = transport["distanceInMiles"]
            
            listing_price = listing["price"]
            listing_address = listing["address"]

            listing_uris = listing["listingUris"]
            listing_link = "https://www.zoopla.co.uk" + listing_uris["detail"]
            
            self.writer_details.writerow([
                listing_id,
                listing_title,
                listing_published_on,
                bed,
                bath,
                listing_price,
                listing_address,
                str(transport_dict),
                listing_link
                ])
            self.file_details.flush()
            print([
                listing_id,
                listing_title,
                listing_published_on,
                bed,
                bath,
                listing_price,
                listing_address,
                str(transport_dict),
                listing_link
                ])
                    
        pagination = json_data["props"]["pageProps"]["initialProps"]["searchResults"]["pagination"]
        total_results = pagination["totalResults"]
        current_pagination = int(pagination["pageNumber"])
        total_paginations = math.ceil(int(total_results)/25)
        
        if int(current_pagination) < total_paginations:
            self.url = self.url.split("pn=")[0] + "pn=" + str(current_pagination + 1)
            self.get_general_info()


# this is a test line to test it.
if __name__ == "__main__":
    ZooplaScrapper("https://www.zoopla.co.uk/for-sale/property/london/?q=london&results_sort=newest_listings&search_source=home")