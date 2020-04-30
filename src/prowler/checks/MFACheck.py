from importlib import import_module
from typing import List, Tuple

import yaml

from prowler.common.functions import *
from . import AbstractCheck, Rule


def check_iam_mfa_for_users_with_console_password() -> Tuple[bool, List[str]]:
    credential_report = get_credential_report()
    result = []
    for user in credential_report:
        if user['password_enabled'] == 'true' and user['mfa_active'] == 'false':
            result.append('User' + user + ' has Password enabled but MFA disabled')
    if not result:
        result.append('No users found with Password enabled and MFA disabled')
    return len(result) == 0, result


def check_iam_root_disabled() -> Tuple[bool, List[str]]:
    return True, []


class MFACheck(AbstractCheck):
    @staticmethod
    def checks_file() -> str:
        a = __file__.rsplit('.', 1)
        assert a[1] == 'py'
        return a[0] + '.yml'

    def rules(self) -> List[Rule]:
        with open(self.checks_file()) as f:
            checks = yaml.load(f, Loader=yaml.Loader)['checks']
        rules: List[Rule] = []
        for check in checks:
            d = {}
            for field in Rule._fields:
                if field != 'check_function':
                    d[field] = check[field]
                else:
                    p, m = check[field].rsplit('.', 1)
                    module = import_module(p)
                    method = getattr(module, m)
                    d[field] = method
            rules.append(Rule(**d))
        return rules
