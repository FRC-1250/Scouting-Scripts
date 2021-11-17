import configparser
import os
import requests

# Build path the configuration files for windows and linux
absolutepath = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
configpath = os.path.join(absolutepath, 'config.ini')

# Read configuration from config.ini
config = configparser.ConfigParser()
config.read(configpath)
token = config['api']['X-TBA-Auth-Key']
listOfTeams = config['inputs']['teams'].split(',')

# Create a headers parameter so we can authenticate against the blue alliance API
headers = {'X-TBA-Auth-Key': token, 'accept':'application/json'}

for team in listOfTeams:
  urlTeamEventsAllTime = f'https://www.thebluealliance.com/api/v3/team/{team}/events'
  teamEventsResponseJson = requests.get(url=urlTeamEventsAllTime, headers=headers).json()
  simpleEventList = []

  for teamEvent in teamEventsResponseJson:
    simpleEvent = {
      'event_code' : teamEvent['key'],
      'week': teamEvent['week'],
      'year': teamEvent['year']
    }
    simpleEventList.append(simpleEvent)

  for event in simpleEventList:
    urlTeamMatchesPerEvent = f'https://www.thebluealliance.com/api/v3/team/{team}/event/{event["event_code"]}/matches/simple'
    teamMatchesResponseJson = requests.get(url=urlTeamMatchesPerEvent, headers=headers).json()
    teamScoreAverage = 0

    for teamMatch in teamMatchesResponseJson:
      blue = teamMatch['alliances']['blue']
      red = teamMatch['alliances']['red']
      if team in blue['team_keys']:
        teamScoreAverage = teamScoreAverage + blue['score']
      elif team in red['team_keys']:
        teamScoreAverage = teamScoreAverage + red['score']
    try:
      # Just in case of bad data and the response is empty, fail gracefully!
      teamScoreAverage = teamScoreAverage / len(teamMatchesResponseJson)
    except Exception as err:
      print(f'{err} -- {team}_{event["event_code"]}')
      continue

    urlAllMatchesPerEvent = f'https://www.thebluealliance.com/api/v3/event/{event["event_code"]}/matches/simple'
    allMatchesResponseJson = requests.get(url=urlAllMatchesPerEvent, headers=headers).json()
    eventScoreAverage = 0
    
    for eventMatch in allMatchesResponseJson:
      eventScoreAverage = eventScoreAverage + eventMatch['alliances']['red']['score']
      eventScoreAverage = eventScoreAverage + eventMatch['alliances']['blue']['score']
    try:
      # Just in case of bad data and the response is empty, fail gracefully!
      eventScoreAverage = eventScoreAverage / (len(allMatchesResponseJson) * 2)
    except Exception as err:
      print(f'{err} -- {team}_{event["event_code"]}')
      continue

    print(f'Team: {team}, Event code: {event["event_code"]}, Year: {event["year"]}, Week: {event["week"]}, Team Average Score: {teamScoreAverage}, Event Average Score: {eventScoreAverage}')