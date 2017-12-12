from setuptools import setup, find_packages

setup(
    name='Tymora',
    version='0.0.1',
    packages=find_packages(),
    install_requires=['discord.py'],
    url='https://github.com/Mego/Tymora',
    license='MIT License',
    author='Mego',
    author_email='Mego@users.noreply.github.com',
    description='Making rolling dice way more complicated',
    entry_points={
        'console_scripts': [
            'tymora = tymora:main',
        ]
    }
)
