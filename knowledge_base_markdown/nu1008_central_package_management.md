# NU1008: Central Package Management Version Conflict

## Error Description
**Error Code:** NU1008

**Error Message:** 
```
Projects that use central package version management should not define the version on the PackageReference items but on the PackageVersion items.
```

This error occurs when a project has Central Package Management (CPM) enabled via `Directory.Packages.props`, but individual `.csproj` files still define package versions using the `Version` attribute on `<PackageReference>` items.

## Detection Tokens
- `NU1008`
- `central package version management`
- `should not define the version on the PackageReference items`
- `PackageVersion items`
- `Directory.Packages.props`
- `ManagePackageVersionsCentrally`

## Root Cause
Central Package Management is a NuGet feature (available in .NET SDK 7.0+) that allows managing all package versions from a single `Directory.Packages.props` file. When this feature is enabled:

1. The `Directory.Packages.props` file contains `<ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>`
2. All package versions should be declared in `Directory.Packages.props` using `<PackageVersion>` items
3. Individual project files should have `<PackageReference>` items **WITHOUT** the `Version` attribute

When a project has both CPM enabled AND versions defined in `<PackageReference>`, NuGet raises the NU1008 error because it creates ambiguity about which version to use.

## Fix Options

### Option 1: Remove Version Attributes from PackageReference (Recommended)
If you want to continue using Central Package Management, remove the `Version` attribute from all `<PackageReference>` items in project files.

**Before:**
```xml
<!-- In MyProject.csproj -->
<ItemGroup>
  <PackageReference Include="Newtonsoft.Json" Version="13.0.1" />
  <PackageReference Include="Microsoft.Extensions.Logging" Version="8.0.0" />
</ItemGroup>
```

**After:**
```xml
<!-- In MyProject.csproj -->
<ItemGroup>
  <PackageReference Include="Newtonsoft.Json" />
  <PackageReference Include="Microsoft.Extensions.Logging" />
</ItemGroup>
```

**Ensure versions are defined in Directory.Packages.props:**
```xml
<!-- In Directory.Packages.props -->
<Project>
  <PropertyGroup>
    <ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>
  </PropertyGroup>
  <ItemGroup>
    <PackageVersion Include="Newtonsoft.Json" Version="13.0.1" />
    <PackageVersion Include="Microsoft.Extensions.Logging" Version="8.0.0" />
  </ItemGroup>
</Project>
```

### Option 2: Use VersionOverride for Project-Specific Versions
If a specific project needs a different version than the centrally managed version, use `VersionOverride` instead of `Version`:

```xml
<!-- In MyProject.csproj -->
<ItemGroup>
  <PackageReference Include="Newtonsoft.Json" VersionOverride="12.0.3" />
</ItemGroup>
```

This explicitly overrides the centrally managed version for this project only.

### Option 3: Disable Central Package Management for Specific Project
If you need to disable CPM for a specific project, add this to the project file:

```xml
<PropertyGroup>
  <ManagePackageVersionsCentrally>false</ManagePackageVersionsCentrally>
</PropertyGroup>
```

Then you can define versions normally in that project's `<PackageReference>` items.

### Option 4: Disable Central Package Management Entirely
If you want to disable CPM for the entire solution, either:
- Delete the `Directory.Packages.props` file, OR
- Set `<ManagePackageVersionsCentrally>false</ManagePackageVersionsCentrally>` in `Directory.Packages.props`

## Automated Fix Script

```powershell
# Script to identify projects with NU1008 violation
# This script scans .csproj files for PackageReference items with Version attributes
# when Directory.Packages.props exists with CPM enabled

param(
    [Parameter(Mandatory=$true)]
    [string]$SolutionDir
)

Write-Host "=== NU1008 Fix: Scanning for PackageReference Version Conflicts ===" -ForegroundColor Cyan

# Check if Directory.Packages.props exists
$packagesProps = Join-Path $SolutionDir "Directory.Packages.props"
if (-not (Test-Path $packagesProps)) {
    Write-Host "No Directory.Packages.props found - CPM not enabled" -ForegroundColor Yellow
    exit 0
}

# Check if CPM is enabled
[xml]$packagesPropsXml = Get-Content $packagesProps
$cpmEnabled = $packagesPropsXml.Project.PropertyGroup.ManagePackageVersionsCentrally -eq "true"
if (-not $cpmEnabled) {
    Write-Host "Central Package Management not enabled in Directory.Packages.props" -ForegroundColor Yellow
    exit 0
}

Write-Host "CPM is enabled - scanning for version conflicts..." -ForegroundColor Green

# Find all .csproj files
$projects = Get-ChildItem -Path $SolutionDir -Recurse -Filter "*.csproj"
$conflictsFound = $false

foreach ($project in $projects) {
    [xml]$projectXml = Get-Content $project.FullName
    
    # Find PackageReference items with Version attribute
    $conflictingRefs = $projectXml.Project.ItemGroup.PackageReference | 
        Where-Object { $_.Version -ne $null -and $_.Version -ne "" }
    
    if ($conflictingRefs) {
        $conflictsFound = $true
        Write-Host "`nProject: $($project.Name)" -ForegroundColor Yellow
        Write-Host "Found PackageReference items with Version attribute:" -ForegroundColor Yellow
        
        foreach ($ref in $conflictingRefs) {
            Write-Host "  - $($ref.Include) Version='$($ref.Version)'" -ForegroundColor Red
        }
        
        Write-Host "  Fix: Remove Version attribute and ensure package is in Directory.Packages.props" -ForegroundColor Green
    }
}

if ($conflictsFound) {
    Write-Host "`n=== CONFLICTS FOUND ===" -ForegroundColor Red
    Write-Host "To fix: Remove Version attributes from PackageReference items in project files" -ForegroundColor Yellow
    Write-Host "Ensure all versions are defined in Directory.Packages.props" -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "`n=== NO CONFLICTS FOUND ===" -ForegroundColor Green
    Write-Host "All projects comply with Central Package Management requirements" -ForegroundColor Green
    exit 0
}
```

## How to Apply This Fix

1. **Identify the problematic project files** by examining the NU1008 error message - it will indicate which projects have the issue

2. **Choose your fix strategy:**
   - **Option 1 (recommended)**: Remove `Version` from `<PackageReference>` and ensure versions are in `Directory.Packages.props`
   - **Option 2**: Use `VersionOverride` for project-specific overrides
   - **Option 3**: Disable CPM for specific projects
   - **Option 4**: Disable CPM entirely

3. **For automated scanning**, run the PowerShell script above:
   ```powershell
   .\fix-nu1008.ps1 -SolutionDir "C:\path\to\solution"
   ```

4. **After making changes**, retry the restore command:
   ```powershell
   msbuild /t:restore "solution.sln" /v:minimal
   ```

## Microsoft Documentation References
- [Central Package Management (CPM)](https://learn.microsoft.com/en-us/nuget/consume-packages/central-package-management)
- [Getting Started with CPM](https://learn.microsoft.com/en-us/nuget/consume-packages/central-package-management#getting-started)
- [Overriding Package Versions](https://learn.microsoft.com/en-us/nuget/consume-packages/central-package-management#overriding-package-versions)
- [Disabling CPM](https://learn.microsoft.com/en-us/nuget/consume-packages/central-package-management#disabling-central-package-management)

## Related Errors
- **NU1604**: Package reference without version (older warning, replaced by NU1015 in .NET 10)
- **NU1015**: PackageReference without version in non-CPM scenarios
- **NU1507**: Multiple package sources with CPM

## Version Information
- **Feature Introduced**: .NET SDK 7.0 / NuGet 6.2
- **Applies to**: All PackageReference-based projects with CPM enabled
- **Visual Studio**: 2022 17.2+
