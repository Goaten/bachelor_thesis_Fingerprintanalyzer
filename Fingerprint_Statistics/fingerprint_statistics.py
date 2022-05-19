import os, json

def is_equal(v1, v2):
    if isinstance(v1, str) and isinstance(v2, str):
        return v1.strip() == v2.strip()

    if isinstance(v1, list) and isinstance(v2, list):
        if isinstance(v1[0], str):
            return sorted(v1) == sorted(v2)
        elif isinstance(v1[0], dict):
            for d in v1:
                if d not in v2:
                    return False
            return True


def get_json_data(path):
    # Read json data that tells what and how to extract data
    with open(path, "r") as json_file:
        data = json.load(json_file)

    return data


def total_num_elements(lst):
    sum = 0
    for e in lst:
        sum += e[0]
    return sum

def get_distribution_num(lst):
    newlst = []
    for e in lst:
        newlst.append(e[0])
    newlst.sort(reverse=True)
    return newlst


def genereate_statistics(statistics_raw):

    statistics = {
        "Chrome": {
            "PV1": {},
            "PV2": {}
        },
        "Edge": {
            "PV1": {},
            "PV2": {}
        },
        "Firefox": {
            "PV1": {},
            "PV2": {}
        }
    }

    for browser in statistics_raw:
        for pv in statistics_raw[browser]:
            for category in statistics_raw[browser][pv]:

                if category not in statistics[browser][pv]:
                    statistics[browser][pv][category] = {}

                for attribute in statistics_raw[browser][pv][category]:

                    a = statistics_raw[browser][pv][category][attribute]

                    statistics[browser][pv][category][attribute] = { # f"Number of unique elements: {len(a)}/{total_num_elements(a)} ({get_distribution_num(a)})"
                            "num_elements": total_num_elements(a),
                            "unique": len(a),
                            "distribution": get_distribution_num(a)
                        } 

    return statistics

def genereate_statistics_raw(fingerprint_paths):
    pointsystem = get_json_data(".\\Pointsystem\\pointsystem.json")

    statistics_raw = {
        "Chrome": {
            "PV1": {},
            "PV2": {}
        },
        "Edge": {
            "PV1": {},
            "PV2": {}
        },
        "Firefox": {
            "PV1": {},
            "PV2": {}
        }
    }

    for testCase in os.listdir(fingerprint_paths):
        for pv in os.listdir(os.path.join(fingerprint_paths, testCase)):
            for browser in os.listdir(os.path.join(fingerprint_paths, testCase, pv)):
                # path to browser
                path = os.path.join(fingerprint_paths, testCase, pv, browser)
                # for each fingerprint
                for f in os.listdir(path):              
                    fingerprint = get_json_data(os.path.join(path, f))

                    for category in fingerprint:
                        for attribute in fingerprint[category]:
                            try:
                                if pointsystem[category][attribute][0] == False:
                                    continue
                            except:
                                if attribute != "Media Devices":
                                    continue

                            value = fingerprint[category][attribute]


                            if attribute == "Media Devices":
                                for m in value:
                                    # Check if category exist within statistics.
                                    if category in statistics_raw[browser][pv]:
                                        # Check if attribute exist within statistics.
                                        for attr in ["Media Devices: label", "Media Devices: deviceId"]:
                                            attr_value = m[attr.split(":")[-1].strip()]
                                            if attr in statistics_raw[browser][pv][category]:
                                                found = False
                                                for a in statistics_raw[browser][pv][category][attr]:
                                                    if is_equal(attr_value, a[1]):
                                                        a[0] += 1
                                                        found = True
                                                        break
                                                if not found:
                                                    statistics_raw[browser][pv][category][attr].append([1, attr_value])
                                            else:
                                                statistics_raw[browser][pv][category][attr] = [[1, attr_value]]
                                        
                                    else:
                                        # Add category and add attribute
                                        statistics_raw[browser][pv][category] = {}
                                        statistics_raw[browser][pv][category]["Media Devices: label"] = [[1, m['label']]]
                                        statistics_raw[browser][pv][category]["Media Devices: deviceId"] = [[1, m['deviceId']]]
                                    
                            else:
                                # Check if category exist within statistics.
                                if category in statistics_raw[browser][pv]:
                                    # Check if attribute exist within statistics.
                                    if attribute in statistics_raw[browser][pv][category]:
                                        found = False
                                        for a in statistics_raw[browser][pv][category][attribute]:
                                            if is_equal(value, a[1]):
                                                a[0] += 1
                                                found = True
                                                break
                                        if not found:
                                            statistics_raw[browser][pv][category][attribute].append([1, value])
                                    else:
                                        statistics_raw[browser][pv][category][attribute] = [[1, value]]
                                        
                                else:
                                    # Add category and add attribute
                                    statistics_raw[browser][pv][category] = {}
                                    statistics_raw[browser][pv][category][attribute] = [[1, value]]
    return statistics_raw
    

def main():
    fingerprint_paths = ".\\Fingerprints\\"
    result_path = ".\\results\\"    

    statistics_raw = genereate_statistics_raw(fingerprint_paths)
    statistics = genereate_statistics(statistics_raw)
                                
    with open(os.path.join(result_path, "statistics_raw.json"), "w") as json_file:
        json.dump(statistics_raw, json_file, indent=1) 

    with open(os.path.join(result_path, "statistics.json"), "w") as json_file:
        json.dump(statistics, json_file, indent=1)          


if __name__ == "__main__":
    main()