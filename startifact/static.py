from boto3.session import Session

from startifact.account import Account
from startifact.parameters.configuration import ConfigurationParameter

default_session = Session()

account = Account(default_session)

config_param = ConfigurationParameter(default_session, account)
