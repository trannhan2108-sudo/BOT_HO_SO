
Param(
  [Parameter(Mandatory=$true)]
  [string]$RepoPath  # ví dụ: 'F:\CTY TN\AI Automation\HO_SO_BOT'
)

$ErrorActionPreference = 'Stop'

# 1) Tạo thư mục chuẩn
New-Item -Force -ItemType Directory -Path "$RepoPath\mapping\archive" | Out-Null
New-Item -Force -ItemType Directory -Path "$RepoPath\code\HO_SO_BOT\templates\_ACTIVE" | Out-Null
New-Item -Force -ItemType Directory -Path "$RepoPath\code\HO_SO_BOT\templates\_ARCHIVE" | Out-Null
New-Item -Force -ItemType Directory -Path "$RepoPath\decision_log" | Out-Null

# 2) Mapping: chọn bản cuối -> đổi tên thành placeholder_mapping_ACTIVE.xlsx
$mappingCandidates = @(
  "$RepoPath\mapping\FINAL_placeholder_catalog.xlsx",
  "$RepoPath\code\HO_SO_BOT\mapping\FINAL_placeholder_catalog.xlsx",
  "$RepoPath\mapping\placeholder_mapping_FINAL.xlsx",
  "$RepoPath\mapping\placeholder_mapping_FINAL.xlsx"
) | Where-Object { Test-Path $_ }

if ($mappingCandidates.Count -gt 0) {
  Copy-Item -Force $mappingCandidates[0] "$RepoPath\mapping\placeholder_mapping_ACTIVE.xlsx"
}

# 3) Decision Log: giữ 1 bản ở gốc
$dl1 = "$RepoPath\decision_log\DECISION_LOG.yaml"
$dl2 = "$RepoPath\code\HO_SO_BOT\decision_log\DECISION_LOG.yaml"
if (Test-Path $dl2) {
  Copy-Item -Force $dl2 $dl1
}

# 4) Templates: move 5 file vào _ACTIVE và chuẩn hóa tên
$tplRoot = "$RepoPath\code\HO_SO_BOT\templates"
$active = "$tplRoot\_ACTIVE"

$map = @{
  "1." = "1. Mẫu hợp đồng cung cấp, lắp đặt_READY.docx";
  "2." = "2. Mẫu bảng chi tiết vật tư_READY.xlsx";
  "3." = "3. Mẫu biên bản nghiệm thu_READY.docx";
  "4." = "4. Mẫu BB thanh lý HĐ_READY.docx";
  "5." = "5. Mẫu đề nghị thanh toán_READY.docx";
}

Get-ChildItem $tplRoot -File | ForEach-Object {
  $name = $_.Name
  foreach ($k in $map.Keys) {
    if ($name.StartsWith($k)) {
      $new = Join-Path $active $map[$k]
      Copy-Item -Force $_.FullName $new
    }
  }
}

Write-Host "Done. Active mapping & templates prepared."
