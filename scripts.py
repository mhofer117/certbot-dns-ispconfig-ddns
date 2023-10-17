import pathlib
import shutil
import subprocess


def lint():
    if pathlib.Path('reports/lint').is_dir():
        shutil.rmtree('reports/lint')
    pathlib.Path('reports/lint').mkdir(parents=True)
    # create statistics only file for badge creation
    subprocess.run(
        ['flake8', '.', '--count', '--max-complexity=10',
         '--max-line-length=79', '--show-source', '--statistics',
         '-q', '-q',
         '--tee', '--output-file', 'reports/lint/flake8-stats.txt'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    lint_result: subprocess.CompletedProcess = subprocess.run(
        ['flake8', '.', '--count', '--max-complexity=10',
         '--max-line-length=79', '--show-source', '--statistics',
         '--tee', '--output-file', 'reports/lint/report.txt']
    )
    exit(lint_result.returncode)


def test():
    if pathlib.Path('reports/tests').is_dir():
        shutil.rmtree('reports/tests', ignore_errors=True)
    test_result: subprocess.CompletedProcess = subprocess.run(
        ['coverage', 'run', '--source=certbot_dns_ispconfig_ddns',
         '--branch', '--module', 'pytest',
         '--junitxml=reports/tests/junit.xml',
         '--md-report', '--md-report-flavor', 'gfm',
         '--md-report-output=reports/tests/report.md',
         'tests/']
    )

    if pathlib.Path('reports/coverage').is_dir():
        shutil.rmtree('reports/coverage', ignore_errors=True)
    pathlib.Path('reports/coverage').mkdir(parents=True)
    with open('reports/coverage/report.md', 'w') as f_obj:
        subprocess.run(
            ['coverage', 'report', '--show-missing', '--format=markdown'],
            stdout=f_obj, text=True
        )
    subprocess.run(['coverage', 'xml', '-o', 'reports/coverage/coverage.xml'])
    coverage_result: subprocess.CompletedProcess = subprocess.run(
        ['coverage', 'report', '--show-missing', '--fail-under=90']
    )
    exit(test_result.returncode + coverage_result.returncode)


def ci_badges():
    tests: subprocess.CompletedProcess = subprocess.run(
        ['genbadge', 'tests', '--verbose',
         '--input-file', 'reports/tests/junit.xml',
         '--output-file', 'reports/tests/badge.svg',
         '--local']
    )
    coverage: subprocess.CompletedProcess = subprocess.run(
        ['genbadge', 'coverage', '--verbose',
         '--input-file', 'reports/coverage/coverage.xml',
         '--output-file', 'reports/coverage/badge.svg',
         '--local']
    )
    lint: subprocess.CompletedProcess = subprocess.run(
        ['genbadge', 'flake8', '--verbose',
         '--input-file', 'reports/lint/flake8-stats.txt',
         '--output-file', 'reports/lint/badge.svg',
         '--name', 'lint',
         '--local']
    )
    exit(tests.returncode + coverage.returncode + lint.returncode)
