<#
.SYNOPSIS
    Ask Extron's own code whether it will load a .pkp, and what it sees inside.

.DESCRIPTION
    The check CLAUDE.md now requires before believing any object-graph edit.
    Our Python parser shares our model of the format; this does not.

    Default     DriverFileAsset.LoadFromFile - exactly what GC calls when it
                catalogues a package. NULL means GC will silently drop the file
                from Driver Manager (the finding 18 section 6 failure).

    -Deserialize  gunzip + BinaryFormatter.Deserialize, printing the full
                exception chain. LoadFromFile swallows the reason; this gives
                it (e.g. "An object cannot be registered twice").

    -Commands   walk the loaded asset: every DriverCommandAsset with its
                ScriptMethodName, display name, attribute bits, parameters and
                enum states, plus the command count per SupportedModel.

    Exit code 1 if any package fails LoadFromFile.

.EXAMPLE
    $ps32 = 'C:\Windows\SysWOW64\WindowsPowerShell\v1.0\powershell.exe'
    & $ps32 -ExecutionPolicy Bypass -File .\Load-Package.ps1 -Path ..\skeleton_i20\out\1bynd_19_20024_v1_0_0.pkp -Commands

.EXAMPLE
    # The finding 18 section 6 pair: identical clones, differing only in id sign.
    & $ps32 -ExecutionPolicy Bypass -File .\Load-Package.ps1 -Deserialize -Path ..\graph_probes\q_POS.pkp,..\graph_probes\q_MIX.pkp
#>
param(
    [Parameter(Mandatory = $true)][string[]]$Path,
    [switch]$Deserialize,
    [switch]$Commands,
    [string]$GcpDir = 'C:\Program Files (x86)\Extron\GCP'
)

. (Join-Path $PSScriptRoot 'lib\Extron.ps1')
$asm = Import-ExtronAssemblies -GcpDir $GcpDir
$fileAsset = $asm['Extron.Configuration.Drivers'].GetType('Extron.Configuration.Drivers.DriverFileAsset')

# `-File` hands every argument over as a plain string, so `-Path a.pkp,b.pkp`
# arrives as ONE comma-joined string rather than an array. Split it here so
# callers do not have to know that.
$Path = @($Path | ForEach-Object { $_ -split ',' } | ForEach-Object { $_.Trim() } | Where-Object { $_ })

$failed = 0
foreach ($p in $Path) {
    if (-not (Test-Path -LiteralPath $p)) {
        Write-Output ("=== {0}" -f $p)
        Write-Output "  MISSING      : no such file"
        $failed++
        continue
    }
    $full = (Resolve-Path -LiteralPath $p).Path
    Write-Output ("=== {0}" -f (Split-Path $full -Leaf))

    $r = $null
    try { $r = $fileAsset::LoadFromFile($full) }
    catch { Write-Output ("  LoadFromFile : threw - {0}" -f $_.Exception.Message) }
    if ($r -eq $null) {
        Write-Output "  LoadFromFile : NULL  - GC will drop this from its catalogue; -Deserialize gives the reason"
        $failed++
    } else {
        Write-Output ("  LoadFromFile : {0}  name={1}" -f $r.GetType().Name, $r.Name)
    }

    if ($Deserialize) {
        try {
            $fs = [IO.File]::OpenRead($full)
            try {
                $gz = New-Object IO.Compression.GZipStream($fs, [IO.Compression.CompressionMode]::Decompress)
                $ms = New-Object IO.MemoryStream
                $gz.CopyTo($ms)
                $gz.Dispose()
            } finally { $fs.Dispose() }
            $ms.Position = 0
            $bf = New-Object Runtime.Serialization.Formatters.Binary.BinaryFormatter
            $o = $bf.Deserialize($ms)
            Write-Output ("  Deserialize  : OK ({0})" -f $o.GetType().FullName)
        } catch {
            $e = $_.Exception
            $depth = 0
            while ($e -ne $null -and $depth -lt 6) {
                Write-Output ("  Deserialize  : [{0}] {1}: {2}" -f $depth, $e.GetType().FullName, $e.Message)
                $e = $e.InnerException
                $depth++
            }
        }
    }

    if ($Commands -and $r -ne $null) {
        $cmds = @($r.DriverCommands)
        Write-Output ("  DriverCommands: {0}" -f $cmds.Count)
        foreach ($c in ($cmds | Sort-Object ScriptMethodName)) {
            $params = @()
            foreach ($prm in $c) {
                $states = @()
                try { foreach ($s in $prm) { $states += $s.Name } } catch { }
                if ($states.Count -gt 0) { $params += ('{0}[{1}]' -f $prm.Name, ($states -join '/')) }
                else { $params += $prm.Name }
            }
            Write-Output ('    {0,-24} {1,-26} attrs={2,-3} {3}' -f $c.ScriptMethodName, $c.Name, [int]$c.Attributes, ($params -join ' | '))
        }
        foreach ($m in $r.SupportedModels) {
            Write-Output ('  model {0}  commands={1}' -f $m.Name, @($m.Commands).Count)
        }
    }
}
if ($failed -gt 0) { exit 1 }
