"""Compatibility entry point: refresh executable Markdown from saved artifacts."""
import argparse
from brazil_project.cli import main

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--only',default='all');parser.add_argument('--config',default='project.toml');parser.add_argument('--municipality')
    args=parser.parse_args()
    command=['report',args.only,'--from-saved','--config',args.config]
    if args.municipality: command+=['--municipality',args.municipality]
    raise SystemExit(main(command))
