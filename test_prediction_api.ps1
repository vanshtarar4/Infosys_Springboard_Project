# PowerShell test script for fraud prediction API

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Fraud Prediction API - Test Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Test 1: High-risk transaction
Write-Host "`n1. Testing HIGH-RISK transaction (large amount, new account):" -ForegroundColor Yellow
$body1 = @{
    customer_id = "C12345"
    kyc_verified = 0
    account_age_days = 5
    transaction_amount = 95000
    channel = "Online"
    timestamp = "2025-09-12 14:30"
} | ConvertTo-Json

$response1 = Invoke-RestMethod -Uri "http://localhost:8001/api/predict" -Method POST -Body $body1 -ContentType "application/json"
$response1 | ConvertTo-Json -Depth 10

# Test 2: Low-risk transaction
Write-Host "`n2. Testing LOW-RISK transaction (small amount, established account):" -ForegroundColor Yellow
$body2 = @{
    customer_id = "C67890"
    kyc_verified = 1
    account_age_days = 500
    transaction_amount = 250
    channel = "POS"
    timestamp = "2025-09-12 10:15"
} | ConvertTo-Json

$response2 = Invoke-RestMethod -Uri "http://localhost:8001/api/predict" -Method POST -Body $body2 -ContentType "application/json"
$response2 | ConvertTo-Json -Depth 10

# Test 3: Get prediction history
Write-Host "`n3. Fetching prediction history:" -ForegroundColor Yellow
$history = Invoke-RestMethod -Uri "http://localhost:8001/api/predictions/history?limit=5" -Method GET
$history | ConvertTo-Json -Depth 10

Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "Tests complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
