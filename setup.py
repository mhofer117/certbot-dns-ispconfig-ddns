from setuptools import setup, find_packages

with open("Readme.md") as f:
    long_description = f.read()

version = "v1.0"

install_requires = [
    "certbot",
    "requests"
]

tests_require = [
    'mock',
    "responses",
]

setup(
    name="certbot-dns-ispconfig-ddns",
    version=version,
    author="Marcel Hofer",
    url="https://github.com/mhofer117/certbot-dns-ispconfig-ddns",
    description=("Obtain certificates using a DNS TXT record for ISPConfig "
                 "domains with DDNS module tokens"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Apache License 2.0",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Security",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Utilities",
        "Topic :: System :: Systems Administration"
    ],
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=install_requires,
    tests_require=tests_require,
    entry_points={
        "certbot.plugins": [
            ("dns-ispconfig-ddns = "
             "certbot_dns_ispconfig_ddns.authenticator:Authenticator")
        ]
    },
)
