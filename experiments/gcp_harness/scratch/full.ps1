$gcp='C:\Program Files (x86)\Extron\GCP'
$loaded=@{}
Get-ChildItem "$gcp\*.dll" | ForEach-Object { try{$a=[Reflection.Assembly]::LoadFrom($_.FullName);$loaded[$a.GetName().Name]=$a}catch{} }
$h=[ResolveEventHandler]{ param($s,$e); $n=$e.Name.Split(',')[0]; if($script:loaded.ContainsKey($n)){return $script:loaded[$n]}; return $null }
[AppDomain]::CurrentDomain.add_AssemblyResolve($h)
$t=$loaded['Extron.Configuration.Drivers'].GetType('Extron.Configuration.Drivers.DriverFileAsset')
$r=$t::LoadFromFile($args[0])
if($r -eq $null){ Write-Output "LoadFromFile: NULL"; exit 1 }
foreach($c in ($r.DriverCommands | Sort-Object ScriptMethodName)){
  $ps=@()
  foreach($p in $c){
    $states=@()
    try { foreach($s in $p){ $states += $s.Name } } catch {}
    if($states.Count -gt 0){ $ps += ("{0}[{1}]" -f $p.Name, ($states -join '/')) }
    else { $ps += $p.Name }
  }
  Write-Output ("{0,-24} {1,-26} attrs={2,-4} {3}" -f $c.ScriptMethodName, $c.Name, [int]$c.Attributes, ($ps -join ' | '))
}
