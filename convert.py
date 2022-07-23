#!/usr/bin/env python3
"""Converts between the HealthMate data export files and gpx."""

import csv
from datetime import datetime
import pytz
import gpxpy
import gpxpy.gpx

LATITUDE_FILE = 'raw_location_latitude.csv'
LONGITUDE_FILE = 'raw_location_longitude.csv'
ALTITUDE_FILE = 'raw_location_altitude.csv'
SPEED_FILE = 'raw_location_gps-speed.csv'

ACTIVITY_FILE = 'activities.csv'

FROM_COL = 0
TO_COL = 1
TIMEZONE_COL = 4
TYPE_COL = 5

RAW_TIME_COL = 0
RAW_LOCATION_COL = 2


class Activity:
    """Generic Activity holder"""

    WHITHINGS_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"

    def __init__(self, start, stop, activity_type, zone):
        self.start = datetime.strptime(start, self.WHITHINGS_TIME_FORMAT)
        self.stop = datetime.strptime(stop, self.WHITHINGS_TIME_FORMAT)
        self.activity_type = activity_type
        self.timezone = pytz.timezone(zone)
        self.has_points = False
        self.gpx = gpxpy.gpx.GPX()

        gpx_track = gpxpy.gpx.GPXTrack()
        self.gpx.tracks.append(gpx_track)

        # Create first segment in our GPX track:
        self.gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(self.gpx_segment)

    def add(self, time, lats, lons, alts, speeds):
        """Add a GPS Location to the activity"""

        location_time = datetime.strptime(
            time, self.WHITHINGS_TIME_FORMAT).astimezone(self.timezone)
        if self.start <= location_time <= self.stop:
            self.has_points = True

            lats = eval(lats, {})
            lons = eval(lons, {})
            alts = eval(alts, {})
            speeds = eval(speeds, {})
            for idx, lat in enumerate(lats):
                lon = lons[idx]
                alt = alts[idx]
                speed = speeds[idx]
                print(f"Adding {lat}, {lon} to activity at {self.start}")
                self.gpx_segment.points.append(
                    gpxpy.gpx.GPXTrackPoint(lat,
                                            lon,
                                            elevation=alt,
                                            speed=speed,
                                            time=location_time))
            return True
        return False

    def save(self, name=None):
        """Save the GPX file"""

        if not name:
            name = f"{self.start}.gpx"

        if self.has_points:
            with open(name, "w") as outfile:
                outfile.write(self.gpx.to_xml())


def main():
    """Main entry point"""
    all_activities = []
    with open(ACTIVITY_FILE, newline='', encoding="utf-8") as activityfile:
        activities = csv.reader(activityfile, delimiter=',', quotechar='"')
        next(activities, None)  # skip the headers
        for row in activities:
            activity = Activity(row[FROM_COL], row[TO_COL], row[TYPE_COL],
                                row[TIMEZONE_COL])
            all_activities.append(activity)

    with open(LATITUDE_FILE, newline='', encoding="utf-8") as latfile, open(
            LONGITUDE_FILE, newline='', encoding="utf-8") as lonfile, open(
                ALTITUDE_FILE, newline='', encoding="utf-8") as altfile, open(
                    SPEED_FILE, newline='', encoding="utf-8") as speedfile:
        lats = csv.reader(latfile, delimiter=',', quotechar='"')
        lons = csv.reader(lonfile, delimiter=',', quotechar='"')
        alts = csv.reader(altfile, delimiter=',', quotechar='"')
        speeds = csv.reader(speedfile, delimiter=',', quotechar='"')

        next(lats, None)  # skip the headers
        next(lons, None)  # skip the headers
        next(alts, None)  # skip the headers
        next(speeds, None)  # skip the headers

        for row_lat in lats:
            row_lon = next(lons)
            row_alt = next(alts)
            row_speed = next(speeds)

            for activity in all_activities:
                if activity.add(row_lat[RAW_TIME_COL],
                                row_lat[RAW_LOCATION_COL],
                                row_lon[RAW_LOCATION_COL],
                                row_alt[RAW_LOCATION_COL],
                                row_speed[RAW_LOCATION_COL]):
                    break

    for activity in all_activities:
        activity.save()


if __name__ == "__main__":
    main()
