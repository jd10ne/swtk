#!/bin/python3
"""
SWTK - AWS SESSION TOKEN SWITCHER -
"""

import argparse
import boto_wp
import os

def main(profile="default", *, token=None, duration=900):
    credentials = boto_wp.get_session_token(profile=profile, token=token, duration=int(duration))

    # valid credential is there
    if credentials is None:
        return
    tmp_prof = profile + "-tmp"
    boto_wp.add_tmp_profile(tmp_prof, credentials)

def arg_parse():
    """引数パーサ
    """
    parser = argparse.ArgumentParser(prog="SWTK - AWS SESSION TOKEN SWITCHER  -")

    # AWS Profile
    parser.add_argument("-p", "--profile", help="AWS profile", required=True)
    # MFA Token
    parser.add_argument("-t", "--token", help="MFA token")
    # Duration Time
    parser.add_argument("-d", "--duration", help="Duration seconds of session token", default=900)

    args = parser.parse_args()

    return args

if __name__ == "__main__":
    args = arg_parse()
    main(profile=args.profile, token=args.token, duration=args.duration)
    pass
