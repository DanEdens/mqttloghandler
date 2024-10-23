from setuptools import setup, find_packages

setup(
    name='mqttlogger',
    version='0.1.0',
    description='A custom logging handler that publishes messages to an MQTT broker.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/mqttlogger',  # Replace with your GitHub repo URL
    packages=find_packages(),
    install_requires=[
        'paho-mqtt>=1.5.1',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.7',
    license='MIT',
    keywords='mqtt logging handler',
)
