# Extron.ps1 - load Extron's own assemblies so a script can ask GC's code
# questions directly instead of through the UI.
#
# Dot-source it:   . (Join-Path $PSScriptRoot 'lib\Extron.ps1')
#
# Two things make this work, both measured on the 2026-09 Windows box:
#
#   1. The Extron DLLs are x86, so this must run in 32-bit PowerShell
#      (C:\Windows\SysWOW64\WindowsPowerShell\v1.0\powershell.exe).
#   2. A .pkp stream names the assembly versions it was written against
#      (Extron.Configuration.* 1.1.24.402), not the installed ones
#      (15.27.0.0). BinaryFormatter fails with "Unable to find assembly"
#      unless an AssemblyResolve handler maps the simple name onto whatever
#      is installed. Extron's own loader does the equivalent internally.

function Assert-Bitness32 {
    if ([IntPtr]::Size -ne 4) {
        throw ("Run under 32-bit PowerShell: " +
               "C:\Windows\SysWOW64\WindowsPowerShell\v1.0\powershell.exe " +
               "(the Extron assemblies are x86).")
    }
}

function Import-ExtronAssemblies {
    param([string]$GcpDir = 'C:\Program Files (x86)\Extron\GCP')

    Assert-Bitness32
    if (-not (Test-Path $GcpDir)) { throw "Global Configurator not found at $GcpDir" }

    $script:ExtronAssemblies = @{}
    foreach ($dll in Get-ChildItem (Join-Path $GcpDir '*.dll')) {
        try {
            $a = [Reflection.Assembly]::LoadFrom($dll.FullName)
            $script:ExtronAssemblies[$a.GetName().Name] = $a
        } catch {
            # Native and mixed-mode DLLs in the install do not load as managed
            # assemblies. None of them are needed to read a package.
        }
    }

    $handler = [ResolveEventHandler]{
        param($sender, $e)
        $simple = $e.Name.Split(',')[0]
        if ($script:ExtronAssemblies.ContainsKey($simple)) {
            return $script:ExtronAssemblies[$simple]
        }
        return $null
    }
    [AppDomain]::CurrentDomain.add_AssemblyResolve($handler)
    return $script:ExtronAssemblies
}
