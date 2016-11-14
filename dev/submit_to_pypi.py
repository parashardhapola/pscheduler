import os

version = open('../VERSION').read()
os.system('git tag %s -m "Add tag"' % version)
os.system('git push --tags origin master')
os.system('python setup.py register -r pypitest')
os.system('python setup.py sdist upload -r pypitest')
os.system('python setup.py register -r pypi')
os.system('python setup.py sdist upload -r pypi')

