# TEMPLATE — copy to $HOME\.snowflake\payer-env.ps1 and fill in the placeholders.
# The real file lives outside the repo. Run at the start of each session:  . $HOME\.snowflake\payer-env.ps1

$env:SNOWFLAKE_ACCOUNT          = "<ACCOUNT_IDENTIFIER>"
$env:SNOWFLAKE_USER             = "<ADMIN_USER>"
$env:SNOWFLAKE_ROLE             = "SYSADMIN"
$env:SNOWFLAKE_WAREHOUSE        = "COMPUTE_WH"
$env:SNOWFLAKE_AUTHENTICATOR    = "snowflake_jwt"
$env:SNOWFLAKE_PRIVATE_KEY_PATH = "$HOME\.snowflake\keys\rsa_key.p8"

$s = Read-Host "Private key passphrase" -AsSecureString
$plain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($s))
$env:SNOWFLAKE_PRIVATE_KEY_PASSPHRASE = $plain
$env:PRIVATE_KEY_PASSPHRASE           = $plain
Remove-Variable s, plain

Write-Host "Snowflake env set: $($env:SNOWFLAKE_USER) @ $($env:SNOWFLAKE_ACCOUNT), role $($env:SNOWFLAKE_ROLE)"