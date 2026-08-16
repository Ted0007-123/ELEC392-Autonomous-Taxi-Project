# THIS FILE CONTAINS GLOBAL vpfs INFO
# Along with a couple basic functions, add more as used

import json
from urllib import request

# Server details will change between lab, home, and competition, so saving them somehwere easy to edit
server_ip = "192.168.0.100"#"?.?.?.?"
server = f"http://{server_ip}:5000"
authKey = "562a754f445dd32c5a39ad7c9b1eb75c"#"my_auth_key"  # For the lab, your auth key is your team number, at competition this will be a secret key
team = 7      


# GENERAL FUNCTIONS_____________________________________________________________________

def vpfs_match():#Match and server status
    """
    # /match?auth=<auth> payload
{
    "mode": "home" | "lab" | "match",   # Current server mode
    "match": int,           # Current match number
    "matchStart": bool,     # Whether the match has started
    "timeRemain": float,    # Match time remaining, negative when match has ended
    "team": int,            # Your team number, if it's wrong then authentication failed
    "inMatch": bool,        # True if your team is competing in the current match
}"""
    res = request.urlopen(server + f"/match?auth={authKey}", timeout=10)
    if res.status == 200:
        # decode JSON data
        data = json.loads(res.read())
        return data

##########################################################################################
def vpfs_fares(): #List of active fares
    """# /fares payload
[
  {
    "id": int,          # ID of the fare, used to claim it
    "modifiers": int    # Modifiers which apply to the fare. 0=Normal Fare, 1=Subsized Fare, 2=Senior Fare
    "src": {            # Ducky pickup location, in meters from map origin
      "x": float,
      "y": float
    },
    "dest": {           # Ducky dropoff location, in meters from map origin
      "x": float,
      "y": float,
    },
    "claimed": bool,    # True if the fare is already claimed
    "expiry": float,    # Fare expiry, cannot be claimed after this time. In UTC seconds, see python time.time()
    "pay": float,       # Fare payout
    "reputation": int   # Fare reputation gain, in %
  }
]"""
    res = request.urlopen(server + f"/fares?all=False", timeout=5)
    # print(res.status)
    if res.status == 200:
        # decode JSON data
        data = json.loads(res.read())
        # print(f"[VPFS] {data}")
        return data

##########################################################################################
def vpfs_fares_claim(ID): #Claim a fare of ID
    """# /fares/claim/<idx>?auth=<auth> payload
[
  {
    "success": bool,    # True if fare was claimed successfully, false if not
    "message": str      # Description of why claim failed, if applicable
  }
]"""
    res = request.urlopen(server + f"/fares/claim/{ID}?auth={authKey}", timeout=10)
    if res.status == 200:
        # decode JSON data
        data = json.loads(res.read())
        return data

##########################################################################################
def vpfs_fares_drop(ID): #drop Claimed a fare of ID
    """# /fares/drop/<idx>?auth=<auth> payload
[
  {
    "success": bool,    # True if fare was dropped successfully, false if not
    "message": str      # Description of why drop failed, if applicable
  }
]"""
    res = request.urlopen(server + f"/fares/drop/{ID}?auth={authKey}", timeout=10)
    if res.status == 200:
        # decode JSON data
        data = json.loads(res.read())
        return data

##########################################################################################
def vpfs_fares_current():  # Find teams current fares info
    """# /fares/current/<team>?auth=<auth> payload
[
  {
    "fare": {               # Fare information, using extended version of /fares endpoint. None if team does not have an active fare
        "id": int,          # ID of the fare, used to claim it
        "modifiers": int    # Modifiers which apply to the fare. 0=Normal Fare, 1=Subsized Fare, 2=Senior Fare
        "src": {            # Ducky pickup location, in meters from map origin
            "x": float,
            "y": float
        },
        "dest": {           # Ducky dropoff location, in meters from map origin
         "x": float,
         "y": float,
        },
        "claimed": bool,    # True if the fare is already claimed
        "expiry": float     # Fare expiry, cannot be claimed after this time. In UTC seconds, see python time.time()
        "pay": float,       # Fare payout
        "reputation": int,  # Fare reputation gain, in %
        "active": bool,     # Whether the fare is active (available/in-progress) or not. Should be True until completion
        "team": int,        # Team which claimed the fare
        "inPosition": bool, # True when the team is close enough to the dropoff point and timer is running
        "pickedUp": bool,   # True when the fare is successfully picked up
        "completed": bool,  # True when the fare is successfully dropped off
        "paid": bool        # True when the fare has been paid out
    } | None,
    "message": str          # Description of why claim failed, if applicable
  }
]"""
    res = request.urlopen(server + f"/fares/current/{team}?auth={authKey}", timeout=10)
    if res.status == 200:
        # decode JSON data
        data = json.loads(res.read())
        return data

##########################################################################################
def vpfs_team_status():  # Find teams rep and money
    """# /teams/status/<team>?auth=<auth> payload
[
  {
    "message": str      # Description of any failure reason, if applicable
    "status": {
        "money": float,       # Current money
        "reputation": float,  # Current reputation
        "team": int           # Team id
    } | None
  }
]"""
    res = request.urlopen(server + f"/fares/status/{team}?auth={authKey}", timeout=10)
    if res.status == 200:
        # decode JSON data
        data = json.loads(res.read())
        return data


##########################################################################################
def vpfs_whereami():  # Find teams location (heading , x , y)
    """# /WhereAmI/<team> payload
[
  {
    "position": {
      "heading": float  # Vehicle's heading with respect to the map x-axis in radians
      "x": float,  # Vehicle's x position, in meters relative to map origin
      "y": float   # Vehicle's y position, in meters relative to map origin
    },
    "last_update": int  # Unix timestamp of when the position was recorded, see Python's time.time()
    "message": str      # Description of why the claim failed, if applicable
  }
]"""
    res = request.urlopen(server + f"/whereami/{team}?auth={authKey}", timeout=10)
    if res.status == 200:
        # decode JSON data
        data = json.loads(res.read())
        # print(data)
        return data