import os

from setuptools import find_packages
from setuptools import setup


NAME = 'CMFDefault'

here = os.path.abspath(os.path.dirname(__file__))


def _package_doc(name):
    f = open(os.path.join(here, name))
    return f.read()


_boundary = '\n' + ('-' * 60) + '\n\n'
README = _boundary.join([
    _package_doc('README.rst'),
     _package_doc('CHANGES.rst'),
])

setup(name='Products.%s' % NAME,
      version='2.4.0.dev0',
      description='Default product for the Zope Content Management Framework',
      long_description=README,
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Plone',
        'Framework :: Zope :: 4',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        ],
      keywords='web application server zope zope2 cmf',
      author='Zope Foundation and Contributors',
      author_email='zope-cmf@zope.org',
      url='https://github.com/zopefoundation/Products.CMFDefault',
      project_urls={
          'Issue Tracker': ('https://github.com/zopefoundation/'
                            'Products.CMFDefault/issues'),
          'Sources': 'https://github.com/zopefoundation/Products.CMFDefault',
      },
      license='ZPL 2.1',
      packages=find_packages(),
      include_package_data=True,
      namespace_packages=['Products'],
      zip_safe=False,
      python_requires='>=2.7, <3.0',
      install_requires=[
          'setuptools',
          'Zope >=4, <5',
          'Products.CMFCore',
          'Products.DCWorkflow',
          'Products.GenericSetup',
          'Products.MailHost',
          'Products.PythonScripts',
          'five.localsitemanager',
          'zope.formlib',
          ],
      extras_require={
          'docs': ['Sphinx', 'repoze.sphinx.autointerface', 'pkginfo'],
          'locales': ['zope.app.locales'],
          },
      entry_points="""
      [zope2.initialize]
      Products.%s = Products.%s:initialize
      """ % (NAME, NAME),
      )
