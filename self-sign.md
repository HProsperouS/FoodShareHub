# mkcert Instructions

Note: mkcert doesn't work for Firefox users.

---

## Installing mkcert

---

First install mkcert, for cert signing

### Windows

#### Installing chocolatey

Note: To check if you've installed chocolatey, just run

```
> choco
Chocolatey v1.1.0
Please run 'choco -?' or 'choco <command> -?' for help menu.
```

1. Run the command below in PowerShell (run as administrator!)

```
Get-ExecutionPolicy
```

1. If the command above in step 1 returns "Restricted", run the command below. Otherwise, skip to step 3.

```
Set-ExecutionPolicy AllSigned
```

1. Run this command below to install chocolatey or go to the [website](https://chocolatey.org/install "‌") itself under individual and copy the command there

```
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

1. Install mkcert using chocolatey

```
choco install mkcert
```

### Linux

1. Install the libraries needed for homebrew on Linux (part 1)
   1. For obvious reasons, use aptitude for debian distro & yum for redhat distros

```
sudo apt install libnss3-tools
    -or-
sudo yum install nss-tools
    -or-
sudo pacman -S nss
    -or-
sudo zypper install mozilla-nss-tools
```

1. Install the libraries needed for homebrew on Linux (part 2)
   - Debian or Ubuntu

```
sudo apt-get install build-essential procps curl file git
```

```
- Fedora, CentOS, or Red Hat
```

```
sudo yum groupinstall 'Development Tools'
sudo yum install procps-ng curl file git
sudo yum install libxcrypt-compat # needed by Fedora 30 and up
```

1. Install homebrew itself!

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

1. Add to PATH

```
export PATH="/home/linuxbrew/.linuxbrew/bin:$PATH"
```

1. Install mkcert

```
brew install mkcert
```

### MacOS

1. Use homebrew to install mkcert, if dont have homebrew install urself

```
brew install mkcert
brew install nss # if you use Firefox
```

---

### mkcert Commands to execute

---

1. Ensure you're in the right directory to avoid being a huge clown
   1. cd C:\ for windows
   2. cd for linux / UNIX based operating systems
2. Generate the certificate and the private key (in the pwd) in powershell or terminal

```
mkcert -key-file app-private-key.pem -cert-file app-cert.pem -ecdsa localhost 127.0.0.1 ::1
```

1. Configure your computer to trust the certificate to place it in certificate trust store, important as trust store relies on the client machine to have this certificate approved, u can view this in mmc certificates

```
mkcert -install
```

1. Place the certificate and private key with the [main.py](http://main.py "‌") as shown in the screenshot below

[![image.png](/res/self-sign.png)](/res/self-sign.png)
