# Invoke the make_folder.ps1 script with the argument 'trash'
& "./make_folder.ps1" "trash"

# Remove the 'trash' folder and its contents
Remove-Item -Recurse -Force "./trash"

# Remove the '__pycache__' folder and its contents
Remove-Item -Recurse -Force "__pycache__"