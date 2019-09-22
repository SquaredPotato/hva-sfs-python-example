from api.amsterdam_api import AmsterdamApi
from api.ns_api import NSApi
from collections import defaultdict
from dataclasses import dataclass
from itertools import islice
import operator


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


# Store departures per station lookup to slightly reduce load on NS's API (memory heavy)
class DepCache:
	departures = dict()  # Departures
	stations = defaultdict(list)  # Departures sorted per station
	totalCalls = 0
	fromAPI = 0

	def __init__(self, ns_api):
		self.ns_api = ns_api

	def get(self, station_id):
		self.totalCalls += 1
		if station_id not in self.stations:
			self.fromAPI += 1
			res = self.ns_api.get_departures(station_id)

			if res is not None:
				# Store returned departures, and append departure ID to stations given in departures 'stations' list
				for a in res:
					if a['id'] not in self.departures:
						self.departures.update({a['id']: a})

					if a['id'] not in self.stations[station_id]:
						self.stations[station_id].append(a['id'])

					for b in a['stations']:
						if a['id'] not in self.stations[station_id]:
							self.stations[b].append(a['id'])
			else:  # Station departures not available through NS API
				return None

		res = dict()

		if station_id in self.stations:
			for a in self.stations[station_id]:
				res.update({a: self.departures[a]})
		else:
			return None

		return res


class StationData:
	delays: int = 0
	totalDelay: int = 0
	disrupted: int = 0
	departures = list()
	name: str = ""

	def __init__(self, delays=0, totaldelay=0, disrupted=0, name=""):
		self.delays = delays
		self.totalDelay = totaldelay
		self.disrupted = disrupted
		self.name = name

	def __repr__(self):
		return self.name + "-> Disrupts: " + str(self.disrupted)

	def getdelays(self) -> int:
		return self.delays

	def gettotaldelay(self) -> int:
		return self.totalDelay

	def getdisrupts(self) -> int:
		return self.disrupted


def main():
	print("NS API Test")
	ns_api = NSApi()

	cache = DepCache(ns_api)

	# Get stations and disruptions
	stations = ns_api.get_train_stations()
	disruptions = ns_api.get_disruptions()

	print(stations)
	print(disruptions)

	# key: station id
	dstations = dict()

	# Create a lookup table of just codes and ids for use later on
	ids = dict()
	cod = dict()

	for a in stations:
		ids.update({str(a['code']).lower(): a['id']})
		cod.update({a['id']: str(a['code']).lower()})

	# Create list of impacted stations with counts
	for a in disruptions:
		for b in a['stations']:
			# Update count
			if b not in dstations:
				for c in stations:  # Lookup station name
					if c['code'] == str(b).upper():
						dstations.update({b: StationData(disrupted=1, name=c['name'])})
						break
			else:
				dstations[b].disrupted += 1

	sorted_dstations = sorted(dstations.values(), key=StationData.getdisrupts, reverse=True)

	print("percentage of disrupted stations: " + str(len(dstations) / len(stations) * 100) + "%\n\nTop 10:\n")

	for i in range(0, min(len(dstations), 10)):
		print(i + 1, ": ", sorted_dstations[i].name, " - ", sorted_dstations[i].disrupted)

	del dstations
	dstations = dict()

	for a in stations:  # Loop through all stations
		departures = cache.get(a['id'])
		# get() returns None when the station is outside the NL
		if departures is not None:
			for b in departures:
				# Somehow not all departures have a station
				if len(departures[b]['stations']) > 0:
					for c in departures[b]['stations']:
						delay_seconds = int(departures[b]['delay_seconds'])
						if delay_seconds > 0:
							if c in dstations:  # Update delay count
								dstations[c].delays += 1
								dstations[c].totalDelay += delay_seconds
							else:
								for d in stations:  # Lookup station name
									if d['id'] == str(c):
										dstations.update(
											{c: StationData(name=d['name'], delays=1, totaldelay=delay_seconds)})
										break

	sorted_dstations = sorted(dstations.values(), key=StationData.getdelays, reverse=True)
	print("Stations with most delays: ")
	for i in range(0, min(len(dstations), 10)):
		print(i + 1, ": ", sorted_dstations[i].name, " - ", sorted_dstations[i].delays)

	sorted_dstations = sorted(dstations.values(), key=StationData.gettotaldelay, reverse=True)
	print("Stations with longest delays: ")
	for i in range(0, min(len(dstations), 10)):
		print(i + 1, ": ", sorted_dstations[i].name, " - ", sorted_dstations[i].totalDelay)

	print("total station lookups: ", str(cache.totalCalls), " from which ", str(cache.totalCalls - cache.fromAPI),
		  " came from cache - ", str((cache.totalCalls - cache.fromAPI) / cache.totalCalls * 100), "% from cache")


if __name__ == "__main__":
	main()
