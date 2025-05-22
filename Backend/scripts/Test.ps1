param (
    [string]$ServerUrl = "http://127.0.0.1/collect"  # Default value
)

# Log the server URL
Write-Host "Server URL: $ServerUrl"

# Your PowerShell logic to collect/send data, etc.
Invoke-RestMethod -Uri $ServerUrl -Method Post -Body @{ data = "Sample Data" } -ContentType "application/json"
