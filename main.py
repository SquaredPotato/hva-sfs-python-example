from api.amsterdam_api import AmsterdamApi
from api.ns_api import NSApi
import json


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

    # Get stations and disruptions
    stations = ns_api.get_train_stations()
    disruptions = ns_api.get_disruptions()

    print(stations)
    print(disruptions)

    # key: station code, 0: number of times encountered in disruptions list, 1: total counted delay for station
    dstations = dict()

    # Create a lookup table for easy conversion later on
    ids = dict()
    for a in stations:
        ids.update({str(a['code']).lower(): a['id']})

    # Create list of impacted stations with counts
    for a in disruptions:
        for b in a['stations']:
            # Update count
            if b not in dstations:
                dstations.update({b: [1, 0]})
            else:
                old = dstations[b][0]
                dstations.update({b: [(old + 1), 0]})

            departures = ns_api.get_departures(ids[b])
            print(departures)

    print("percentage of affected stations: " + str(len(dstations) / len(stations) * 100) + "%\n")

    # Get all the departure trains from one train station (direction and delay in seconds)
    # Use id from get_train_stations() as identifier.
    print(ns_api.get_departures("8400045"))


if __name__ == "__main__":
    main()
