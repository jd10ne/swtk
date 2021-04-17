#!/bin/python3
"""
Boto3 Warper
"""

import boto3
import botocore
from awscli.customizations.configure.writer import ConfigFileWriter as Cw
import getpass
import os

DEFAULT_REGION = "ap-northeast-1"
CONFIG = "~/.aws/config"
CREDENTIALS = "~/.aws/credentials"


def resource(resource: str, *, profile="default", credential=None, region_name=DEFAULT_REGION):
    if credential is None:
        session = boto3.Session(profile_name=profile, region_name=region_name)
    else:
        session = boto3.Session(
            aws_access_key_id=credential["AccessKeyId"],
            aws_secret_access_key=credential["SecretAccessKey"],
            aws_session_token=credential["SessionToken"]
        )
    return session.resource(resource)


def client(resource: str, *, profile="default", credential=None, region_name=DEFAULT_REGION):
    if credential is None:
        session = boto3.Session(profile_name=profile, region_name=region_name)
    else:
        session = boto3.Session(
            aws_access_key_id=credential["AccessKeyId"],
            aws_secret_access_key=credential["SecretAccessKey"],
            aws_session_token=credential["SessionToken"]
        )
    return session.client(resource)


def get_name_tag(tags: list):
    for t in tags:
        if t["Key"] == "Name":
            return t["Value"]
    return None


def _get_assume_role_token(source_client, target_arn, duration, *, mfa=None, token=None):
    if mfa is None:
        credentials = source_client.assume_role(
            RoleArn=target_arn,
            RoleSessionName="resource-reporter",
            DurationSeconds=duration
        )
    else:
        credentials = source_client.assume_role(
                    RoleArn=target_arn,
                    RoleSessionName="resource-reporter",
                    DurationSeconds=duration,
                    SerialNumber=mfa,
                    TokenCode=token
        )
    return credentials

def _valid_session_token(profile):
    try:
        sess = client("sts", profile=profile)
        resp = sess.get_caller_identity()
        return True
    except botocore.exceptions.ClientError as error:
        return False
    except Exception as error:
        raise False

def get_session_token(*, duration=900, profile="default", token=None, credential_path=CREDENTIALS, **kwargs):
    try:
        config_path = kwargs['config_path'] if 'config_path' in kwargs else CONFIG
        profiles = botocore.configloader.load_config(credential_path)['profiles']
        tmp_prof = profile + "-tmp"

        # if there is tempolary session profile
        if profiles.get(tmp_prof) is not None:
            if _valid_session_token(tmp_prof):
                return None

        # profile not found in credential file
        if profile not in profiles:
            profiles = botocore.configloader.load_config(config_path)['profiles']

        # specified mfa
        if profiles[profile]["mfa_serial"] is not None:
            mfa = profiles[profile]["mfa_serial"]
            # if token isn't inputed
            if token is None:
                token = getpass.getpass(prompt="Enter MFA code for " + mfa + ": ")

        # assume role
        if profiles[profile]["source_profile"] is not None:
            source_profile = profiles[profile]["source_profile"]
            source_client = client("sts", profile=source_profile)
            target_arn = profiles[profile]["role_arn"]
            if mfa is None:
                credentials = _get_assume_role_token(source_client, target_arn, duration)["Credentials"]
            else:
                credentials = _get_assume_role_token(source_client, target_arn, duration, mfa=mfa, token=token)["Credentials"]
        else:
            if mfa is None:
                credentials = client("sts", profile=profile).get_session_token(
                    DurationSeconds=duration
                )
            else:
                credentials = client("sts", profile=profile).get_session_token(
                    DurationSeconds=duration,
                    SerialNumber=mfa,
                    TokenCode=token
                )
        pass
    except Exception as error:
        raise error

    return credentials

def add_tmp_profile(profile, credentials, *, config_path=CONFIG, credential_path=CREDENTIALS):

    config_val = {
        "__section__" : 'profile ' + profile,
        "region" : DEFAULT_REGION
    }

    credential_val = {
        "__section__" : profile,
        "aws_access_key_id" : credentials["AccessKeyId"],
        "aws_secret_access_key" : credentials["SecretAccessKey"],
        "aws_session_token" : credentials["SessionToken"],
    }

    writer = Cw()
    writer.update_config(config_val, os.path.expanduser(config_path))
    writer.update_config(credential_val, os.path.expanduser(credential_path))
