from configparser import ConfigParser
config = ConfigParser()

config.read('config.ini')
config.add_section('main')
config.set('main', 'path', 'pandas_data')
config.set('main', 'objs', 'objs.csv')
config.set('main', 'rails', 'rails.csv')
config.set('main', 'emulation', 'emulation.txt')

with open('config.ini', 'w') as f:
    config.write(f)