## 🛠️ Troubleshooting & Alternative Environments

### Experiencing Windows Freezes or C-Drive Bloat?
During development, the standard **Docker Desktop for Windows** installation caused severe system instability, installation script freezes, and aggressively consumed gigabytes of storage on the `C:` drive. 

If you are experiencing similar issues, this project has been fully tested and verified running on a **Server-Style Static Binary** setup isolated entirely on a secondary drive (`D:`).

#### My Stable Environment:
* **Docker Engine (Server):** v29.6.0 (Static Binaries)
* **Docker CLI (Client):** v29.6.0
* **Storage Location:** `D:\Docker\` (Zero `C:` drive dependency)

#### How to replicate this lean setup:
If you want to ditch Docker Desktop and move to high-performance standalone binaries:
1. Completely uninstall Docker Desktop.
2. Download the official Docker Static Binaries for Windows.
3. Extract them to your preferred drive (e.g., `D:\Docker\`).
4. Register `dockerd.exe` as a native Windows Service.
5. Add the directory to your System PATH so you can use `docker` commands directly in PowerShell.

*This stripped-away GUI wrapper approach drastically lowers RAM usage and eliminates Windows subsystem conflicts.*