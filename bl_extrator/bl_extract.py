import json, os, argparse
from bs4 import BeautifulSoup as bs


def extract_list(html, seperator):
    """
    Will extract content meant to be in a list. Seperator will indicate how to perform the split.

    Params:
    html: html code containing desired list content.
    [string] seperator: Indication for how to perform the split.

    Return:
    [list] List with desired content.
    """
    
    lst = []
    if seperator == ",":
        element = html.text
        lst = [e.strip() for e in element.split(seperator)]
    
    elif seperator == "str_lst":
        "[\"en-US\",\"en\"]"
        elements = html.text
        for e in elements.split(","):
            str_start = e.find("\"") + 1
            str_end = e.rfind("\"")
            lst.append(e[str_start:str_end])
        
    else:
        if html.find("div"):
            br_lst = html.find("div")
        else:
            br_lst = html
        
        for element in br_lst:
            if "<br/>" not in str(element):
                lst.append(element)

    return lst

def extract_data_webRTC(bs_html, config):
    """
    Specifically meant for the webRTC html test in browserleaks.
    Given html data and a configuration file. It will extract desired attributes based on the configuration file.

    Params:
    bs_html: Dictionary that contains data that is desired to be saved into a json format.
    [json] config: Data from config file. It will inform how html data should be extrated.

    Return:
    [dict] Dictionary containing extracted attributes.
    """   

    fingerprint = {}
    fingerprint["WebRTC Leak"] = {}

    for attribute in config: # For each category
        # Get attributes in category
        if attribute != "Media Devices":
            a = bs_html.find('span', {'id': config[attribute]})
            fingerprint["WebRTC Leak"][attribute] = a.text
        else:
            a = bs_html.find('td', {'id': config[attribute]})
            lst = a.text.splitlines()      

            mDevices = []
            d = {}
            for e in lst:
                if not e:
                    mDevices.append(d)
                    d = {}
                    continue

                pos = e.find(":")
                d[e[:pos].strip()] = e[pos+1:].strip()

                if len(lst) == 4 and len(d) == 4:
                    mDevices.append(d)
                    
            fingerprint["WebRTC Leak"][attribute] = mDevices

    return fingerprint


def extract_data(bs_html, config):
    """
    Given html data and a configuration file. It will extract desired attributes based on the configuration file.

    Params:
    bs_html: Dictionary that contains data that is desired to be saved into a json format.
    [json] config: Data from config file. It will inform how html data should be extrated.

    Return:
    [dict] Dictionary containing extracted attributes.
    """    

    lst_attr = {
        "Navigator Plugins": {
            "plugins": ",",
            "mimeTypes": ","
            },
        "SpeechSynthesis": {
            "Speech Voices": "",
            },
        "Navigator Object": {
            "languages": "str_lst"
        }

    }
    filter_out = ["Fullscreen Leak Test", "Mime Types"]
    fingerprint = {}
    for category in config: # For each category

        # Get attributes in category
        c = bs_html.find('tbody', {'id': config[category]})

        fingerprint[category] = {}
        # For each attribute in category
        for a in c:
            # Get elements in attribute (name, data)
            attribute = a.findAll("td" , recursive=False)
            
            attr_elements = []
            # for each element in attribute (name, data)
            for element in attribute:
                if element.text in filter_out:
                    attr_elements = []
                    break

                if attr_elements and category in lst_attr and attr_elements[0] in lst_attr[category]:
                    attr_elements.append(extract_list(element, lst_attr[category][attr_elements[0]]))
                else:
                    attr_elements.append(element.text)
                
            if attr_elements:
                fingerprint[category][attr_elements[0]] = attr_elements[1]

    return fingerprint

def save_data(data, path, filename):
    """
    Will save json data to a given path. The path will be created if it does not exist.

    Params:
    [dict] data: Dictionary that contains data that is desired to be saved into a json format.
    [string] path: Path to save location.
    [string] filename: Desired filename.

    Return:
    -
    """

    if not os.path.isdir(path):
        os.makedirs(path)

    with open(os.path.join(path, filename), "w") as json_file:
        json.dump(data, json_file, indent=1)

def get_html_content(html_path):
    """
    Read and return data from html file.

    Params:
    [string] path: Path to html file.

    Return:
    [dict]: html data.
    """
    # Get html content
    with open(html_path, "r", encoding="UTF-8") as f:
        soup = bs(f, "html.parser")
    return soup

def get_json_data(path):
    """
    Read and return data from json file.

    Params:
    [string] path: Path to json file.

    Return:
    [dict]: json data.
    """
    # Read json data that tells what and how to extract data
    with open(path, "r") as json_file:
        data = json.load(json_file)

    return data

def get_html_files(html_path, config_path):
    """
    Given a path to folder with html files, it will read content to memory, and the config json file that informs
    how to extract the html file's desired content.

    Params:
    [string] html_path: Path to html files.
    [string] config_path: Path to config files.

    Return:
    [list]: List of http data.
    """
    lookup = {
        "http_header.html": "http_headers.json",
        "javascript.html": "javascript.json",
        "webrtc_leak.html": "webRTC.json"
    }
    http_lst = []
    for f in os.listdir(html_path):
        if ".json" in f:
            continue
        if f not in lookup:
            print(f"ERROR: {f} is named incorrectly. Check spelling.")
        filepath = os.path.join(html_path, f)
        if os.path.isfile(filepath):
            http_lst.append({
                "name": f,
                "html": get_html_content(filepath),
                "config": get_json_data(os.path.join(config_path, lookup[f]))
            })

    return http_lst

def create_save_location(originPath, pv, browser):
    """
    Will construct path to desired save location.

    Params:
    [string] originPath: Path to testcase folder.
    [string] pv: Either PV1 or PV2.
    [string] browser: Current browser name.

    Return:
    [string]: Constructed path.
    """

    test_date = originPath.split("\\")[-1]

    save_path = os.path.join(originPath, "..\\..\\Fingerprints", test_date, pv, browser)  

    return save_path


def strip_strings_in_dict(d):
    """
    Will perform the strip funciton on all content in dictionary.

    Params:
    [dict] d: Desired dictionary.

    Return:
    [dict]: Stripped dictionary.
    """
    for category in d:
        for attribute in d[category]:
            d[category][attribute] = d[category][attribute].strip()
    return d


def main():
    """
    Main function.
    Will traverse folder and, from all pv and browsers, extact attributes from its three html files and one json file, and combine it into one single json file.
    New json file will be saved in predetermined location.

    Positional arguments:
    [string] source: Path to test case folder.
    """

    # Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("test_path", help="path to folder with test data for one test day.")
    args = parser.parse_args()
    
    exists = os.path.exists(".\\bl_extrator\\extraction_config")
    config_path = ".\\bl_extrator\\extraction_config" if exists else ".\\extraction_config\\"

    for pv in os.listdir(args.test_path):
        for browser in os.listdir(os.path.join(args.test_path, pv)):
            for test_num in os.listdir(os.path.join(args.test_path, pv, browser)):
                path = os.path.join(args.test_path, pv, browser, test_num)

                html_lst = get_html_files(path, config_path)

                data = get_json_data(os.path.join(path, "m_data.json"))
                data = strip_strings_in_dict(data)
                for html in html_lst:
                    if "webrtc_leak" in html["name"]:
                        data.update(extract_data_webRTC(html["html"], html["config"]))
                    else:
                        data.update(extract_data(html["html"], html["config"]))

                # Save data as json file
                save_location = create_save_location(args.test_path, pv, browser) if not args.debug else ".\\extracted_data"
                filename = "fingerprint_" + test_num + ".json"
                save_data(data, save_location, filename)
    
    return 0

if __name__ == "__main__":
    main()