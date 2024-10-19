import requests
import json

URL = "https://event.withhive.com/ci/smon/evt_coupon/useCoupon"

HEADERS = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "en-US,en;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
    "cache-control": "no-cache",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "pragma": "no-cache",
    "sec-ch-ua": "\"Google Chrome\";v=\"129\", \"Not=A?Brand\";v=\"8\", \"Chromium\";v=\"129\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-requested-with": "XMLHttpRequest",
    "Referer": "https://event.withhive.com/ci/smon/evt_coupon",
    "Referrer-Policy": "strict-origin-when-cross-origin"
}

def fetch(id: str, code: str):
    """Make a request to use a coupon code

    Args:
        id (str): Hive ID
        code (str): Coupon code

    Returns:
        Tuple[int, dict]: Status code and response json \n
        (int, {"retCode": int|str, "retMsg": str})

    retCodes:
        100 - success
        304 - already used (changed from (H304) - str)
        306 - invalid code (changed from (H306) - str)
        404 - URL not found (custom)
        503 - invalid HiveID
    """
    try:
        body = f"country=US&lang=en&server=europe&hiveid={id}&coupon={code}"
        response = requests.post(URL, headers=HEADERS, data=body)
        rJson = response.json()
        
        # Removing (H) from retCode
        if type(rJson["retCode"]) == str: # Avoid error if retCode is int
            rJson["retCode"] = rJson["retCode"].translate(str.maketrans({"(": "", ")": "", "H": ""}))

        # Getting the first line of retMsg
        rJson["retMsg"] = str(rJson["retMsg"]).split("<br/>")[0]

        return response.status_code, rJson
    except Exception as e:
        return 404, {"retCode": 404, "retMsg": "URL not found"}


DB = "./db/ids.json"

def multiFetch(code: str) -> str|tuple:
    """Make a request to use a coupon code for multiple users

    Args:
        code (str): Coupon code

    Returns:
        dict: {id: (status code, response json)}
    """
    try:
        with open(DB, "r") as f: 
            db: dict = json.load(f)
    except FileNotFoundError:
        return "No registered IDs"
    
    ids = list(db.keys())

    errors = []
    noErrors: int = 0
    for id in ids:
        rCode, resp = fetch(id, code)
        if rCode == 404 or resp["retCode"] == 404:
            return "URL not found, contact the developer"
        if rCode != 200:
            return "Unknown error, contact the developer"
        if resp["retCode"] == 306:
            return "Invalid code, it might be expired, invalid or usage limit reached"
        else:
            if resp["retCode"] == 304:
                errors.append(f"<@{db[id]}> already used the code.")
            
            elif resp["retCode"] == 503:
                errors.append(f"<@{db[id]}> has registered an invalid Hive ID.")

            elif resp["retCode"] == 100:
                noErrors += 1

            else:
                errors.append(f"<@{db[id]}> has encountered an unknown error.")

    response = f"{noErrors} users successfully used the code." if noErrors > 1 else f"{noErrors} user successfully used the code." if noErrors == 1 else "No users successfully used the code."
    if errors:
        response += f"\n\n {len(errors)} users got an error:" if len(errors) > 1 else f"\n\n {len(errors)} user got an error:"
        return response, errors
    return response

if __name__ == "__main__":
    print(multiFetch("SW2022FEB21"))