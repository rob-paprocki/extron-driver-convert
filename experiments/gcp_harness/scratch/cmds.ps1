$ErrorActionPreference='Continue'
$gcp='C:\Program Files (x86)\Extron\GCP'
$loaded=@{}
Get-ChildItem "$gcp\*.dll" | ForEach-Object { try{$a=[Reflection.Assembly]::LoadFrom($_.FullName);$loaded[$a.GetName().Name]=$a}catch{} }
$h=[ResolveEventHandler]{ param($s,$e); $n=$e.Name.Split(',')[0]; if($script:loaded.ContainsKey($n)){return $script:loaded[$n]}; return $null }
[AppDomain]::CurrentDomain.add_AssemblyResolve($h)
$t=$loaded['Extron.Configuration.Drivers'].GetType('Extron.Configuration.Drivers.DriverFileAsset')
foreach($f in $args){
  Write-Output "=== $(Split-Path $f -Leaf)"
  $r=$t::LoadFromFile($f)
  if($r -eq $null){ Write-Output "  LoadFromFile: null"; continue }
  $names=New-Object Collections.Generic.List[string]
  function Walk($a,$d){
    if($d -gt 6){return}
    if($a.GetType().Name -eq 'DriverCommandAsset'){ $script:names.Add($a.Name) }
    foreach($c in $a.ChildAssets){ Walk $c ($d+1) }
  }
  $script:names=$names
  Walk $r 0
  $u = $names | Sort-Object -Unique
  Write-Output ("  DriverCommandAsset objects: {0}  distinct: {1}" -f $names.Count, $u.Count)
  Write-Output ("  {0}" -f ($u -join ', '))
}
