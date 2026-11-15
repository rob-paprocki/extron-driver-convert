$gcp='C:\Program Files (x86)\Extron\GCP'
$loaded=@{}
Get-ChildItem "$gcp\*.dll" | ForEach-Object { try{$a=[Reflection.Assembly]::LoadFrom($_.FullName);$loaded[$a.GetName().Name]=$a}catch{} }
$h=[ResolveEventHandler]{ param($s,$e); $n=$e.Name.Split(',')[0]; if($script:loaded.ContainsKey($n)){return $script:loaded[$n]}; return $null }
[AppDomain]::CurrentDomain.add_AssemblyResolve($h)
$t=$loaded['Extron.Configuration.Drivers'].GetType('Extron.Configuration.Drivers.DriverFileAsset')
foreach($f in $args){
  Write-Output "=== $(Split-Path $f -Leaf)"
  $r=$t::LoadFromFile($f)
  if($r -eq $null){ Write-Output "  LoadFromFile: NULL"; continue }
  $dc=$r.DriverCommands
  $names=@()
  foreach($c in $dc){ $names += ("{0} [{1}]" -f $c.Name, $c.ScriptName) }
  Write-Output ("  DriverCommands: {0}" -f $names.Count)
  foreach($n in ($names|Sort-Object)){ Write-Output ("    {0}" -f $n) }
  foreach($m in $r.SupportedModels){ Write-Output ("  model {0} v{1} cmds={2}" -f $m.Name,$m.Ver,@($m.Commands).Count) }
}
