"""
Analysis Script

Description:
Written to be run through the commandprompt with passing arguments.
Analyse differences in fingerprints and give points based on effective changes.

Positional arguments:
[string] source: Path to folder with fingerprints.
[string] destination: Path to destination folder to save output.

Optional arguments:
-d, --debug: Activate debugging.
-h: Print argument usage.

"""


import json, argparse, os
from deepdiff import DeepDiff

def get_json_data(path):
    """
    Get content in a json file.

    Params:
    [string] path: Path to json file.

    Return:
    Json content as a dictionary.
    """
    with open(path, "r") as json_file:
        data = json.load(json_file)

    return data


def get_fingerprints(path):
    """
    Get a list with all fingerprints in a provided path.

    Params:
    [string] path: Path to directory containing fingerprints.

    Return:
    A list of fingerprints.
    Each fingerprint is a dictionary containing the following:
        name: Name of fingerprint.
        path: Path to fingerprint.
        data: Contents of fingerprint.
    """
    fingerprints = []
    for f in os.listdir(path):
        filepath = os.path.join(path, f)
        if os.path.isfile(filepath):
            fingerprints.append({
                "name": f,
                "path": filepath,
                "data": get_json_data(filepath)
            })

    return fingerprints


def find_missing_attr(f1, f2):
    """
    Given two fingerprints, any attributes that are missing from one but not the other, will be detected.

    Params:
    [dict] f1: First fingerprint.
    [dict] f2: Second fingerprint.

    Return:
    [list]: List of missing attributes.
    """
    lst = []
    for category in f1["data"]:
        if category not in f2["data"]:
            print(f"ERROR: The category '{category}' in {f1['name']}, does not exist in {f2['name']}")
            exit(1)
        for attribute in f1["data"][category]:
            if attribute not in f2["data"][category]:
                print(f"ERROR: The attribute '{attribute}' in {f1['name']}, does not exist in {f2['name']}")
                lst.append(attribute)

    return lst


def lists_with_dict_changes(lst1, lst2):
    """
    Compare two lists of dictionaries and find differences.
    Build for the attribute 'media devices' and will only check 'label' and 'deviceID'

    Params:
    [list] lst1: First list.
    [list] lst2: Second list.

    Return:
    [dict]: Dictionary with found differences.
    """
    changes = {
        "label": False,
        "deviceId": False
    }
    # Find altered dictionaries
    for d1 in lst1:
        if False not in changes.values():
            return changes

        equal = False
        for d2 in lst2:
            diff_value = DeepDiff(d1,d2)
            # If identical found, break and continue with next dictionaty in lst1.
            if not diff_value:
                equal = True
                break
        # If d1 not in lst2
        if not equal:
            for key in d1:
                if key == "kind" or key == "groupId" or changes[key]:
                    continue

                exist = False
                for d2 in lst2:
                    if d1[key] == d2[key]:
                        exist = True
                        break
                # If key has changed
                if not exist:
                    changes[key] = True

    return changes


def lists_equal(lst1, lst2):
    """
    Compare two lists and see if they are equal.

    Params:
    [list] lst1: First list.
    [list] lst2: Second list.

    Return:
    [bool]: True if equal, else false.    
    """
    for element in lst1:
        if element not in lst2:
            return False
    for element in lst2:
        if element not in lst1:
            return False
       
    return True


def compare_fingerprints(f1, f2, pointsystem):
    """
    Two fingerprints are compared to detect any differences.

    Params:
    [dict] f1: First fingerprint.
    [dict] f2: Second fingerprint.
    [dict] pointsystem: Used pointsystem.

    Return:
    [dict]: A dictionary with found differences.
    """
    # Check if fingerprints have matching set of attributes.
    missing_attr = find_missing_attr(f1, f2)
    missing_attr += find_missing_attr(f2, f1)

    # Compare attribute values between fingerprints to find mismatched values.
    result = {
        "num_total": 0,
        "num_changed": 0,
        "changes": [],
        "ignored_changes": []
    }

    for category in f1["data"]:
        for attribute in f1["data"][category]:
            if attribute == "Media Devices" or pointsystem[category][attribute][0]:
                result["num_total"] += 1
            if attribute in missing_attr:
                continue
            elif isinstance(f1["data"][category][attribute], str):
                if f1["data"][category][attribute].upper().strip() != f2["data"][category][attribute].upper().strip():
                    # print(f"MISMATCH between {f1['name']} and {f2['name']} in {attribute}.\n{f1['data'][category][attribute]}\n{f2['data'][category][attribute]}")
                    if pointsystem[category][attribute][0]:
                        result["changes"].append({
                            "category": category,
                            "name": attribute,
                            "value1": f1['data'][category][attribute],
                            "value2": f2['data'][category][attribute]
                        })
                        result["num_changed"] += 1
                    else:
                        result["ignored_changes"].append({
                            "category": category,
                            "name": attribute,
                            "value1": f1['data'][category][attribute],
                            "value2": f2['data'][category][attribute]
                        })
            else:
                if attribute != "Media Devices":
                    equal = lists_equal(f1["data"][category][attribute], f2["data"][category][attribute])
                    if not equal:
                        # print(f"MISMATCH between {f1['name']} and {f2['name']} in {attribute}.\n{f1['data'][category][attribute]}\n{f2['data'][category][attribute]}")
                        if pointsystem[category][attribute][0]:
                            result["changes"].append({
                                "category": category,
                                "name": attribute,
                                "value1": f1['data'][category][attribute],
                                "value2": f2['data'][category][attribute]
                            })
                            result["num_changed"] += 1
                        else:
                            result["ignored_changes"].append({
                                "category": category,
                                "name": attribute,
                                "value1": f1['data'][category][attribute],
                                "value2": f2['data'][category][attribute]
                            })
                else:
                    # Is number of media devices equal?
                    if len(f1["data"][category][attribute]) != len(f2["data"][category][attribute]):
                        result["changes"].append({
                            "category": category,
                            "name": "Media Devices: Quantity",
                            "value1": len(f1["data"][category][attribute]),
                            "value2": len(f2["data"][category][attribute])
                        })
                        result["num_changed"] += 1

                    # Have any changes been made?

                    # What changes has been made?
                    changes = lists_with_dict_changes(f1["data"][category][attribute], f2["data"][category][attribute])

                    for key in changes:
                        if changes[key]:
                            result["changes"].append({
                                "category": category,
                                "name": f"Media Devices: {key}",
                                "value1": f1['data'][category][attribute],
                                "value2": f2['data'][category][attribute]
                            })
                            result["num_changed"] += 1

    return result


def get_max_points(pointsystem):
    """
    Calculate max available points.

    Params:
    [dict] pointsystem: Used pointsystem.

    Return:
    Two variables. Max points and number of attributes.
    """
    max_points = 0
    total_attr = 0
    included_attr = []
    for category in pointsystem:
        if category == "pointsystem":
            continue
        
        for attribute in pointsystem[category]:
            if not pointsystem[category][attribute][0]:
                continue

            # Check if attr have friends
            if pointsystem[category][attribute][1]:
                included = False
                for element in pointsystem[category][attribute][1]:
                    if element in included_attr:
                        included = True
                        break
                if not included:
                    group = pointsystem[category][attribute][0]
                    max_points += pointsystem["pointsystem"][group]
                    included_attr.append(f"{category};{attribute}")
                    total_attr += 1
            else:
                group = pointsystem[category][attribute][0]
                max_points += pointsystem["pointsystem"][group]
                total_attr += 1

    max_points = max_points * pointsystem["pointsystem"]["bonus"]
    total_attr = total_attr * pointsystem["pointsystem"]["bonus"]
    return max_points, total_attr

def award_points(changes, pointsystem):
    """
    Given occurred attribute changes, points are awared.

    Params:
    [dict] changes: Occurred attribute changes.
    [dict] pointsystem: Used pointsystem.

    Return:
    Two variables. Points awarded and number of counted changes.
    """
    num_changed = 0
    points = 0
    included_attr = []
    for attr in changes:
        category = attr["category"]
        attribute = attr["name"]
        group = pointsystem[category][attribute][0]
        included = False

        # Check if attribute has friends
        if pointsystem[category][attribute][1]:
            for element in pointsystem[category][attribute][1]:
                if element in included_attr:
                    included = True
                    break
        if not included:
            points += pointsystem["pointsystem"][group]
            num_changed += 1
            included_attr.append(f"{category};{attribute}")

    return points, num_changed


def get_effective_change(d_1_2, d_1_3, pointsystem):
    """
    Given two dictionaries of found differences between fingerprints. Both the effective and raw change is decided.

    Params:
    [dict] diff1_2: Differences between f1 and f2.
    [dict] diff1_3: Differences between f1 and f3.
    [dict] pointsystem: Used pointsystem.

    Return:
    Two variables. Percentage effective change (using pointsystem) and percentage raw change (without pointsystem)
    """

    # calculate max points
    max_points, total_attr = get_max_points(pointsystem)

    # Remove attribute changes from d_1_3 that exist in d_1_2
    for a1 in d_1_2["changes"]:
        for i, a2 in enumerate(d_1_3["changes"]):
            if a1["category"] == a2["category"] and a1["name"] == a2["name"]:
                del d_1_3["changes"][i]
                break
    
    # Give points for changes during session
    points, num = award_points(d_1_2["changes"], pointsystem)
    points * pointsystem["pointsystem"]["bonus"]
    num * pointsystem["pointsystem"]["bonus"]
    
    # Give points for changes between session
    tmp1, tmp2 = award_points(d_1_3["changes"], pointsystem)
    points += tmp1
    num += tmp2

    print(f"RAW: {num}/{total_attr} ({round((num/total_attr)*100, 2)}%)")
    print(f"SCORE: {points}/{max_points} ({round((points/max_points)*100, 2)}%)")

    return round((points/max_points)*100, 2), round((num/total_attr)*100, 2)

def select_fingerprint(fingerprints, name):
    """
    Given a specific fingerprint's name. This fingerprint will be found and returned.

    Params:
    [list] fingerprints: List of fingerprints.
    [string] name: Name of fingerprint

    Return:
    [dict] fingerprint.
    """
    for fingerprint in fingerprints:
        if name in fingerprint["name"]:
            return fingerprint

def print_diff(diff_1_2, diff_1_3):
    """
    Print used when debugging. Will print out found differences.

    Params:
    [dict] diff1_2: Differences between f1 and f2.
    [dict] diff1_3: Differences between f1 and f3.

    Return:
    -
    """

    print("\n-------------DURING SESSION-----------------\n")
    print("Number of attributes:", diff_1_2["num_total"])
    print("Number of changed attributes:", diff_1_2["num_changed"])
    print("\nCHANGES:")
    for attr in diff_1_2["changes"]:
        print(attr["category"], "-", attr["name"])
    print("\nIGNORED CHANGES:")
    for attr in diff_1_2["ignored_changes"]:
        print(attr["category"], "-", attr["name"])
    print("\n-------------BETWEEN SESSIONS-----------------\n")
    print("Number of attributes:", diff_1_3["num_total"])
    print("Number of changed attributes:", diff_1_3["num_changed"])
    print("\nChanges:")
    for attr in diff_1_3["changes"]:
        print(attr["category"], "-", attr["name"])
    print("\nIGNORED CHANGES:")
    for attr in diff_1_3["ignored_changes"]:
        print(attr["category"], "-", attr["name"])
    print("\n------------------------------------------\n")

def analyze_fingerprints(fingerprints, pointsystem):
    """
    Three fingerprints are compared, f1, f2, f3. 
    f1 and f2 is compared for changes.
    f1 and f3 is compared for changes.
    Effective change is then determined.

    Params:
    [list] fingerprints: A list of dictionaries who each represents a fingerprint.
    [dict] pointsystem: A dictionary for used pointsystem.

    Return:
    Two variables. Percentage effective change (using pointsystem) and percentage raw change (without pointsystem)
    """
    f1 = select_fingerprint(fingerprints, "fingerprint_1")
    f2 = select_fingerprint(fingerprints, "fingerprint_2")
    f3 = select_fingerprint(fingerprints, "fingerprint_3")
    
    # Compare fingerprint 1 and 2
    diff_1_2 = compare_fingerprints(f1, f2, pointsystem)

    # Compare fingerprints 1 and 3
    diff_1_3 = compare_fingerprints(f1, f3, pointsystem)

    # Determine effective changes with pointsystem and return result
    return get_effective_change(diff_1_2, diff_1_3, pointsystem)


def get_browser_and_pv(path):
    """
    Get browser and prefixed version from path.

    Params:
    [string] path: Path ending with /Prefixed_version/Browser

    Return:
    Two variables. Browser and Prefixed version.
    """
    components = path.split("\\")
    pv = components[-2]
    browser = components[-1]

    return browser, pv



def analyze():
    """
    Main function.
    Written to be run through the commandprompt with passing arguments.
    Analyse differences in fingerprints and give points based on effective changes.
    Will save result to a provided destination.

    Positional arguments:
    [string] source: Path to folder with fingerprints.

    """
    # Arguments from commandline
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="Path to folder with fingerprints")
    args = parser.parse_args()

    # Check provided paths
    if not os.path.isdir(args.source):
        print("Source path does not exist.")
        exit(1)
    
    # Get Pointsystem
    exists = os.path.exists(".\\Pointsystem\\pointsystem.json")
    pointsystem_path = ".\\Pointsystem\\pointsystem.json" if exists else "..\\Pointsystem\\pointsystem.json"
    pointsystem = get_json_data(pointsystem_path)

    # Get three fingerprints from source argument
    fingerprints = get_fingerprints(args.source)

    point_result, raw_result = analyze_fingerprints(fingerprints, pointsystem)

    # Save results
    results_path = ".\\results\\analysis_results.json"
    
    saved_results = get_json_data(results_path)
    browser, pv = get_browser_and_pv(args.source)
    
    # Pointsystem results
    saved_results[browser][pv]["test_results"].append(point_result)
    new_average = round(sum(saved_results[browser][pv]["test_results"])/len(saved_results[browser][pv]["test_results"]), 2)
    saved_results[browser][pv]["pointsystem_average"] = new_average

    # None pointsystem results
    saved_results[browser][pv]["raw_results"].append(raw_result)
    new_average = round(sum(saved_results[browser][pv]["raw_results"])/len(saved_results[browser][pv]["raw_results"]), 2)
    saved_results[browser][pv]["raw_average"] = new_average

    with open(results_path, "w") as json_file:
        json.dump(saved_results, json_file, indent=1)

    

    return


if __name__ == "__main__":
    os.system('color')
    analyze()
