# NU1605: Detected Package Downgrade

## Error Description
**Error Code:** NU1605

**Error Message Examples:**
```
Detected package downgrade: 'Microsoft.Extensions.Http' from 9.0.7 to 8.0.0. Reference the package directly from the project to select a different version.
```

```
Warning As Error: Detected package downgrade: [PackageName] from [HigherVersion] to [LowerVersion]
```

This warning/error occurs when NuGet's dependency resolution causes a package to be downgraded from a higher version to a lower version due to the "direct dependency wins" rule. While NU1605 is a warning in NuGet, the .NET SDK often treats it as an error through `WarningsAsErrors` or `TreatWarningsAsErrors` settings.

## Detection Tokens
- `NU1605`
- `Detected package downgrade`
- `Warning As Error`
- `Reference the package directly from the project to select a different version`
- `direct dependency`
- `WarningsAsErrors`

## Root Cause

NuGet uses the **"direct dependency wins"** rule during dependency resolution:
- When a project graph contains different versions of the same package
- If one version is a **direct dependency** (explicitly referenced in a project file)
- That direct version overrides any transitive dependency versions

**Example scenario causing NU1605:**
```
Project -> PackageA 1.0.0 -> PackageB >= 9.0.7 (transitive, requires higher version)
Project -> PackageB >= 8.0.0 (direct, lower version specified)
```

Result: NuGet uses 8.0.0 because it's directly referenced, causing a downgrade from 9.0.7 → 8.0.0

This can potentially break PackageA which expects PackageB >= 9.0.7, leading to runtime errors.

## Why This Becomes an Error

While NuGet treats NU1605 as a warning, it often becomes a build error because:

1. **.NET SDK default behavior**: The .NET SDK sets `WarningsAsErrors` to include NU1605
2. **Project-level setting**: Your project may have `<TreatWarningsAsErrors>true</TreatWarningsAsErrors>`
3. **Build configuration**: CI/CD pipelines often treat all warnings as errors

## Fix Options

### Option 1: Upgrade Direct Dependency to Higher Version (Recommended)
Update the direct package reference to match or exceed the required version.

**Before:**
```xml
<ItemGroup>
  <PackageReference Include="Microsoft.Extensions.Http" Version="8.0.0" />
  <!-- Some other package requires Microsoft.Extensions.Http >= 9.0.7 -->
</ItemGroup>
```

**After:**
```xml
<ItemGroup>
  <PackageReference Include="Microsoft.Extensions.Http" Version="9.0.7" />
</ItemGroup>
```

### Option 2: Add Direct Reference at Higher Version
If you don't currently have a direct reference to the downgraded package, add one.

**Before:**
```xml
<ItemGroup>
  <PackageReference Include="PackageA" Version="1.0.0" />
  <!-- PackageA depends on PackageB >= 9.0.7, but another dependency requires 8.0.0 -->
</ItemGroup>
```

**After:**
```xml
<ItemGroup>
  <PackageReference Include="PackageA" Version="1.0.0" />
  <PackageReference Include="Microsoft.Extensions.Http" Version="9.0.7" />
</ItemGroup>
```

This explicitly tells NuGet to use the higher version.

### Option 3: Suppress NU1605 Warning (Not Recommended - Risk of Runtime Errors)
If you understand the risk and want to suppress this specific warning:

**In project file (.csproj):**
```xml
<PropertyGroup>
  <NoWarn>$(NoWarn);NU1605</NoWarn>
</PropertyGroup>
```

**Or exclude from warnings-as-errors:**
```xml
<PropertyGroup>
  <WarningsNotAsErrors>NU1605</WarningsNotAsErrors>
</PropertyGroup>
```

⚠️ **Warning**: Suppressing NU1605 may lead to runtime failures if the downgraded package is incompatible.

### Option 4: Downgrade the Dependency Package
If the higher version is not actually needed, downgrade the package that requires it (if possible).

This is less common and may not be feasible if the dependency is critical.

### Option 5: Special Case - .NET Core Runtime Packages
For specific .NET Core runtime package downgrades (e.g., System.IO.FileSystem.Primitives):

```xml
<ItemGroup>
  <PackageReference Include="Microsoft.NETCore.Targets" Version="3.0.0" PrivateAssets="all" />
</ItemGroup>
```

Use the version matching your SDK major version.

## How to Diagnose Package Downgrade Issues

### Step 1: Identify the Downgrade Chain
The error message shows the dependency chain:
```
Project -> PackageA 4.0.0 -> PackageB (>= 9.0.7)
Project -> PackageB (>= 8.0.0)
```

This tells you:
- **Direct reference**: Project directly references PackageB 8.0.0
- **Transitive requirement**: PackageA requires PackageB >= 9.0.7
- **Conflict**: Direct wins, causing downgrade from 9.0.7 → 8.0.0

### Step 2: View Full Dependency Tree
Run this command to see all dependencies:

```powershell
# .NET CLI
dotnet list package --include-transitive

# Or use NuGet
nuget dependencies MyProject.csproj
```

### Step 3: Find Which Package Requires Higher Version
Search the dependency tree for packages that depend on the downgraded package.

```powershell
# Search for specific package in dependency tree output
dotnet list package --include-transitive | Select-String "Microsoft.Extensions.Http"
```

## Automated Fix Script

```powershell
# Script to identify and suggest fixes for NU1605 package downgrades
# Run after a build that produces NU1605 warnings/errors

param(
    [Parameter(Mandatory=$true)]
    [string]$BuildLogPath
)

Write-Host "=== NU1605 Package Downgrade Analyzer ===" -ForegroundColor Cyan

if (-not (Test-Path $BuildLogPath)) {
    Write-Host "Build log not found: $BuildLogPath" -ForegroundColor Red
    exit 1
}

$logContent = Get-Content $BuildLogPath -Raw

# Extract NU1605 warnings/errors
$nu1605Pattern = "Detected package downgrade:\s+'([^']+)'\s+from\s+([\d.]+)\s+to\s+([\d.]+)"
$matches = [regex]::Matches($logContent, $nu1605Pattern)

if ($matches.Count -eq 0) {
    Write-Host "No NU1605 package downgrades detected in build log" -ForegroundColor Green
    exit 0
}

Write-Host "`nFound $($matches.Count) package downgrade(s):" -ForegroundColor Yellow

foreach ($match in $matches) {
    $packageName = $match.Groups[1].Value
    $fromVersion = $match.Groups[2].Value
    $toVersion = $match.Groups[3].Value
    
    Write-Host "`n--- Package Downgrade Detected ---" -ForegroundColor Red
    Write-Host "  Package: $packageName" -ForegroundColor Yellow
    Write-Host "  From Version: $fromVersion (required by transitive dependency)" -ForegroundColor Cyan
    Write-Host "  To Version: $toVersion (direct reference)" -ForegroundColor Cyan
    
    Write-Host "`n  RECOMMENDED FIX:" -ForegroundColor Green
    Write-Host "  Update your PackageReference to the higher version:" -ForegroundColor Green
    Write-Host "  <PackageReference Include=`"$packageName`" Version=`"$fromVersion`" />" -ForegroundColor White
}

Write-Host "`n=== Summary ===" -ForegroundColor Cyan
Write-Host "Total package downgrades: $($matches.Count)" -ForegroundColor Yellow
Write-Host "Action: Update direct package references to higher versions shown above" -ForegroundColor Green
Write-Host "Or add direct references if they don't exist" -ForegroundColor Green
```

## How to Apply This Fix

### Method 1: Manual Fix (Recommended)
1. **Read the NU1605 error message** to identify:
   - Which package is being downgraded
   - The required higher version
   - The current lower version

2. **Open your .csproj file** and find the PackageReference for the downgraded package

3. **Update the Version attribute** to match or exceed the higher version:
   ```xml
   <PackageReference Include="Microsoft.Extensions.Http" Version="9.0.7" />
   ```

4. **If the package isn't directly referenced**, add it:
   ```xml
   <ItemGroup>
     <PackageReference Include="Microsoft.Extensions.Http" Version="9.0.7" />
   </ItemGroup>
   ```

5. **Restore and rebuild:**
   ```powershell
   msbuild /t:restore "solution.sln" /v:minimal
   msbuild /t:Clean,Build "solution.sln" /v:minimal
   ```

### Method 2: Automated Analysis
1. **Capture build output to log file:**
   ```powershell
   msbuild /t:restore "solution.sln" /v:minimal > build.log 2>&1
   ```

2. **Run analysis script:**
   ```powershell
   .\analyze-nu1605.ps1 -BuildLogPath "build.log"
   ```

3. **Apply suggested fixes** from script output

### Method 3: Use NuGetSolver (Visual Studio Extension)
1. Install NuGetSolver from Visual Studio Marketplace
2. Open solution in Visual Studio
3. Run NuGetSolver to auto-detect and resolve conflicts
4. Review and apply suggested changes

## Microsoft Documentation References
- [NuGet Warning NU1605](https://learn.microsoft.com/en-us/nuget/reference/errors-and-warnings/nu1605)
- [Dependency Resolution - Direct Dependency Wins](https://learn.microsoft.com/en-us/nuget/concepts/dependency-resolution#direct-dependency-wins)
- [Suppressing NuGet Warnings](https://learn.microsoft.com/en-us/nuget/consume-packages/package-references-in-project-files#suppressing-nuget-warnings)
- [Package Versioning](https://learn.microsoft.com/en-us/nuget/concepts/package-versioning)

## Related Errors
- **NU1107**: Version conflict detected
- **NU1108**: Cycle detected in package dependencies
- **NU1109**: Transitive pinning downgrade not allowed (Central Package Management)

## Common Scenarios

### Scenario 1: Microsoft.Extensions.* Package Conflicts
Very common with .NET libraries that use different versions of Microsoft.Extensions packages.

**Fix:** Align all Microsoft.Extensions.* packages to the same version (usually latest stable).

```xml
<ItemGroup>
  <PackageReference Include="Microsoft.Extensions.DependencyInjection" Version="9.0.0" />
  <PackageReference Include="Microsoft.Extensions.Logging" Version="9.0.0" />
  <PackageReference Include="Microsoft.Extensions.Http" Version="9.0.0" />
</ItemGroup>
```

### Scenario 2: .NET Core Runtime Package Downgrades
Occurs with System.* packages in .NET Core 3.0+ projects.

**Fix:** Add Microsoft.NETCore.Targets reference.

### Scenario 3: Third-Party Package Ecosystem Conflicts
When using packages from different publishers that share common dependencies.

**Fix:** Add direct references to shared dependencies at the highest required version.

## Prevention Tips
1. **Use consistent package versions** across all projects in a solution
2. **Regularly update packages** to avoid version sprawl
3. **Use Central Package Management** (Directory.Packages.props) for multi-project solutions
4. **Check dependency trees** before adding new packages: `dotnet list package --include-transitive`
5. **Enable NU1605 warnings** during development to catch issues early

## Version Information
- **Applies to**: All NuGet package-based projects (.NET Framework, .NET Core, .NET 5+)
- **Default behavior in .NET SDK**: NU1605 treated as error
- **Can be suppressed**: Yes, but not recommended
