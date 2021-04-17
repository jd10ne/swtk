# SWTK - Make a AWS temporary session profile

SWTK is useful if you have many AWS IAM accounts or the environment is enabled MFA force setting.
Did you feel the fatigue that was asked the MFA token at every execution.
It can be able to automate get session token, assume role session and profile making of temporary security credentials.
you can execute the process need the MFA token with temporary profile.



## Requirements

- python3.8
- boto3

## Install

```
# pip
pip install -r requirements.txt

# pipenv
pipenv install
```