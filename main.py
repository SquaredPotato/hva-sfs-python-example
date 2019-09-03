from api.amsterdam_api import AmsterdamApi
from api.ns_api import NSApi

def trash_bins():
    amsterdam_api = AmsterdamApi()

    req = 'A'

    while req != 'M' and req != 'T':
        req = input("Do you want a list of trash bins or monuments? Enter T or M:")

    if req == 'T':
        list_trash_bins = amsterdam_api.get_trash_bins()

        print("Overview of trash bins in Amsterdam")

        for trash_bin in list_trash_bins:
            print(
                str(trash_bin['id']) + "\t" +
                trash_bin['name'] + "\t" +
                trash_bin['type'] + "\t" +
                trash_bin['address']
            )
    else:
        print("Overview of monuments in Amsterdam")

        list_monuments = amsterdam_api.get_monuments()

        for monument in list_monuments:
            print(
                str(monument['id']) + "\t" +
                monument['address']
            )

def main():
    print("NS API Test")
    ns_api = NSApi()

    # Get a list of train stations
    #print(ns_api.get_train_stations())

    # Get a list of disruptions
    #print(ns_api.get_disruptions())

    # Get all the departure trains from one train station (direction and delay in seconds)
    # Use id from get_train_stations() as identifier.
    #print(ns_api.get_departures("8400057"))


if __name__ == "__main__":
    main()

