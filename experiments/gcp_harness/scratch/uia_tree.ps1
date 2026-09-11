. "$PSScriptRoot\uia_lib.ps1"
$win = Get-GCP
Write-Output ("WINDOW '{0}'" -f $win.Current.Name)
Dump-Tree $win 0 3
