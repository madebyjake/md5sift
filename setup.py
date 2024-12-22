import os
import datetime
from setuptools import setup, find_packages, Command

class GenerateSpecCommand(Command):
    """Custom command to generate an RPM .spec file."""
    description = 'Generate an RPM spec file dynamically'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        spec_content = f"""%global name {self.distribution.get_name()}
%global version {self.distribution.get_version()}
%global release 1%{{?dist}}
%global summary {self.distribution.get_description()}

Name:           %{{name}}
Version:        %{{version}}
Release:        %{{release}}
Summary:        %{{summary}}

License:        MIT
URL:            https://github.com/madebyjake/md5sift
Source0:        %{{name}}-%{{version}}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel python3-setuptools
Requires:       python3

%description
Quickly generate MD5 checksum reports for large directories with filtering options.

%prep
%setup -q

%build
%py3_build

%install
%py3_install
install -d %{{buildroot}}%{{python3_sitelib}}

%files
%license LICENSE
%doc README.md
%{{_bindir}}/md5sift
%{{python3_sitelib}}/md5sift
%{{python3_sitelib}}/md5sift/*
%{{python3_sitelib}}/md5sift/__main__.py
%{{python3_sitelib}}/md5sift-*.egg-info

%changelog
* {datetime.datetime.now().strftime('%a %b %d %Y')} Jake Wells <https://github.com/madebyjake/>
- https://github.com/madebyjake/md5sift/releases/
"""

        with open('md5sift.spec', 'w') as spec_file:
            spec_file.write(spec_content)
        
        print("✅ RPM spec file 'md5sift.spec' has been successfully generated!")

try:
    with open('README.md', 'r') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "Quickly generate MD5 checksum reports for large directories with filtering options."

setup(
    name='md5sift',
    version='1.1.0',
    packages=find_packages(),
    py_modules=['md5sift'],
    entry_points={
        'console_scripts': [
            'md5sift=md5sift.__main__:main'
        ]
    },
    install_requires=[],
    author='Jake Wells',
    author_email='jake@example.com',
    description='Quickly generate MD5 checksum reports for large directories with filtering options.',
    license='MIT',
    url='https://github.com/madebyjake/md5sift',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License'
    ],
    python_requires='>=3.6',
    long_description=long_description,
    long_description_content_type='text/markdown',
    cmdclass={
        'genspec': GenerateSpecCommand,
    }
)
