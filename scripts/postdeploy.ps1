$pythonCmd = Get-Command python, python3 -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $pythonCmd) {
  Write-Host "Neither python nor python3 found. Please install Python."
  exit 1
}

# Install dependencies from requirements.txt in the scripts folder
$requirementsFile = Resolve-Path "./scripts/requirements.txt"
Write-Host "Installing dependencies from requirements.txt..."
Start-Process -FilePath $pythonCmd.Path -ArgumentList "-m pip install -q -r `"$requirementsFile`"" -Wait -NoNewWindow

Write-Host 'Uploading initial data to AI Search and Cosmos DB...'
Start-Process -FilePath $pythonCmd.Path -ArgumentList "./scripts/data_load/setup_aisearch.py" -Wait -NoNewWindow
Start-Process -FilePath $pythonCmd.Path -ArgumentList "./scripts/data_load/setup_cosmosdb.py" -Wait -NoNewWindow