import os

# run from one directory up

version = open('VERSION').read()
os.system('git tag %s' % version)
os.system('git push --tags origin master')

os.system('python setup.py sdist bdist_wheel')
os.system('twine register dist/pscheduler-*.whl')
os.system('twine upload dist/*')
os.system('rm -rf pscheduler.egg-info dist build')
