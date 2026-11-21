# Run as Administrator in PowerShell on Windows 11.
# Replace CN with your Partner Center Publisher value before Store submission.
param(
  [string]$Publisher = "CN=REPLACE_WITH_PARTNER_CENTER_PUBLISHER",
  [string]$MsixPath = ".\PLAYTREE.msix",
  [string]$PfxPath = ".\PLAYTREE_Test.pfx",
  [string]$PfxPassword = "testpass"
)

$cert = New-SelfSignedCertificate -Type Custom -Subject $Publisher -KeyUsage DigitalSignature -FriendlyName "PLAYTREE Test Cert" -CertStoreLocation Cert:\CurrentUser\My
$sec = ConvertTo-SecureString -String $PfxPassword -Force -AsPlainText
Export-PfxCertificate -Cert $cert -FilePath $PfxPath -Password $sec | Out-Null

signtool sign /fd SHA256 /f $PfxPath /p $PfxPassword $MsixPath
Write-Host "Signed $MsixPath"