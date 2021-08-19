#!/usr/bin/python3
"""
hack_the_box_start.py

a good way to start a hack the box machine. this script sets up the directory structure
for the pen test. it also starts some automated scans with some default parameters.

writen with python version 3.9.6 on arch linux.

By: Calacuda | MIT Licence | Epoch: August 19th, 2021
"""


import argparse
import socket
import os
from multiprocessing import Pool
import json


parser = argparse.ArgumentParser(description="set up a hack the box machine directory.")
parser.add_argument('name', metavar='name', type=str,
                    help='the name of the machine')
parser.add_argument('-nv', '--nmap-vuln', action='store_const',
                    const=False, default=True,
                    help='do NOT do an nmap scan vuln if the machine is a wedserver.')
parser.add_argument('-nn', '--no-nmap', action='store_const',
                    const=True, default=False,
                    help='no nmap scan.')
parser.add_argument('-gb', '--gobuster', type=bool, nargs=1,
                    default=False,
                    help="use the default gobuster command. conflicts with \"--feroxbuster\"")
parser.add_argument('-fob', '--feroxbuster', type=bool,
                    nargs=1, default=True,
                    help="use the default feroxbuster command, default is ture.")
parser.add_argument('--scan', metavar="scan_cmd", type=str, nargs=1, default="",
                    help="define a custom wed directory scan command to use.")
parser.add_argument('--config', metavar="config_file", type=str, nargs=1,
                    default="~/.config/hackthebox_scripts/setup.json",
                    help="the config to use, default is, \"~/.config/hackthebox_scripts/setup.json\"")
parser.add_argument('-s', '--searchsploit', type=bool,
                    nargs=1, default=True,
                    help="do a searchsploit scan. default is true")
parser.add_argument('--extra', type=str, nargs=1,
                    default="",
                    help="extra comand line args to feed to the default feroxbuster or gobuster comands.")

ARGS = parser.parse_args()


def make_dirs(dirs: list[str]):
    main_dir = ARGS.name
    try:
        os.mkdir(main_dir)
    except FileExistsError:
        pass
    for sub_dir in dirs:
        try:
            os.mkdir(os.path.join(os.getcwd(), main_dir, sub_dir))
        except FileExistsError:
            pass

def is_web_server(host: str) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    location = (host, 80)
    result = s.connect_ex(location) == 0
    s.close()
    return result


def nmap(scan: str):
    """
    runs a single nmap scan called by nmap_scans
    """
    print(f"running :  {scan}")
    os.system(scan + " > /dev/null")
    print(f"finished :  {scan}")


def nmap_scans(scans: list[str]):
    """
    runs nmap scans in parallel.
    """
    with Pool(processes=len(scans)) as pool:
        pool.map(nmap, scans)


def get_configs(conf_file: str) -> dict:
    """
    reads the config file and returns a dictionary of configurations.
    """
    with open(os.path.expanduser(conf_file), "r") as f:
        return json.load(f)


def run_output(cmd: str):
    print(f"running :  {cmd}")
    # os.system(f"tmux new -s web-buster {cmd}")
    os.system(cmd)


def ferox_scan(cmd: str):
    run_output(cmd)


def gobust_scan(cmd: str):
    run_output(cmd)


def main():
    config = get_configs(ARGS.config)
    webserver = is_web_server(ARGS.name)
    dirs = ["nmap"]
    if ARGS.searchsploit:
        dirs.append("searchsploit")
    if webserver:
        dirs.append("web-dirs")
    make_dirs(dirs)

    if not ARGS.no_nmap:
        nm_cmds = config.get("nmap_scans")
        if ARGS.nmap_vuln:
            nm_cmds.append(config.get("nmap_vuln"))
        nm_cmds = [cmd.format(name=ARGS.name) for cmd in nm_cmds]
        nmap_scans(nm_cmds)

    if webserver and not ARGS.gobuster:
        cmd = config.get("ferox_cmd").format(name=ARGS.name, extra_cmd=ARGS.extra)
        ferox_scan(cmd)
    elif webserver and ARGS.gobuster:
        cmd = config.get("gobust_cmd").format(name=ARGS.name, extra_cmd=ARGS.extra)
        gobust_scan(cmd)
    elif ARGS.scan_cmd != "":
        run_output(ARGS.scan_cmd)
    else:
        print("not scanning server.")
    # searchsploit


if __name__ == "__main__":
    main()
