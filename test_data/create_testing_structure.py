import os, json
from datetime import date

def main():
    root_folder = str(date.today())

    subpaths = [
        "PV1\\Chrome\\2",
        "PV1\\Chrome\\1",
        "PV1\\Chrome\\3",
        "PV1\\Firefox\\1",
        "PV1\\Firefox\\2",
        "PV1\\Firefox\\3",
        "PV1\\Edge\\1",
        "PV1\\Edge\\2",
        "PV1\\Edge\\3",
        "PV2\\Chrome\\1",
        "PV2\\Chrome\\2",
        "PV2\\Chrome\\3",
        "PV2\\Firefox\\1",
        "PV2\\Firefox\\2",
        "PV2\\Firefox\\3",
        "PV2\\Edge\\1",
        "PV2\\Edge\\2",
        "PV2\\Edge\\3"
    ]          


    d = {
        "Canvas Fingerprinting": {
            "Signature": ""
            },
        "WebGL Report": {
            "WebGL Report Hash": "",
            "WebGL Image Hash": ""
            },
        "Font Fingerprinting": {
            "Fonts Enumeration": "",
            "Unicode Glyphs": ""
            },
        "Features Detection": {
            "Features Hash": ""
            },
        "Client Rects": {
            "Full Hash": ""
        }
        }

    for p in subpaths:
        path = os.path.join(".\\", root_folder, p)

        if not os.path.isdir(path):
            os.makedirs(path)

        if not os.path.isfile(os.path.join(path, "m_data.json")):
            with open(os.path.join(path, "m_data.json"), "w") as json_file:
                json.dump(d, json_file, indent=1)
        else:
            print(f"{os.path.join(path, 'm_data.json')} already exists.")

        for html in ["http_header.html", "javascript.html", "webrtc_leak.html"]:
            if not os.path.isfile(os.path.join(path, html)):
                open(os.path.join(path, html), "w").close()
            else:
                print(f"{os.path.join(path, html)} already exists.")


if __name__ == "__main__":
    main()