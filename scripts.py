import subprocess


def lint():
    lint_result: subprocess.CompletedProcess = subprocess.run(
        ['flake8', '.', '--count', '--max-complexity=10',
         '--max-line-length=79', '--show-source', '--statistics']
    )
    exit(lint_result.returncode)


def test():
    test_result: subprocess.CompletedProcess = subprocess.run(
        ['pytest', '--cov=certbot_dns_ispconfig_ddns', '--cov-fail-under=80',
         '--cov-branch', '--cov-report=term', '--cov-report=term-missing',
         '--cov-report=xml:coverage.xml', 'tests/']
    )
    exit(test_result.returncode)
