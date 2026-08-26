param(
    [switch]$PolicyProbe
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($PolicyProbe) {
    [Console]::Out.WriteLine('{"schema_version":"g1-realpath-inventory-policy-probe-v1","policy_probe":true,"realpath_queries":0,"artifacts_written":0}')
    exit 0
}

$exclusionSetPath = 'C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/docs/forschung/213Z_G1_REALPFAD_AUSSCHLUSSMENGE.json'
$expectedExclusionSetBytes = 6253L
$expectedExclusionSetSha256 = '52DA5D8DD26314BF173367E7F02D1F1B1055077380E83159A0FAE3EB87304ACF'
$finalOutputPath = 'C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/213ZZ_g1_realpath_inventory.json'
$stagingOutputPath = 'C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/.213ZZ_g1_realpath_inventory.json.staging'
$outputSchemaVersion = 'g1-realpath-metadata-inventory-v1'
$expectedEntryCount = 54

if ($PSVersionTable.PSVersion -lt [Version]'5.1') {
    throw 'PowerShell 5.1 or newer is required.'
}

$exclusionSetFile = Get-Item -LiteralPath $exclusionSetPath -Force
if ($exclusionSetFile.PSIsContainer -or $exclusionSetFile.Length -ne $expectedExclusionSetBytes) {
    throw 'The exclusion-set byte binding does not match.'
}

$actualExclusionSetSha256 = (Get-FileHash -LiteralPath $exclusionSetPath -Algorithm SHA256).Hash.ToUpperInvariant()
if ($actualExclusionSetSha256 -cne $expectedExclusionSetSha256) {
    throw 'The exclusion-set SHA-256 binding does not match.'
}

$exclusionSet = Get-Content -LiteralPath $exclusionSetPath -Raw | ConvertFrom-Json
$topLevelProperties = @($exclusionSet.PSObject.Properties.Name)
if (($topLevelProperties.Count -ne 4) -or
    (@($topLevelProperties | Where-Object { $_ -notin @('schema', 'source_binding', 'expected_counts', 'entries') }).Count -ne 0)) {
    throw 'The exclusion-set top-level schema is invalid.'
}

if ($exclusionSet.schema -cne 'mcm-g1-validation-realpath-exclusion-v1') {
    throw 'The exclusion-set schema value is invalid.'
}

$entries = @($exclusionSet.entries)
if ($entries.Count -ne $expectedEntryCount) {
    throw 'The exclusion-set entry count is invalid.'
}

$boundPaths = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
foreach ($entry in $entries) {
    $entryProperties = @($entry.PSObject.Properties.Name)
    if (($entryProperties.Count -ne 2) -or
        (@($entryProperties | Where-Object { $_ -notin @('role', 'path') }).Count -ne 0)) {
        throw 'An exclusion-set entry has an invalid schema.'
    }

    if (($entry.role -isnot [string]) -or [String]::IsNullOrWhiteSpace($entry.role) -or
        ($entry.path -isnot [string]) -or [String]::IsNullOrWhiteSpace($entry.path)) {
        throw 'An exclusion-set entry contains an invalid binding.'
    }

    if (-not $boundPaths.Add($entry.path)) {
        throw 'The exclusion set contains a duplicate path binding.'
    }
}

if ((Test-Path -LiteralPath $finalOutputPath) -or (Test-Path -LiteralPath $stagingOutputPath)) {
    throw 'An inventory output path is already present.'
}

$results = New-Object 'System.Collections.Generic.List[object]'
$ordinal = 0
foreach ($entry in $entries) {
    $ordinal++
    try {
        $item = Get-Item -LiteralPath $entry.path -Force -ErrorAction Stop
    }
    catch [System.Management.Automation.ItemNotFoundException] {
        $item = $null
    }

    $exists = $null -ne $item
    $itemType = 'missing'
    $sizeBytes = $null
    if ($exists) {
        if ($item.PSIsContainer) {
            $itemType = 'directory'
        }
        elseif ($item -is [System.IO.FileInfo]) {
            $itemType = 'file'
            $sizeBytes = [Int64]$item.Length
        }
        else {
            $itemType = 'other'
        }
    }

    $results.Add([pscustomobject][ordered]@{
        ordinal = $ordinal
        role = $entry.role
        path = $entry.path
        exists = $exists
        item_type = $itemType
        size_bytes = $sizeBytes
    })
}

$inventory = [pscustomobject][ordered]@{
    schema_version = $outputSchemaVersion
    source_exclusion_set_sha256 = $expectedExclusionSetSha256
    entry_count = $expectedEntryCount
    entries = $results
}

$inventory | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $stagingOutputPath -Encoding UTF8 -NoNewline

$validatedInventory = Get-Content -LiteralPath $stagingOutputPath -Raw | ConvertFrom-Json
$validatedTopLevelProperties = @($validatedInventory.PSObject.Properties.Name)
if (($validatedTopLevelProperties.Count -ne 4) -or
    (@($validatedTopLevelProperties | Where-Object { $_ -notin @('schema_version', 'source_exclusion_set_sha256', 'entry_count', 'entries') }).Count -ne 0) -or
    ($validatedInventory.schema_version -cne $outputSchemaVersion) -or
    ($validatedInventory.source_exclusion_set_sha256 -cne $expectedExclusionSetSha256) -or
    ($validatedInventory.entry_count -ne $expectedEntryCount) -or
    (@($validatedInventory.entries).Count -ne $expectedEntryCount)) {
    throw 'The staged inventory failed structural validation.'
}

Move-Item -LiteralPath $stagingOutputPath -Destination $finalOutputPath
exit 0
