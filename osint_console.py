#!/usr/bin/env python3
"""
OSINT Console - passive intelligence tool (educational)
Install: pip install rich requests dnspython phonenumbers
Use only on targets you own or are authorized to test.
"""
import os
import random
import socket
import time
import requests
from concurrent.futures import ThreadPoolExecutor
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.theme import Theme
from rich.progress import Progress, BarColumn, TextColumn, track

PALETTES = {
    "matrix": ("bright_green", "green"),
    "cyber": ("bright_cyan", "cyan"),
    "neon": ("bright_magenta", "magenta"),
    "gold": ("bright_yellow", "yellow"),
    "blood": ("bright_red", "red"),
}
THEME_NAME = random.choice(list(PALETTES))
_main, _acc = PALETTES[THEME_NAME]
console = Console(record=True, theme=Theme({
    "main": _main, "mainb": f"bold {_main}",
    "accent": _acc, "accentb": f"bold {_acc}",
}))

HISTORY_FILE = os.path.expanduser("~/.osint_console_history")
try:
    import readline
except ImportError:
    readline = None
UA = {"User-Agent": "Mozilla/5.0"}

BANNER = r"""
  ___  _   _  ____ _   _ _____ ___ _  ___   _
 / _ \| | | |/ ___| | | | ____|_ _| |/ / | | |
| | | | | | | |   | |_| |  _|  | || ' /| |_| |
| |_| | |_| | |___|  _  | |___ | || . \|  _  |
 \___/ \___/ \____|_| |_|_____|___|_|\_\_| |_|
"""

SKULL = r"""
        _____
      /       \
     |  ()  () |
      \   ^   /
       | VVV |
        \___/
"""

AUTHOR = "Coded by OUCHEIKH"
USER = "oucheikh"

MENU = [
    ("01", "DOMAIN", "Domain / RDAP / DNS information"),
    ("02", "PORTSCAN", "Authorized TCP port scanning"),
    ("03", "SUBDOMAIN", "Passive subdomain enumeration (crt.sh)"),
    ("04", "PHONE", "Phone-number metadata"),
    ("05", "USERNAME", "Public username presence check"),
    ("06", "IPINFO", "IP / ASN / ISP / geo metadata"),
    ("07", "STATUS", "Module and dependency status"),
    ("08", "HASH", "MD5 / SHA1 / SHA256 of a text"),
    ("09", "EMAIL", "Email format + mail server (MX) check"),
    ("10", "SAVE", "Save session output to results.txt"),
    ("11", "EXIT", "Close console"),
]


def typewrite(text, style="accent", delay=0.002):
    """Print text char by char (typing effect)."""
    for ch in text:
        console.print(ch, end="", style=style, markup=False, highlight=False)
        console.file.flush()
        time.sleep(delay)
    console.print()


def loading(msg="Loading", steps=30, delay=0.03):
    """Green loading bar."""
    with Progress(TextColumn("[main]{task.description}"),
                  BarColumn(complete_style="accent", finished_style="main"),
                  TextColumn("[accent]{task.percentage:>3.0f}%"),
                  console=console, transient=True) as p:
        t = p.add_task(msg, total=steps)
        for _ in range(steps):
            time.sleep(delay)
            p.advance(t)


def show_menu():
    typewrite(BANNER, "mainb", 0.002)
    for line in SKULL.splitlines():
        console.print(line, style="accent", markup=False, highlight=False)
        time.sleep(0.05)
    typewrite("        " + AUTHOR, "mainb", 0.03)
    typewrite(f"\n  Welcome {USER}_", "accentb", 0.04)
    console.print()
    console.print(Panel("OUCHEIKH  //  PASSIVE INTELLIGENCE CONSOLE\n"
                        "DOMAIN • DNS • PORTS • SUBDOMAINS • USERNAME • PHONE",
                        border_style="accent"))
    t = Table(title="COMMAND MATRIX", border_style="accent")
    t.add_column("#", style="main")
    t.add_column("CMD", style="bold")
    t.add_column("Description", style="accent")
    for row in MENU:
        t.add_row(*row)
    console.print(t)
    console.print("[accent]Type [main]help[/] for details  |  theme: " + THEME_NAME + "[/]")


def domain():
    import dns.resolver
    d = console.input("[main]Domain:[/] ").strip()
    for rtype in ("A", "AAAA", "MX", "NS", "TXT"):
        try:
            ans = dns.resolver.resolve(d, rtype, lifetime=5)
            for r in ans:
                console.print(f"[green]{rtype:5}[/] {r.to_text()}")
        except Exception:
            console.print(f"[red]{rtype:5}[/] -")
    try:
        r = requests.get(f"https://rdap.org/domain/{d}", timeout=10, headers=UA).json()
        console.print("\n[bold]RDAP[/]")
        for e in r.get("events", []):
            console.print(f"  {e.get('eventAction')}: {e.get('eventDate')}")
        console.print(f"  Status: {', '.join(r.get('status', []))}")
    except Exception as e:
        console.print(f"[red]RDAP error:[/] {e}")


def portscan():
    host = console.input("[main]Host (only if authorized):[/] ").strip()
    ok = console.input("[yellow]Do you own / have permission? (y/n):[/] ").lower()
    if ok != "y":
        console.print("[red]Aborted.[/]")
        return
    ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 8080]

    def check(p):
        with socket.socket() as s:
            s.settimeout(1)
            return p, s.connect_ex((host, p)) == 0

    with ThreadPoolExecutor(20) as ex:
        for p, is_open in track(ex.map(check, ports), total=len(ports),
                                description="Scanning", console=console):
            if is_open:
                console.print(f"[green]OPEN[/] {p}")
    console.print("Scan done.")


def subdomain():
    d = console.input("[main]Domain:[/] ").strip()
    try:
        r = requests.get(f"https://crt.sh/?q=%25.{d}&output=json", timeout=30, headers=UA)
        subs = set()
        for e in r.json():
            for n in e["name_value"].split("\n"):
                subs.add(n.strip().lstrip("*."))
        for s in sorted(subs):
            console.print(f"[green]•[/] {s}")
        console.print(f"[bold]{len(subs)} found[/]")
    except Exception as e:
        console.print(f"[red]Error:[/] {e}")


def phone():
    import phonenumbers
    from phonenumbers import carrier, geocoder, timezone
    n = console.input("[main]Number (+212...):[/] ").strip()
    try:
        p = phonenumbers.parse(n)
        console.print(f"Valid    : {phonenumbers.is_valid_number(p)}")
        console.print(f"Country  : {geocoder.description_for_number(p, 'en')}")
        console.print(f"Carrier  : {carrier.name_for_number(p, 'en') or '-'}")
        console.print(f"Timezone : {', '.join(timezone.time_zones_for_number(p))}")
    except Exception as e:
        console.print(f"[red]Error:[/] {e}")


# name: (url, mode, marker)
#   mode "status": 200 = found, 404 = not found
#   mode "text"  : 200 + marker text on page = NOT found
USER_SITES = {
    "GitHub": ("https://github.com/{}", "status", None),
    "GitLab": ("https://gitlab.com/{}", "status", None),
    "Codeberg": ("https://codeberg.org/{}", "status", None),
    "DockerHub": ("https://hub.docker.com/u/{}", "status", None),
    "PyPI": ("https://pypi.org/user/{}/", "status", None),
    "Dev.to": ("https://dev.to/{}", "status", None),
    "Medium": ("https://medium.com/@{}", "status", None),
    "Replit": ("https://replit.com/@{}", "status", None),
    "Keybase": ("https://keybase.io/{}", "status", None),
    "Gravatar": ("https://gravatar.com/{}", "status", None),
    "About.me": ("https://about.me/{}", "status", None),
    "Behance": ("https://www.behance.net/{}", "status", None),
    "Dribbble": ("https://dribbble.com/{}", "status", None),
    "Flickr": ("https://www.flickr.com/people/{}", "status", None),
    "SoundCloud": ("https://soundcloud.com/{}", "status", None),
    "Vimeo": ("https://vimeo.com/{}", "status", None),
    "Pinterest": ("https://www.pinterest.com/{}/", "status", None),
    "Pastebin": ("https://pastebin.com/u/{}", "status", None),
    "Spotify": ("https://open.spotify.com/user/{}", "status", None),
    "Reddit": ("https://www.reddit.com/user/{}/", "status", None),
    "Steam": ("https://steamcommunity.com/id/{}", "text",
              "The specified profile could not be found"),
    "HackerNews": ("https://news.ycombinator.com/user?id={}", "text",
                   "No such user"),
    "Chess.com": ("https://www.chess.com/member/{}", "status", None),
    "Lichess": ("https://lichess.org/@/{}", "status", None),
    "YouTube": ("https://www.youtube.com/@{}", "status", None),
    "TikTok": ("https://www.tiktok.com/@{}", "status", None),
    "Snapchat": ("https://www.snapchat.com/add/{}", "status", None),
    "Tumblr": ("https://{}.tumblr.com", "status", None),
    "Wikipedia": ("https://en.wikipedia.org/wiki/User:{}", "status", None),
}


# Sites that hide profiles behind a login wall or block scripts: we cannot
# check them reliably, so we give links to open and verify manually.
# {} = username variant, {q} = the full name typed, URL-encoded.
SOCIAL_MANUAL = {
    "Facebook": ["https://www.facebook.com/{}",
                 "https://www.facebook.com/search/people/?q={q}"],
    "Instagram": ["https://www.instagram.com/{}/"],
    "X / Twitter": ["https://x.com/{}",
                    "https://x.com/search?q={q}&f=user"],
    "LinkedIn": ["https://www.linkedin.com/in/{}",
                 "https://www.linkedin.com/search/results/people/?keywords={q}"],
    "Threads": ["https://www.threads.net/@{}"],
    "Telegram": ["https://t.me/{}"],
    "Twitch": ["https://www.twitch.tv/{}"],
}


def check_user(item, u):
    name, (url, mode, marker) = item
    link = url.format(u)
    try:
        r = requests.get(link, timeout=8, headers=UA, allow_redirects=True)
    except requests.RequestException:
        return name, link, "ERR"
    if r.status_code in (403, 429):
        return name, link, "BLOCKED"
    if mode == "status":
        if r.status_code == 200:
            return name, link, "FOUND"
        return name, link, "NO" if r.status_code == 404 else "ERR"
    if r.status_code != 200:
        return name, link, "NO" if r.status_code == 404 else "ERR"
    return name, link, "NO" if marker in r.text else "FOUND"


def make_variants(raw):
    """'yahya oucheikh' -> yahyaoucheikh, yahya.oucheikh, ... (max 10)."""
    words = [w for w in raw.lower().split() if w]
    if len(words) == 1:
        return words
    out = []
    for order in (words, words[::-1]):
        for sep in ("", ".", "_", "-"):
            out.append(sep.join(order))
    out.append(words[0][0] + words[-1])  # initial + last name
    seen = []
    for v in out:
        if v not in seen:
            seen.append(v)
    return seen[:10]


def username():
    import re
    raw = console.input("[main]Username (or full name):[/] ").strip()
    words = raw.split()
    if not raw or len(words) > 3 or not all(
            re.fullmatch(r"[\w.\-]{1,30}", w) for w in words):
        console.print("[red]Use letters, digits, _ . - (max 3 words)[/]")
        return
    variants = make_variants(raw)
    if len(variants) > 1:
        console.print(f"[accent]Trying {len(variants)} variants: "
                      f"{', '.join(variants)}[/]")
    jobs = [(it, v) for v in variants for it in USER_SITES.items()]
    with ThreadPoolExecutor(20) as ex:
        results = list(track(
            ex.map(lambda j: check_user(j[0], j[1]) + (j[1],), jobs),
            total=len(jobs), description="Checking sites", console=console))
    order = {"FOUND": 0, "BLOCKED": 1, "ERR": 2, "NO": 3}
    results.sort(key=lambda r: (order[r[2]], r[3], r[0]))
    colors = {"FOUND": "green", "NO": "dim", "BLOCKED": "yellow", "ERR": "yellow"}
    t = Table(title=f"USERNAME: {raw}", border_style="accent")
    t.add_column("Site", style="main")
    t.add_column("Result")
    if len(variants) > 1:
        t.add_column("Variant", style="accent")
    t.add_column("URL", style="accent", overflow="fold")
    for name, link, res, var in results:
        if res == "NO":
            continue
        row = [name, f"[{colors[res]}]{res}[/]"]
        if len(variants) > 1:
            row.append(var)
        row.append(link)
        t.add_row(*row)
    console.print(t)
    found = sum(r[2] == "FOUND" for r in results)
    blocked = sum(r[2] in ("BLOCKED", "ERR") for r in results)
    console.print(f"[main]{found} found[/] / {len(results)} checks"
                  f"  ({blocked} blocked or unreachable - verify manually)")
    from urllib.parse import quote_plus
    m = Table(title="OPEN IN BROWSER TO VERIFY (login required / bot-blocked)",
              border_style="accent")
    m.add_column("Site", style="main")
    m.add_column("Links", style="accent", overflow="fold")
    for site, templates in SOCIAL_MANUAL.items():
        links = []
        for tpl in templates:
            if "{q}" in tpl:
                links.append(tpl.replace("{q}", quote_plus(raw)))
            else:
                links += [tpl.format(v) for v in variants[:3]]
        m.add_row(site, "\n".join(links))
    console.print(m)
    console.print("[dim]A match only means an account with that name exists, "
                  "not that it is the same person.[/]")


def ipinfo():
    ip = console.input("[main]IP / domain:[/] ").strip()
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=10).json()
        for k in ("query", "country", "regionName", "city", "isp", "org", "as", "timezone"):
            console.print(f"{k:11}: {r.get(k)}")
    except Exception as e:
        console.print(f"[red]Error:[/] {e}")


def hashing():
    import hashlib
    t = console.input("[main]Text:[/] ").encode()
    for name in ("md5", "sha1", "sha256"):
        console.print(f"{name.upper():7}: {hashlib.new(name, t).hexdigest()}")


def email():
    import re
    import dns.resolver
    e = console.input("[main]Email:[/] ").strip()
    if not re.fullmatch(r"[\w.+-]+@[\w-]+(\.[\w-]+)+", e):
        console.print("[red]Invalid format[/]")
        return
    console.print("[green]Format OK[/]")
    dom = e.split("@")[1]
    try:
        for r in dns.resolver.resolve(dom, "MX", lifetime=5):
            console.print(f"[green]MX[/] {r.to_text()}")
    except Exception:
        console.print("[red]No mail server found for this domain[/]")


def save():
    console.save_text("results.txt")
    console.print("[green]Saved to results.txt[/]")


def help_cmd():
    t = Table(title="HELP", border_style="accent")
    t.add_column("CMD", style="main")
    t.add_column("Usage / example", style="accent")
    rows = [
        ("1  DOMAIN", "Enter a domain, e.g. example.com -> DNS + RDAP dates"),
        ("2  PORTSCAN", "Enter a host you OWN, e.g. 127.0.0.1 -> open ports"),
        ("3  SUBDOMAIN", "Enter a domain -> subdomains found in SSL certs"),
        ("4  PHONE", "Enter intl number, e.g. +212600000000 -> country, carrier"),
        ("5  USERNAME", "Enter a username -> which public sites have it"),
        ("6  IPINFO", "Enter IP or domain -> geo / ISP / ASN"),
        ("7  STATUS", "Check that required libraries are installed"),
        ("8  HASH", "Enter text -> MD5 / SHA1 / SHA256"),
        ("9  EMAIL", "Enter email -> format check + MX records"),
        ("10 SAVE", "Write the session output to results.txt"),
        ("11 EXIT", "Quit (also: exit / quit)"),
        ("history", "Use Up/Down arrows to bring back previous commands"),
    ]
    for r in rows:
        t.add_row(*r)
    console.print(t)


def status():
    for mod in ("requests", "dns.resolver", "phonenumbers", "rich"):
        try:
            __import__(mod)
            console.print(f"[green]OK     [/] {mod}")
        except ImportError:
            console.print(f"[red]MISSING[/] {mod}")


ACTIONS = {"1": domain, "2": portscan, "3": subdomain, "4": phone,
           "5": username, "6": ipinfo, "7": status,
           "8": hashing, "9": email, "10": save,
           "help": help_cmd, "h": help_cmd, "?": help_cmd}


def main():
    if readline:
        try:
            readline.read_history_file(HISTORY_FILE)
        except OSError:
            pass
    loading("Initializing modules")
    show_menu()
    while True:
        c = console.input("\n[accentb]oucheikh@osint[/][white]:~$ [/]").strip().lstrip("0")
        if c in ("11", "exit", "quit"):
            break
        fn = ACTIONS.get(c)
        if fn:
            console.bell()
            loading("Running", 15, 0.02)
            fn()
        else:
            console.print("[red]Invalid option[/]")


if __name__ == "__main__":
    try:
        main()
    finally:
        if readline:
            try:
                readline.write_history_file(HISTORY_FILE)
            except OSError:
                pass
