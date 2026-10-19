# Standalone administrative setup. No grant values, files, claims or source runs.
# Use the verified 64-bit PowerShell 7 host. Default mode is read-only.
[CmdletBinding()]
param([ValidateSet('Inspect', 'Install', 'SelfTest')][string]$Mode = 'Inspect')
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$Paths = @('SOFTWARE\MCM_FIELD_ORGANISM',
    'SOFTWARE\MCM_FIELD_ORGANISM\S2UC',
    'SOFTWARE\MCM_FIELD_ORGANISM\S2UC\ApprovedOneShots')
$Sddl = 'O:BAG:BAD:P(A;CI;KA;;;SY)(A;CI;KA;;;BA)(A;CI;KR;;;AU)'
$Created = [System.Collections.Generic.List[string]]::new()

function Assert-Security([System.Security.AccessControl.RawSecurityDescriptor]$Descriptor) {
    if ($Descriptor.Owner.Value -notin @('S-1-5-18','S-1-5-32-544')) { throw 'OWNER_MISMATCH' }
    if (($Descriptor.ControlFlags -band [System.Security.AccessControl.ControlFlags]::DiscretionaryAclProtected) -eq 0) { throw 'DACL_NOT_PROTECTED' }
    if ($null -eq $Descriptor.DiscretionaryAcl -or $Descriptor.DiscretionaryAcl.Count -ne 3) { throw 'DACL_SHAPE' }
    $Expected = @{'S-1-5-18'=983103; 'S-1-5-32-544'=983103; 'S-1-5-11'=131097}
    $Seen = @{}
    foreach ($Ace in $Descriptor.DiscretionaryAcl) {
        if ($Ace -isnot [System.Security.AccessControl.CommonAce] -or $Ace.IsCallback -or
            $Ace.AceQualifier -ne [System.Security.AccessControl.AceQualifier]::AccessAllowed -or
            [int]$Ace.AceFlags -ne 2) { throw 'ACE_TYPE_OR_FLAGS' }
        $Sid = $Ace.SecurityIdentifier.Value
        if (-not $Expected.ContainsKey($Sid) -or $Seen.ContainsKey($Sid) -or $Ace.AccessMask -ne $Expected[$Sid]) { throw 'ACE_RIGHTS' }
        $Seen[$Sid] = $true
    }
}

function Assert-Content([string[]]$Values, [string[]]$Children, [int]$Index) {
    if ($Values.Count -ne 0) { throw 'EXISTING_VALUES_REQUIRE_REVIEW' }
    $Allowed = if ($Index -eq 0) { 'S2UC' } elseif ($Index -eq 1) { 'ApprovedOneShots' } else { '' }
    foreach ($Child in $Children) {
        if ($Child -cne $Allowed) { throw 'EXISTING_SUBKEY_REQUIRES_REVIEW' }
    }
}

function Read-State($Base, [string]$Path, [int]$Index) {
    $Key = $Base.OpenSubKey($Path, [Microsoft.Win32.RegistryKeyPermissionCheck]::ReadSubTree,
        [System.Security.AccessControl.RegistryRights]::ReadKey)
    if ($null -eq $Key) { return [pscustomobject]@{path=$Path; exists=$false; verified=$false} }
    try {
        $Security = $Key.GetAccessControl([System.Security.AccessControl.AccessControlSections]::Owner -bor
            [System.Security.AccessControl.AccessControlSections]::Access)
        $Raw = [System.Security.AccessControl.RawSecurityDescriptor]::new($Security.GetSecurityDescriptorBinaryForm(),0)
        Assert-Security $Raw
        Assert-Content @($Key.GetValueNames()) @($Key.GetSubKeyNames()) $Index
        return [pscustomobject]@{path=$Path; exists=$true; verified=$true;
            owner=$Raw.Owner.Value; sddl=$Raw.GetSddlForm([System.Security.AccessControl.AccessControlSections]::All);
            read_access=$true; values=0}
    } finally { $Key.Dispose() }
}

try {
        Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class S2UCRegistryCreate {
    [StructLayout(LayoutKind.Sequential)] public struct SA {
        public int Length; public IntPtr Descriptor; public int Inherit;
    }
    [DllImport("advapi32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
    public static extern bool ConvertStringSecurityDescriptorToSecurityDescriptor(
        string sddl, uint revision, out IntPtr descriptor, out uint size);
    [DllImport("advapi32.dll", CharSet=CharSet.Unicode)]
    public static extern int RegCreateKeyEx(IntPtr parent, string leaf, int reserved,
        string cls, int options, int access, ref SA security, out IntPtr key, out int disposition);
    [DllImport("advapi32.dll")] public static extern int RegCloseKey(IntPtr key);
    [DllImport("kernel32.dll")] public static extern IntPtr LocalFree(IntPtr value);
}
'@
    Assert-Security ([System.Security.AccessControl.RawSecurityDescriptor]::new($Sddl))
    if ($Mode -eq 'SelfTest') {
        $Cases = @(
            'O:AUG:BAD:P(A;CI;KA;;;SY)(A;CI;KA;;;BA)(A;CI;KR;;;AU)',
            'O:BAG:BAD:(A;CI;KA;;;SY)(A;CI;KA;;;BA)(A;CI;KR;;;AU)',
            'O:BAG:BAD:P(A;CI;KA;;;SY)(A;CI;KA;;;BA)(A;CI;KA;;;AU)',
            'O:BAG:BAD:P(A;CI;KA;;;SY)(A;CI;KA;;;BA)',
            'O:BAG:BAD:P(A;CI;KA;;;SY)(A;CI;KA;;;BA)(A;CI;KR;;;WD)')
        foreach ($Bad in $Cases) {
            $Rejected = $false
            try { Assert-Security ([System.Security.AccessControl.RawSecurityDescriptor]::new($Bad)) } catch { $Rejected=$true }
            if (-not $Rejected) { throw 'SELFTEST_ACCEPTED_BAD_DACL' }
        }
        foreach ($Index in 0..2) { Assert-Content @() @() $Index }
        Assert-Content @() @('S2UC') 0
        Assert-Content @() @('ApprovedOneShots') 1
        $Rejected=$false
        try { Assert-Content @('unexpected') @() 2 } catch { $Rejected=$true }
        if (-not $Rejected) { throw 'SELFTEST_ACCEPTED_VALUE' }
        $Rejected=$false
        try { Assert-Content @() @('unexpected') 2 } catch { $Rejected=$true }
        if (-not $Rejected) { throw 'SELFTEST_ACCEPTED_CHILD' }
        $NativeDescriptor=[IntPtr]::Zero; $NativeSize=[uint32]0
        if (-not [S2UCRegistryCreate]::ConvertStringSecurityDescriptorToSecurityDescriptor($Sddl,1,[ref]$NativeDescriptor,[ref]$NativeSize)) { throw 'SELFTEST_NATIVE_SDDL' }
        try {
            $Bytes=[byte[]]::new([int]$NativeSize)
            [Runtime.InteropServices.Marshal]::Copy($NativeDescriptor,$Bytes,0,$Bytes.Length)
            Assert-Security ([System.Security.AccessControl.RawSecurityDescriptor]::new($Bytes,0))
            $Attributes=[S2UCRegistryCreate+SA]::new()
            if ([Runtime.InteropServices.Marshal]::SizeOf($Attributes) -ne 24) { throw 'SELFTEST_X64_SA_LAYOUT' }
        } finally { $null=[S2UCRegistryCreate]::LocalFree($NativeDescriptor) }
        @{status='SELFTEST_PASS'; native_sddl=$true; native_sa_bytes=24; accepted_security=1; rejected_security=5;
          rejected_content=2; registry_opened=$false; registry_changed=$false} | ConvertTo-Json -Compress
        exit 0
    }
    if (-not [Environment]::Is64BitProcess) { throw 'USE_64_BIT_WINDOWS_POWERSHELL' }
    if ($Mode -eq 'Install') {
        $Principal = [Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())
        if (-not $Principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { throw 'ADMINISTRATOR_TOKEN_REQUIRED' }
    }
    $Base = [Microsoft.Win32.RegistryKey]::OpenBaseKey([Microsoft.Win32.RegistryHive]::LocalMachine,
        [Microsoft.Win32.RegistryView]::Registry64)
    try {
        # Inspect ALL existing targets before the first possible creation.
        $Before = @(for ($i=0; $i -lt $Paths.Count; $i++) { Read-State $Base $Paths[$i] $i })
        if ($Mode -eq 'Inspect') {
            $Ready = @($Before | Where-Object { -not $_.verified }).Count -eq 0
            @{status=$(if ($Ready) {'READY_EMPTY_TRUST_STORE'} else {'MISSING_KEYS'});
              mode=$Mode; view=64; keys=$Before; registry_changed=$false} | ConvertTo-Json -Depth 6
            if ($Ready) { exit 0 } else { exit 2 }
        }

        $Descriptor = [IntPtr]::Zero; $Size=[uint32]0
        if (-not [S2UCRegistryCreate]::ConvertStringSecurityDescriptorToSecurityDescriptor($Sddl,1,[ref]$Descriptor,[ref]$Size)) { throw 'SECURITY_DESCRIPTOR_CONVERSION' }
        try {
            for ($i=0; $i -lt $Paths.Count; $i++) {
                $State = Read-State $Base $Paths[$i] $i
                if ($State.exists) { continue } # Matching existing keys stay untouched.
                $Cut=$Paths[$i].LastIndexOf('\'); $ParentPath=$Paths[$i].Substring(0,$Cut)
                if ($i -gt 0) { $null=Read-State $Base $ParentPath ($i-1) }
                $Parent=$Base.OpenSubKey($ParentPath,[Microsoft.Win32.RegistryKeyPermissionCheck]::ReadWriteSubTree,
                    ([System.Security.AccessControl.RegistryRights]::ReadKey -bor [System.Security.AccessControl.RegistryRights]::CreateSubKey))
                if ($null -eq $Parent) { throw 'PARENT_MISSING' }
                try {
                    $Attributes=[S2UCRegistryCreate+SA]::new()
                    $Attributes.Length=[Runtime.InteropServices.Marshal]::SizeOf($Attributes)
                    $Attributes.Descriptor=$Descriptor
                    $Handle=[IntPtr]::Zero; $Disposition=0
                    # A single leaf, explicit 64-bit view, ACL attached at creation.
                    $ErrorCode=[S2UCRegistryCreate]::RegCreateKeyEx($Parent.Handle.DangerousGetHandle(),
                        $Paths[$i].Substring($Cut+1),0,$null,0,0x20119,[ref]$Attributes,[ref]$Handle,[ref]$Disposition)
                    if ($ErrorCode -ne 0) { throw "REG_CREATE_FAILED:$ErrorCode" }
                    try {
                        if ($Disposition -ne 1) { throw 'CONCURRENT_EXISTING_KEY_NO_OVERWRITE' }
                        $Created.Add($Paths[$i])
                    } finally { $null=[S2UCRegistryCreate]::RegCloseKey($Handle) }
                } finally { $Parent.Dispose() }
                $null=Read-State $Base $Paths[$i] $i
            }
            $After=@(for ($i=0; $i -lt $Paths.Count; $i++) { Read-State $Base $Paths[$i] $i })
            if (@($After | Where-Object { -not $_.verified }).Count -ne 0) { throw 'FINAL_VERIFICATION_FAILED' }
            @{status='REGISTRY_SETUP_VERIFIED'; mode=$Mode; view=64; keys=$After;
              created=@($Created.ToArray()); authorization_values_written=0;
              claims_created=0; sources_started=0} | ConvertTo-Json -Depth 6
        } finally { $null=[S2UCRegistryCreate]::LocalFree($Descriptor) }
    } finally { $Base.Dispose() }
    exit 0
} catch {
    @{status='STOPPED'; mode=$Mode; error=$_.Exception.Message;
      created=@($Created.ToArray()); no_automatic_rollback=$true;
      authorization_values_written=0; claims_created=0; sources_started=0} | ConvertTo-Json -Depth 5
    exit 1
}
