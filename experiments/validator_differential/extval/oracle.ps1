param([string]$ListFile,[string]$OutFile,[switch]$LoadGuidTable)
$ErrorActionPreference='Stop'
$gcp="C:\Program Files (x86)\Extron\GCP"
[Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Contracts.dll") | Out-Null
[Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Core.dll") | Out-Null
$asm=[Reflection.Assembly]::LoadFrom("$gcp\Extron.Configuration.Drivers.dll")
$dfaT=$asm.GetType("Extron.Configuration.Drivers.DriverFileAsset")
$valT=$asm.GetType("Extron.Configuration.Drivers.DriverAssetValidator")
$loadM=$dfaT.GetMethod("LoadFromFile",[Type[]]@([string]))
$instF=$valT.GetField("Instance",'Public,Static')
$inst=$instF.GetValue($null)
$valM=$valT.GetMethod("Validate")
if($LoadGuidTable){
  try{ $valT.GetMethod("LoadDefaultFromResource").Invoke($inst,@()) | Out-Null; Write-Host "guidtable: loaded" }
  catch{ Write-Host ("guidtable: FAILED " + $_.Exception.GetBaseException().GetType().FullName + ": " + $_.Exception.GetBaseException().Message) }
}
$sw=New-Object IO.StreamWriter($OutFile,$false,(New-Object Text.UTF8Encoding($false)))
$sw.WriteLine("path`tstatus`tcode`tdetail")
$n=0
foreach($p in [IO.File]::ReadLines($ListFile)){
  if([string]::IsNullOrWhiteSpace($p)){continue}
  $n++
  $status="ok"; $code=""; $detail=""
  try{
    $la=New-Object object[] 1
    $la[0]=[string]$p
    $asset=$loadM.Invoke($null,$la)
    if($null -eq $asset){ $status="loadnull"; $detail="LoadFromFile returned null" }
    else{
      try{
        $va=New-Object object[] 1
        $va[0]=$asset
        $r=$valM.Invoke($inst,$va)
        $code=[int]$r; $detail=$r.ToString()
      }catch{
        $e=$_.Exception.GetBaseException()
        $status="validate_throw"; $detail=($e.GetType().FullName + ": " + ($e.Message -replace "[\r\n\t]"," "))
      }
    }
  }catch{
    $e=$_.Exception.GetBaseException()
    $status="load_throw"; $detail=($e.GetType().FullName + ": " + ($e.Message -replace "[\r\n\t]"," "))
  }
  $sw.WriteLine(("{0}`t{1}`t{2}`t{3}" -f $p,$status,$code,$detail))
  if($n % 200 -eq 0){ $sw.Flush(); Write-Host "  ...$n" }
}
$sw.Close()
Write-Host "done $n"
