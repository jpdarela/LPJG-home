param (
    [string]$folderName
)

# Create the folder if it doesn't exist
if (-Not (Test-Path -Path $folderName)) {
    New-Item -ItemType Directory -Path $folderName
}

# Move .nc files to the specified folder
Move-Item -Path .\*.nc -Destination $folderName

# Move .log files to the specified folder
Move-Item -Path .\*.log -Destination $folderName

# Remove directories starting with 'run'
Remove-Item -Recurse -Force .\run*