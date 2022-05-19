# ExArbete_FingerprintAnalyzer

---
## Complete_analysis.ps1

### Description:
This is a script that will utalize three other scripts written with python. 

### Arguments:

[switch] extract: By setting this flag, it will traverse the 'test_data' folder to extact fingerprints and save them into the 'Fingerprints' folder as json files. If 'all' flag is not set, it will skip previously extracted data.

[switch] analyze: By setting this flag, it will traverse the 'fingerprints' folder to analyze all fingerprints in each test case and save results in the 'results' folder. If 'all' flag is not set, it will skip previously analyzed data.

[switch] statistics: By setting this flag, it will traverse the 'fingerprints' folder to perform statistics on all fingerprints in each test case and save results in the 'results' folder.

[switch] all: The effect of this flag is explained in affected flags.


## Statistics_summary.py

### Description:
Will create a short summary on the 'statistics.json' file that is created when the 'Complete_analysis.ps1' script is executed with the 'statistics' flag.

## create_testing_structure.py

### Description:
Will create a folder containing a file structur that is used when a new test is performed.

