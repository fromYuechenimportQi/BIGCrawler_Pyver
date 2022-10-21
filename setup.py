from setuptools import setup, find_packages


setup(
    name='BIGCrawler',
    version="1.0.1",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": ['BIGCrawler = src.BIGCrawler:main']
    },
    install_requires=[
        'bs4', 'argparse', 'tqdm'
    ],
    url='https://github.com/yueyue970506/BIGCrawler',
    license='MIT',
    author='Yuechen Qi',
    author_email='519584766@qq.com',
    description='Crawler program for BIG database'
)
