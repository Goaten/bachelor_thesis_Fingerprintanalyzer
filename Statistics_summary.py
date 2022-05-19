import json
from unicodedata import category


def get_json_data(path):
    # Read json data that tells what and how to extract data
    with open(path, "r") as json_file:
        data = json.load(json_file)

    return data

def get_distribution(data, browser, pv):
    distribution = []
    for category in data[browser][pv]:
        for attribute in data[browser][pv][category]:
            if "Media Devices" in attribute:
                continue
            a = data[browser][pv][category][attribute]
            
            found = False
            for d in distribution:
                if a["unique"] == d["unique"]:
                    d["num"] += 1
                    found = True
            if not found:
                distribution.append({
                    "unique": a["unique"],
                    "num": 1
                })
    return distribution



def main():
    data = get_json_data(".\\results\\statistics.json")

    distribution = {}

    for browser in data:
        distribution[browser] = {}
        for pv in data[browser]:
            distribution[browser][pv] = get_distribution(data, browser, pv)
            
            print(browser, "-", pv)
            for d in distribution[browser][pv]:
                print(f"{d['unique']} (unique values): {d['num']} (ocurrances)")
            print("")


if __name__ == "__main__":
    main()