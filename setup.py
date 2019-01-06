from setuptools import setup

setup(name='neurobit',
      version='1.0',
      description='Neurobit Utilities to score and analyze sleep data using the Z3Score Framework.',
      url='https://github.com/neurobittechnologies/neurobit',
      author='Amiya Patanaik',
      author_email='amiya@neurobit.io',
      license='GPL',
      packages=['neurobit'],
      install_requires=[
          'pycfslib>=1.3',
          'pyedflib',
          'scipy',
          'numba',
          'click',
          'requests'
      ],
      entry_points='''
        [console_scripts]
        neurobit=neurobit:cli
     ''',
      zip_safe=False)
