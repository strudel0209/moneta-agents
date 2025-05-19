$ErrorActionPreference = "Stop"

if (-Not $Env:AZURE_AUTH_TENANT_ID) {
    $Env:AZURE_AUTH_TENANT_ID = (az account show --query tenantId -o tsv)
    Write-Host "AZURE_AUTH_TENANT_ID not provided: Default to $($Env:AZURE_AUTH_TENANT_ID) from AZ CLI"
}
azd env set AZURE_AUTH_TENANT_ID $Env:AZURE_AUTH_TENANT_ID

$APP_NAME = "$($Env:AZURE_ENV_NAME)-app"
$CURRENT_USER_UPN = az ad signed-in-user show --query userPrincipalName -o tsv
$CURRENT_USER_ID = az ad user show --id $CURRENT_USER_UPN --query id --output tsv
$AZURE_CLIENT_APP_ID = (az ad app list --display-name $APP_NAME --query '[].appId' -o tsv)

Write-Host "Current user          : $CURRENT_USER_UPN"
Write-Host "Current tenant        : $($Env:AZURE_AUTH_TENANT_ID)"
Write-Host "App Registration name : $APP_NAME"

if (-Not $AZURE_CLIENT_APP_ID) {
    Write-Host "Creating app $APP_NAME..."
    $AZURE_APP_ID = az ad app create --display-name $APP_NAME --web-redirect-uris http://localhost:5801/ --query id -o tsv
    $AZURE_CLIENT_APP_ID = (az ad app show --id $AZURE_APP_ID --query appId -o tsv)

    az ad app update `
      --id $AZURE_CLIENT_APP_ID `
      --identifier-uris "api://$AZURE_CLIENT_APP_ID" `
      --enable-id-token-issuance true `
      --enable-access-token-issuance true `
      --required-resource-accesses @scripts/requiredResourceAccess.json

    $SERVICE_PRINCIPAL_ID = az ad sp create --id $AZURE_CLIENT_APP_ID --query id -o tsv
    az ad app owner add --id $AZURE_CLIENT_APP_ID --owner-object-id $CURRENT_USER_ID

    $AZURE_CLIENT_APP_SECRET = az ad app credential reset `
      --id $AZURE_CLIENT_APP_ID `
      --display-name "client-secret" `
      --query password `
      --years 1 `
      -o tsv

    az rest --method PATCH --headers 'Content-Type=application/json' --uri "https://graph.microsoft.com/v1.0/applications/$AZURE_APP_ID" --body @scripts/oauth2PermissionScopes.json
    az rest --method PATCH --headers 'Content-Type=application/json' --uri "https://graph.microsoft.com/v1.0/applications/$AZURE_APP_ID" --body @scripts/preAuthorizedApplications.json

    azd env set AZURE_CLIENT_APP_SECRET $AZURE_CLIENT_APP_SECRET
    Write-Host "App $APP_NAME created with ID $AZURE_CLIENT_APP_ID and SP ID $SERVICE_PRINCIPAL_ID"
}
else {
    Write-Host "App '$AZURE_CLIENT_APP_ID' already exists, skipping creation"
}

azd env set AZURE_CLIENT_APP_ID $AZURE_CLIENT_APP_ID
