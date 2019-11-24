from notebook.auth import passwd

pwd = input('Enter jupyterlab password: ')
hash = passwd(pwd)
print('Your jupyterlab password hash is:', hash)
