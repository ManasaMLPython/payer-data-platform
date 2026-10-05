# Runbook — Snowflake access

- **Ticket:** PAYER-14
- **Account:** `<ACCOUNT_IDENTIFIER>` · Enterprise · AWS us-east-2 (Ohio)
- **Admin user:** `<ADMIN_USER>` — web login with password + MFA; tools use key-pair authentication

## Key pair (one-time setup)
Keys live in `C:\Users\<you>\.snowflake\keys\` — outside the repo, never committed.

In Git Bash (`bind 'set enable-bracketed-paste off'` first if pasting adds stray characters):
```bash
mkdir -p ~/.snowflake/keys && cd ~/.snowflake/keys
openssl genrsa -out rsa_key_tmp.pem 2048
winpty openssl pkcs8 -topk8 -v2 aes256 -inform PEM -in rsa_key_tmp.pem -out rsa_key.p8   # sets passphrase
rm rsa_key_tmp.pem                                                                       # delete unencrypted key
winpty openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub
grep -v "PUBLIC KEY" rsa_key.pub | tr -d '\n'; echo                                      # one-line public key
```
`winpty` is needed for commands that prompt for a passphrase, and cannot be used with a pipe.

## Register the public key
```sql
USE ROLE SECURITYADMIN;
ALTER USER <ADMIN_USER> SET RSA_PUBLIC_KEY='<one-line public key>';
DESC USER <ADMIN_USER>;   -- note RSA_PUBLIC_KEY_FP
```
Verify the fingerprint locally — it must equal the value after `SHA256:`:
```bash
openssl rsa -pubin -in rsa_key.pub -outform DER | openssl dgst -sha256 -binary | openssl enc -base64
```

## Snowflake CLI connection
```powershell
snow connection add --connection-name payer_admin --account <ACCOUNT_IDENTIFIER> --user <ADMIN_USER> `
  --role ACCOUNTADMIN --warehouse COMPUTE_WH --authenticator SNOWFLAKE_JWT `
  --private-key-file "C:\Users\<you>\.snowflake\keys\rsa_key.p8" --no-interactive
snow connection set-default payer_admin
```

## Every new terminal session
```powershell
$s = Read-Host "Private key passphrase" -AsSecureString
$env:PRIVATE_KEY_PASSPHRASE = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($s))
snow connection test
```
The passphrase lives only in that terminal's memory.

## Key rotation
Snowflake allows two public keys per user (`RSA_PUBLIC_KEY` and `RSA_PUBLIC_KEY_2`): register the new key as `RSA_PUBLIC_KEY_2`, switch tools to the new private key, then unset the old one. No downtime.

## Troubleshooting
| Symptom | Cause / fix |
|---|---|
| `^[[200~` or `~mkdir: command not found` in Git Bash | Bracketed paste — right-click paste, or `bind 'set enable-bracketed-paste off'` |
| `stdin is not a tty` | `winpty` used with a pipe — run the steps separately |
| JWT token invalid | Public key mis-pasted — compare fingerprints |
| Passphrase / decrypt error | `PRIVATE_KEY_PASSPHRASE` not set in this terminal session |