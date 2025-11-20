#!/usr/bin/env python3
"""
Wireless Protocol Security Research - Package Setup
====================================================

A comprehensive framework for wireless protocol security research including
attack implementations, traffic capture automation, and ML dataset generation
for WiFi, BLE, Zigbee, and LoRa protocols.

Installation:
    # Basic installation
    pip install -e .

    # Protocol-specific
    pip install -e .[ble]
    pip install -e .[wifi]
    pip install -e .[zigbee]
    pip install -e .[lora]

    # Development with ML tools
    pip install -e .[dev,ml]

    # Everything
    pip install -e .[all]

Author: Wireless Security Research Team
License: Educational/Research Use Only
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Wireless Protocol Security Research Framework"

# Core dependencies (always installed)
CORE_DEPS = [
    'scapy>=2.5.0',
    'pyshark>=0.6.0',
    'pandas>=2.0.0',
    'numpy>=1.24.0',
    'pyyaml>=6.0',
    'python-dateutil>=2.8.2',
    'colorama>=0.4.6',
    'click>=8.1.0',
    'tqdm>=4.65.0',
    'dpkt>=1.9.8',
    'netifaces>=0.11.0',
]

# Extra dependencies for specific protocols
EXTRAS = {
    # WiFi-specific
    'wifi': [
        'pyric>=0.1.6.3',
    ],

    # BLE-specific
    'ble': [
        'bleak>=0.21.0',
        'bluepy>=1.3.0',
        'pybluez>=0.23',
    ],

    # Zigbee-specific
    'zigbee': [
        # KillerBee installed separately
    ],

    # LoRa-specific
    'lora': [
        'pyserial>=3.5',
        'pycryptodome>=3.18.0',
    ],

    # ML and dataset processing
    'ml': [
        'scikit-learn>=1.3.0',
        'tensorflow>=2.13.0',
        'matplotlib>=3.7.0',
        'seaborn>=0.12.0',
        'joblib>=1.3.0',
        'pyarrow>=12.0.0',
        'fastparquet>=2023.4.0',
    ],

    # Development tools
    'dev': [
        'pytest>=7.4.0',
        'pytest-cov>=4.1.0',
        'pytest-asyncio>=0.21.0',
        'black>=23.0.0',
        'flake8>=6.0.0',
        'mypy>=1.4.0',
        'ipython>=8.14.0',
        'jupyter>=1.0.0',
    ],

    # Utilities
    'utils': [
        'requests>=2.31.0',
        'tabulate>=0.9.0',
        'rich>=13.4.0',
        'psutil>=5.9.0',
    ],
}

# Combine all extras for 'all' installation
EXTRAS['all'] = list(set(sum(EXTRAS.values(), [])))

setup(
    name='wireless-security-research',
    version='0.1.0',
    description='Multi-language wireless protocol security research framework',
    long_description=read_readme(),
    long_description_content_type='text/markdown',

    author='Wireless Security Research Team',
    author_email='research@example.com',
    url='https://github.com/yourusername/wireless-security-research',

    # Package configuration
    packages=find_packages(
        include=[
            'Implementations',
            'Implementations.*',
            'Infrastructure',
            'Infrastructure.*',
        ]
    ),

    # Python version requirement
    python_requires='>=3.8',

    # Dependencies
    install_requires=CORE_DEPS,
    extras_require=EXTRAS,

    # Entry points for CLI tools
    entry_points={
        'console_scripts': [
            # Traffic capture tools
            'wsr-capture=Infrastructure.TrafficCapture.automation.unified_capture:main',
            'wsr-label=Infrastructure.DatasetPipeline.labeling.auto_labeler:main',

            # Hardware validation
            'wsr-validate=Infrastructure.HardwareValidation.test_suites.validate_all:main',

            # Dataset tools
            'wsr-extract=Infrastructure.DatasetPipeline.preprocessing.feature_extractor:main',
            'wsr-split=Infrastructure.DatasetPipeline.preprocessing.train_test_split:main',
        ],
    },

    # Package data
    include_package_data=True,
    package_data={
        '': [
            '*.md',
            '*.yaml',
            '*.json',
            '*.txt',
            'Dockerfile',
            'docker-compose.yml',
            'Makefile',
            'CMakeLists.txt',
            '*.sh',
        ],
    },

    # Classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Topic :: Security',
        'Topic :: System :: Networking',
        'License :: Other/Proprietary License',  # Educational use only
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: POSIX :: Linux',
    ],

    # Keywords
    keywords='security wireless bluetooth ble wifi zigbee lora penetration-testing ml dataset',

    # Project URLs
    project_urls={
        'Documentation': 'https://github.com/yourusername/wireless-security-research/wiki',
        'Source': 'https://github.com/yourusername/wireless-security-research',
        'Tracker': 'https://github.com/yourusername/wireless-security-research/issues',
    },

    # License
    license='Educational/Research Use Only - See LICENSE file',

    # Zip safety
    zip_safe=False,
)
