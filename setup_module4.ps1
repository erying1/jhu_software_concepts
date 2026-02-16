# PowerShell script to set up Module 4 folder structure
# Run this from your jhu_software_concepts directory

Write-Host "Setting up Module 4 folder structure..." -ForegroundColor Cyan
Write-Host ""

# Create module_4 directory
if (-not (Test-Path "module_4")) {
    New-Item -ItemType Directory -Path "module_4" | Out-Null
    Write-Host "Created module_4/" -ForegroundColor Green
} else {
    Write-Host "module_4/ already exists" -ForegroundColor Yellow
}

# Create subdirectories
$directories = @(
    "module_4/src",
    "module_4/src/app",
    "module_4/src/app/templates",
    "module_4/tests",
    "module_4/docs",
    ".github",
    ".github/workflows"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "Created $dir/" -ForegroundColor Green
    } else {
        Write-Host "$dir/ already exists" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Folder structure created!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Copy Module 3 code to module_4/src/" -ForegroundColor White
Write-Host "2. Run: .\copy_module3_to_module4.ps1" -ForegroundColor White
Write-Host ""
