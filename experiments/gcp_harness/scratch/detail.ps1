$gcp='C:\Program Files (x86)\Extron\GCP'
$loaded=@{}
Get-ChildItem "$gcp\*.dll" | ForEach-Object { try{$a=[Reflection.Assembly]::LoadFrom($_.FullName);$loaded[$a.GetName().Name]=$a}catch{} }
$h=[ResolveEventHandler]{ param($s,$e); $n=$e.Name.Split(',')[0]; if($script:loaded.ContainsKey($n)){return $script:loaded[$n]}; return $null }
[AppDomain]::CurrentDomain.add_AssemblyResolve($h)
$t=$loaded['Extron.Configuration.Drivers'].GetType('Extron.Configuration.Drivers.DriverFileAsset')
$r=$t::LoadFromFile($args[0])
$first=@($r.DriverCommands)[0]
Write-Output "DriverCommandAsset properties:"
$first.GetType().GetProperties() | ForEach-Object { Write-Output ("   {0} : {1}" -f $_.Name,$_.PropertyType.Name) }
