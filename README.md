# lastf

[![Latest Release](https://img.shields.io/github/release/xeyossr/lastf.svg?style=for-the-badge)](https://github.com/xeyossr/lastf/releases)
[![Software License](https://img.shields.io/badge/License-GPLv3-blue.svg?style=for-the-badge)](/LICENSE)

Better `last` command interface with structured output.

![lastf_long-date](/lastf_long-date.png)
![lastf](/lastf.png)

## Installation

### Packages

- Arch Linux: `yay -S lastf`

### From source

```bash
git clone https://github.com/xeyossr/lastf.git
cd lastf
chmod +x build.sh && ./build.sh
```

## Usage

You can simply run lastf without any command-line arguments:

```bash
lastf
```

If you prefer to see date entries in the **long format** (`May 05, 2025 13:24`) instead of the **ISO 8601 format** (`2025-05-05 13:24`), start the program with the `--long-date` flag:

```bash
lastf --long-date
```
