#!/usr/bin/python3

if __name__ == "__main__":
  column_mapping = {
    'blue': 'In water',
    'yellow': 'In fridge',
    'white': 'Garage',
  }
  with open('log.csv', 'r') as log:
    first_line = log.readline()
    print('"use strict;"')
    print('// ' + first_line)
    print("var OK = 'OK';")
    print("var ERROR = 'ERROR';")
    for key_val in column_mapping.items():
      print("var %s = '%s';" % key_val)
    print("var columns = [%s];" % ','.join("'%s'" % v for v in column_mapping.values()))
    print('var logs = [')
    print(',\n'.join(['  [%s]' % line.strip() for line in log]))
    print('];')

