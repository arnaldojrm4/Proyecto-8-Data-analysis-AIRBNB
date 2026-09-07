[CmdletBinding()]
param(
    [Parameter()]
    [string]$DataRoot = (Join-Path (Split-Path $PSScriptRoot -Parent) 'data\powerbi'),

    [Parameter()]
    [string]$ExpectedSchemaMajor = '1'
)

$ErrorActionPreference = 'Stop'
$requiredOutputs = @(
    'dim_city.csv',
    'dim_neighborhood.csv',
    'dim_room_type.csv',
    'fact_listings.csv',
    'fact_opportunity_segments.csv',
    'fact_statistical_results.csv',
    'fact_quality_summary.csv'
)
$requiredFiles = @('build_control.csv') + $requiredOutputs
$restrictedHeaders = @('listingname', 'hostname', 'listingid', 'hostid', 'latitude', 'longitude')
$allowedCoordinates = @{
    'dim_neighborhood.csv' = @('centroidlatitude', 'centroidlongitude')
    'fact_opportunity_segments.csv' = @('centroidlatitude', 'centroidlongitude')
}

function Normalize-Header([string]$Value) {
    return ($Value.ToLowerInvariant() -replace '[^a-z0-9]', '')
}

function Assert-Condition([bool]$Condition, [string]$Message) {
    if (-not $Condition) {
        throw "Power BI verification failed: $Message"
    }
}

$resolvedRoot = (Resolve-Path -LiteralPath $DataRoot).Path
$actualCsv = @(Get-ChildItem -LiteralPath $resolvedRoot -File -Filter '*.csv' | ForEach-Object Name)
Assert-Condition (((($actualCsv | Sort-Object) -join '|') -eq (($requiredFiles | Sort-Object) -join '|'))) `
    "expected exactly $($requiredFiles.Count) contractual CSV files"

$controlPath = Join-Path $resolvedRoot 'build_control.csv'
$control = @(Import-Csv -LiteralPath $controlPath)
Assert-Condition ($control.Count -eq $requiredOutputs.Count) 'build_control.csv must contain one row per output'
Assert-Condition ((@($control.build_id | Sort-Object -Unique)).Count -eq 1) 'mixed build_id values'
Assert-Condition (($control.release_gate_status -notcontains 'fail') -and
    (@($control.release_gate_status | Sort-Object -Unique) -join '|' -eq 'pass')) 'release gate is not pass'

foreach ($version in $control.schema_version) {
    Assert-Condition (($version -split '\.')[0] -eq $ExpectedSchemaMajor) `
        "schema major $version is incompatible with $ExpectedSchemaMajor"
}

$rowsByFile = @{}
foreach ($filename in $requiredOutputs) {
    $path = Join-Path $resolvedRoot $filename
    $row = @($control | Where-Object output_file -eq $filename)
    Assert-Condition ($row.Count -eq 1) "missing or duplicated control row for $filename"

    $data = @(Import-Csv -LiteralPath $path)
    $rowsByFile[$filename] = $data.Count
    $hash = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    Assert-Condition ($hash -eq $row[0].output_sha256.ToLowerInvariant()) "hash mismatch for $filename"
    Assert-Condition ($data.Count -eq [int64]$row[0].output_row_count) "row mismatch for $filename"

    $headers = @($data[0].PSObject.Properties.Name)
    $normalized = @($headers | ForEach-Object { Normalize-Header $_ })
    $leaks = @($normalized | Where-Object { $restrictedHeaders -contains $_ })
    Assert-Condition ($leaks.Count -eq 0) "restricted header in $filename"

    $coordinates = @($normalized | Where-Object { $_ -match 'latitude|longitude' })
    $allowed = @($allowedCoordinates[$filename])
    Assert-Condition (@($coordinates | Where-Object { $allowed -notcontains $_ }).Count -eq 0) `
        "individual coordinate exposed in $filename"
}

$listings = @(Import-Csv -LiteralPath (Join-Path $resolvedRoot 'fact_listings.csv'))
$listingKeys = @($listings.listing_key | Sort-Object -Unique)
$expectedCanonical = [int64]$control[0].canonical_row_count
$expectedDistinct = [int64]$control[0].distinct_listing_key_count
$difference = $expectedCanonical - $listings.Count
Assert-Condition ($listingKeys.Count -eq $listings.Count) 'listing_key is not unique'
Assert-Condition ($listings.Count -eq $expectedDistinct) 'distinct listing count does not reconcile'
Assert-Condition ($difference -eq 0) 'Diferencia de conciliación is not zero'

$result = [ordered]@{
    status = 'pass'
    data_root = $resolvedRoot
    build_id = $control[0].build_id
    schema_version = $control[0].schema_version
    output_files = $requiredOutputs.Count
    imported_listing_rows = $listings.Count
    distinct_listing_keys = $listingKeys.Count
    reconciliation_difference = $difference
    privacy = 'pass'
    hashes = 'pass'
}
$result | ConvertTo-Json -Depth 3
