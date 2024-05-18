import googlemaps

def search_store_by_name(store_name):
    store_name = str(store_name).lower()
    if "masterCard - pagamento" in store_name:
        store_name = store_name.replace("masterCard - pagamento", "")
    # Initialize the Google Maps client
    gmaps = googlemaps.Client(key="AIzaSyBkNTALVOFt_g0TFHNyHoEj-ZSk2CPGCHg")
    # Perform a text-based search for the store name
    places = gmaps.places(store_name)

    # categories
    categories = {
        "Rent" : ["stock house sas", "affitto", "soperga"],
        "Food" : ["pellegrini", "politecnico di milano", "bar", 'cafe', 'restaurant', 'food','supermarket', 'grocery_or_supermarket', 'bakery', "esselunga"],
        "Health" : ['health', 'pharmacy', 'dentist', 'diva parrucchiere'],
        "Bills and Taxes" : ["iliad", "a2a", "vodafone"],
        "Clothing" : ["clothing_store", 'shoe_store'],
        "Entertainment" : ['book_store', 'movie_rental', 'amazon', 'bowling_alley'],
        "Transportation" : ['travel_agency', 'trenitalia', 'atm'],
        "Household" : ['furniture_store', 'home_goods_store', 'laundry']
    }

    # Check if any results are returned
    if places['status'] == 'OK':
        # Retrieve details of the first place (assuming the most relevant)
        result = places['results'][0]['types']
        res = { category : 0 for category in categories.keys()}
        for category_key, category_values in categories.items():
            for cat in category_values:
                if store_name in cat or cat in store_name:
                    return category_key
                for res_str in result:
                    if cat in res_str:
                        res[category_key] += 1

        max = sorted(res.items(), key=lambda item: item[1], reverse=True)[0]
        if max[1] > 0:
            return max[0]
        return "Other"


    else:
        for category_key, category_values in categories.items():
            for cat in category_values:
                if cat in store_name:
                    return category_key
        return "Other"


if __name__ == "__main__":
    store_name = 'Esselunga'

    print(search_store_by_name( store_name))