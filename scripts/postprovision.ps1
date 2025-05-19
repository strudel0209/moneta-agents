# Add here commands that need to be executed after provisioning
# Typically: loading data in databases, AI Search or storage accounts, etc.
# see https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/azd-extensibility

$REDIRECT_URI = "$Env:SERVICE_FRONTEND_URL/.auth/login/aad/callback"
Write-Host "Adding app registration redirect URI '$REDIRECT_URI'..."
az ad app update `
    --id "$Env:AZURE_CLIENT_APP_ID" `
    --web-redirect-uris "http://localhost:5801/.auth/login/aad/callback" $REDIRECT_URI `
    --output table

azd env set AZURE_CLIENT_APP_SECRET ""
