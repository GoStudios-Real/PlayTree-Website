# Microsoft Store / Partner Center Checklist

## Before packaging
- [ ] Run `build_playtree.bat` and verify `dist\PLAYTREE.exe` works.
- [ ] Create Store assets: icon 300x300, screenshots, trailer (optional).
- [ ] Have a Microsoft Partner Center developer account.

## MSIX package
- [ ] Install MSIX Packaging Tool (Microsoft Store).
- [ ] Create package from `dist\PLAYTREE.exe`.
- [ ] Use `AppxManifest.xml.template` as reference for identity/capabilities.
- [ ] Publisher must match Partner Center `CN=...`.
- [ ] Sign MSIX with a trusted certificate for sideloading; Microsoft re-signs MSIX packages accepted for Store distribution.

## Partner Center submission
- [ ] Reserve app name: PLAYTREE.
- [ ] Choose the package that is actually being submitted. `dist\PLAYTREE.exe` is the game executable, not an installer; do not submit it as an EXE installer.
- [ ] Pricing: Free.
- [ ] Category: Games > Action & adventure / RPG.
- [ ] Upload listing copy from `chrome_ext/store_description.txt`.
- [ ] Upload screenshots, icons, age rating questionnaire.
- [ ] Select device families (Windows Desktop; Xbox only if certified).
- [ ] Submit for certification.

## Miscellaneous install failure scenarios

### PLAYTREE package-specific answer

The current build script produces a portable PyInstaller game executable (`dist\PLAYTREE.exe`); this repository does not build an EXE setup/bootstrapper or define installer exit codes. For the current binary, enter **N/A — not an installer; no install return-code contract**. Do not claim that generic MSI codes below are PLAYTREE EXE return codes.

For a Store submission, package the game as MSIX and use package/deployment diagnostics, or create and test a real signed EXE installer before selecting the EXE-installer path. Microsoft requires MSI/EXE installers submitted to the Store to be Authenticode-signed; the Store does not re-sign those installer files. See [App package requirements for MSIX apps](https://learn.microsoft.com/en-us/windows/apps/publish/publish-your-app/msix/app-package-requirements).

### Generic Windows Installer reference (only if the submitted installer uses MSI)

These are standard Windows Installer values, **not verified return values from a PLAYTREE EXE installer**. An EXE bootstrapper can define different codes; use its own vendor documentation and tested behavior instead.

| Scenario | Windows Installer value | Meaning / Partner Center note | Documentation |
| --- | ---: | --- | --- |
| Installation succeeds | `0` | Success. | [Windows Installer error codes](https://learn.microsoft.com/en-us/windows/win32/msi/error-codes) |
| User cancels | `1602` | Installation canceled by the user. | [Windows Installer error codes](https://learn.microsoft.com/en-us/windows/win32/msi/error-codes) |
| Generic fatal installation error | `1603` | Fatal error; inspect the installer log for the actual cause. | [Windows Installer error codes](https://learn.microsoft.com/en-us/windows/win32/msi/error-codes) |
| Another installation is already running | `1618` | Retry after the other installation completes. | [Windows Installer error codes](https://learn.microsoft.com/en-us/windows/win32/msi/error-codes) |
| Installer package cannot be opened | `1619` | Verify package path/accessibility and package validity. | [Windows Installer error codes](https://learn.microsoft.com/en-us/windows/win32/msi/error-codes) |
| Temporary folder is full or inaccessible | `1632` | Resolve temp-folder space or access, then retry. | [Windows Installer error codes](https://learn.microsoft.com/en-us/windows/win32/msi/error-codes) |
| Package is unsupported on this platform | `1633` | Submit a compatible architecture/OS package. | [Windows Installer error codes](https://learn.microsoft.com/en-us/windows/win32/msi/error-codes) |
| Restart required after successful install | `3010` | Success, reboot required; not an installation failure. | [Windows Installer error codes](https://learn.microsoft.com/en-us/windows/win32/msi/error-codes) |
| Installer initiated a restart | `1641` | Success; the installer initiated a reboot. | [Windows Installer error codes](https://learn.microsoft.com/en-us/windows/win32/msi/error-codes) |

Microsoft documents that `msiexec.exe` returns installer/system error levels in [Standard Installer command-line options](https://learn.microsoft.com/en-us/windows/win32/msi/standard-installer-command-line-options). Do not enter the MSI table as the EXE return-code map unless the actual EXE installer is verified to pass those values through.

## Xbox note
Full Xbox console Store availability requires Xbox certification and a compatible package. Desktop MSIX is the easiest starting point; test with Xbox Dev Mode before targeting console certification.