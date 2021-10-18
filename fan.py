#!/bin/python3

"""
Simple object used to scrape team schedules and text a defined end user

IRF
"""

# ----- Imports
import pandas as pd
import datetime, json, random
from twilio.rest import Client


# ----- Definitions
class Fan:
      def __init__(self, TEAM_ABBREV, PHONE):

            # Hard-coded teams ... could be changed with a modicum of effort
            if TEAM_ABBREV == "NYK":
                  self.team_name = "New York Knicks"
                  self.team_abbreviation = TEAM_ABBREV
                  self.url = "https://www.basketball-reference.com/teams/NYK/2022_games.html"
                  self.hype = random.choice(["KING RANDLE SZN",
                                            "KEMBA TIME",
                                            "THIBIDOU TIME",
                                            "THE DERRICK ROSE RENNAISANCE"])


            elif TEAM_ABBREV == "POR":
                  self.team_name = "Portland Trailblazers"
                  self.team_abbreviation = TEAM_ABBREV
                  self.url = "https://www.basketball-reference.com/teams/POR/2022.html"
                  self.hype = random.choice(["DAME TIME",
                                            "THE ROSE CITY RENNAISANCE"])

            self.delivery_phone_number = PHONE                                      # End user's phone number
            self.today = datetime.datetime.strftime("%Y-%m-%d")                     # Today in "YEAR-MONTH-DAY" format

            twilio_info = self._get_twilio_setup()                                  # Dictionary with Twilio information

            self.recovery = twilio_info["recovery"]
            self.sid = twilio_info["sid"]
            self.auth = twilio_info["auth"]
            self.phone_number = twilio_info["my_number"]


      def _get_twilio_setup(self):
            """
            Reads in external JSON file with Twilio API info

            Returns dictionary
            """

            with open('./twilio.json') as incoming:
                  twil_info = json.load(incoming)

            return twil_info


      def scrape_games(self):
            """
            Scrapes team schedule from Basketball Reference

            Returns Pandas DataFrame object
            """

            sched = pd.read_html(self.url)[0]                                       # Read in HTML as DataFrame
            sched = sched[sched['Date'] != 'Date'].reset_index(drop=True)           # Drop filler rows
            sched = sched.loc[:, ['Date', 'Start (ET', 'Opponent']]                 # Isolate columns of interest

            # Convert date values to standard format
            sched['Date'] = sched['Date'].apply(lambda x: datetime.datetime.strptime(x, "%a, %b %d, %Y"))

            # Match game times with today's date, if applicable
            sched = sched[sched['Date'] == self.today]

            return sched


      def build_messages(self, opponent, time):
            """
            Simple string to use as body of text message
            """

            return "IT'S {}!\n\nTONIGHT @ {}: {} x {}\n\nLET'S GO {}".format(self.hype, time,
                                                                              self.team_name, opponent, 
                                                                              self.team_abbreviation.upper())


      def send_text(self):
            """
            Wraps the functions above
            Sends an SMS text with Twilio's rest API 
            """

            auth = Client(self.sid, self.auth)                                      # Instantiate API Client
            gameday = self.scrape_games().reset_index(drop=True)                    # Read in game times

            # No text on off days
            if len(gameday) == 0:
                  print(f"No game today for the {self.team_name}")

            # If there's a game tonight, send the end user a text
            else:
                  opponent = gameday['Opponent'][0]
                  start_time = gameday['Start (ET)'][0].replace('0p', '0 PM EST')
                  message = self.build_messages(opponent=opponent, time=start_time)

                  auth.messages.create(body=message, to=self.delivery_phone_number, from_=self.phone_number)



