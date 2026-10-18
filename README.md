# OSINT Console

A terminal-based **passive intelligence console** written in Python. It gathers publicly available information about domains, IPs, usernames, phone numbers and emails from one menu, with a hacker-style interface (typing effect, loading bars, random color themes).

> Coded by **OUCHEIKH**

```
  ___  _   _  ____ _   _ _____ ___ _  ___   _
 / _ \| | | |/ ___| | | | ____|_ _| |/ / | | |
| | | | | | | |   | |_| |  _|  | || ' /| |_| |
| |_| | |_| | |___|  _  | |___ | || . \|  _  |
 \___/ \___/ \____|_| |_|_____|___|_|\_\_| |_|
```

---

## Features

| # | Command | What it does |
|---|---------|--------------|
| 01 | **DOMAIN** | DNS records (A, AAAA, MX, NS, TXT) and RDAP registration dates |
| 02 | **PORTSCAN** | TCP scan of common ports (asks for confirmation of authorization) |
| 03 | **SUBDOMAIN** | Passive subdomain enumeration from public SSL certificates (crt.sh) |
| 04 | **PHONE** | Country, carrier and timezone from an international number |
| 05 | **USERNAME** | Checks a username on 29 public sites, plus verification links for social networks |
| 06 | **IPINFO** | Geolocation, ISP and ASN of an IP or domain |
| 07 | **STATUS** | Checks that required libraries are installed |
| 08 | **HASH** | MD5 / SHA1 / SHA256 of a text |
| 09 | **EMAIL** | Format check and mail server (MX) lookup |
| 10 | **SAVE** | Saves the session output to `results.txt` |
| 11 | **EXIT** | Quits (also `exit` / `quit`) |

Type `help` (or `h`, `?`) inside the console for usage examples.

### USERNAME module

- Accepts a username **or a full name** (e.g. `john smith`). Full names are turned into common variants: `johnsmith`, `john.smith`, `john_smith`, `john-smith`, the reversed order, and initial + last name.
- Automatic check on 29 public sites (GitHub, GitLab, Dev.to, Docker Hub, PyPI, YouTube, TikTok, Snapchat, Steam, Chess.com...), 20 requests in parallel.
- Facebook, Instagram, X/Twitter, LinkedIn, Threads, Telegram and Twitch require login or block scripts, so they cannot be checked reliably. The tool prints **links to open in your browser** instead, including name-search links for Facebook, X and LinkedIn.
- A match only means an account with that name exists, not that it belongs to the person you are looking for. Always verify manually.

### Interface

- Typing effect banner and welcome message
- Green loading bars
- 5 random color themes at each launch: `matrix`, `cyber`, `neon`, `gold`, `blood`
- Custom prompt: `oucheikh@osint:~$`
- Command history with Up/Down arrows (saved in `~/.osint_console_history`)
- Terminal bell on each command

---

## Installation

Requires **Python 3.8+**.

Download the repository (**Code > Download ZIP**), extract it, open a terminal in the folder, then:

```bash
pip install -r requirements.txt
python osint_console.py
```

On Windows, install `pyreadline3` as well if you want command history:

```bash
pip install pyreadline3
```

### Dependencies

`rich`, `requests`, `dnspython`, `phonenumbers`

---

## Usage example

```
oucheikh@osint:~$ 6
IP / domain: 8.8.8.8
...
oucheikh@osint:~$ 10
Saved to results.txt
```

---

## Notes and limitations

- Uses only public sources: DNS, RDAP, crt.sh, ip-api.com and public profile pages. It does not log in anywhere and does not bypass any protection.
- External services can be rate-limited or unavailable; some sites may show `BLOCKED` or `ERR`.
- Site layouts change over time, so some username checks may need updating.
- PHONE only returns metadata (country, carrier, timezone), never the owner's identity or exact location.

---

## Legal disclaimer

This tool is for **educational purposes and authorized security research** only.

- Use PORTSCAN only on systems you own or have explicit written permission to test. Scanning other people's systems without permission may be illegal.
- Respect privacy laws and the terms of service of the websites you query.
- The author is not responsible for any misuse of this tool.

---


## Author

**OUCHEIKH**
