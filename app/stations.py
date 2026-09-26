"""A small reference set of real Indian Railways station codes.

Not exhaustive — this is a sample reel of stations we can vouch for, the
same way Meera only trusted notices she could actually read. Unknown codes
are not auto-rejected outright; they're accepted if they *look* like a
station code (2-5 uppercase letters) but flagged with lower confidence isn't
needed for this contest, so we keep the rule simple: valid format + presence.
"""

KNOWN_STATION_CODES = {
    "NDLS": "New Delhi",
    "CSMT": "Mumbai CSMT",
    "PUNE": "Pune Junction",
    "CSTM": "Mumbai CST",
    "HWH": "Howrah Junction",
    "MAS": "Chennai Central",
    "SBC": "Bengaluru City",
    "ADI": "Ahmedabad Junction",
    "PNBE": "Patna Junction",
    "LKO": "Lucknow Junction",
    "JP": "Jaipur Junction",
    "BCT": "Mumbai Central",
    "KOAA": "Kolkata",
    "GHY": "Guwahati",
    "SC": "Secunderabad Junction",
    "NGP": "Nagpur Junction",
    "BZA": "Vijayawada Junction",
    "ERS": "Ernakulam Junction",
    "ASR": "Amritsar Junction",
    "CDG": "Chandigarh",
}
