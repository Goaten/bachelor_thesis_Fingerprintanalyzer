param (
    [switch]$extract = $false,
    [switch]$analyze = $false,
	[switch]$statistics = $false,
    [switch]$all = $false
)

# Script paths
$extract_script = ".\bl_extrator\bl_extract.py"
$analyze_script = ".\Analysis_script\analysis_script.py"
$statistics_script = ".\Fingerprint_statistics\fingerprint_statistics.py"

# data paths
$testdata_path = ".\test_data"
$fingerprints_path = ".\Fingerprints"

# Get list of already done
[string[]]$done_extracting = Get-Content -Path ".\done_extracting.txt"
[string[]]$done_analysing = Get-Content -Path ".\done_analysing.txt"

if ($all){
    if ($extract){Clear-Content ".\done_extracting.txt"}
    if ($analyze){
        Clear-Content ".\done_analysing.txt"
        Remove-Item -Path ".\results\analysis_results.json"
        Copy-Item -Path ".\results\analysis_results - Template.json" -Destination ".\results\analysis_results.json"
    } 
}

if ($extract) {
    Write-Host "Extrating all fingerprints from $($testdata_path)" -ForegroundColor Yellow
    $test_cases = @(Get-ChildItem -Path $testdata_path -Name -Directory -Exclude "test","omitted")

    # For each testcase
    for ($i = 0; $i -le ($test_cases.Length - 1); $i += 1){
        $test_case_path = Join-Path -Path $testdata_path -ChildPath $test_cases[$i]
        if ($all){
            Write-Host "Working with $($test_case_path)" -ForegroundColor Yellow
            python $extract_script $test_case_path
            Add-Content -Path ".\done_extracting.txt" -Value $test_case_path           
        }
        else {
            if (!($done_extracting -contains $test_case_path)){
                Write-Host "Working with $($test_case_path)" -ForegroundColor Yellow
                python $extract_script $test_case_path
                Add-Content -Path ".\done_extracting.txt" -Value $test_case_path 
            }
        }  
    }
    Write-Host "Done!" -ForegroundColor Yellow
}

if ($analyze) {
    Write-Host "Performing analysis on all fingerprints in $($fingerprints_path)" -ForegroundColor Yellow
    $test_cases = @(Get-ChildItem -Path $fingerprints_path -Name -Directory -Exclude "2022-03-11")

    # For each testcase
    for ($iCase = 0; $iCase -le ($test_cases.Length - 1); $iCase += 1){
        $case_path = Join-Path -Path $fingerprints_path -ChildPath $test_cases[$iCase]
        $PVs = @(Get-ChildItem -Path $case_path -Name -Directory)

        # For each PV
        for ($iPV = 0; $iPV -le ($PVs.Length - 1); $iPV += 1){
            $pv_path = Join-Path -Path $case_path -ChildPath $PVs[$iPV]
            $browsers = @(Get-ChildItem -Path $pv_path -Name -Directory)

            for ($iBrowser = 0; $iBrowser -le ($browsers.Length - 1); $iBrowser += 1){
                $browser_path = Join-Path -Path $pv_path -ChildPath $browsers[$iBrowser]

                if ($all){
                    Write-Host "Working with $($browser_path)" -ForegroundColor Yellow
                    python $analyze_script $browser_path
                    Add-Content -Path ".\done_analysing.txt" -Value $browser_path           
                }
                else {
                    if (!($done_analysing -contains $browser_path)){
                        Write-Host "Working with $($browser_path)" -ForegroundColor Yellow
                        python $analyze_script $browser_path
                        Add-Content -Path ".\done_analysing.txt" -Value $browser_path 
                    }
                }
            }

        }

    }
    Write-Host "Done!" -ForegroundColor Yellow
}

if ($statistics) {
    Write-Host "Generating statistics for all browsers' from fingerprints in $($fingerprints_path)" -ForegroundColor Yellow
    python $statistics_script
    Write-Host "Done!" -ForegroundColor Yellow
}