#!/usr/bin/env pwsh

# Add here commands that need to be executed before provisioning
# Typically: preparing additional environment variables, creating app registrations, etc.
# see https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/azd-extensibility

$AZURE_APP_ID = az ad app show `
    --id "${env:AZURE_CLIENT_APP_ID:-00000000-0000-0000-0000-000000000000}" `
    --query '[].id' `
    -o tsv 2> $null

if ($AZURE_APP_ID) {
    Write-Output "Deleting app $env:AZURE_CLIENT_APP_ID..."
    az ad app delete --id "$AZURE_APP_ID"
}