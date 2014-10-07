#!/usr/bin/python

## This file is part of Whonix.
## Copyright (C) 2012 - 2014 Patrick Schleizer <adrelanos@riseup.net>
## See the file COPYING for copying conditions.

import socket
import re
import sys
import binascii

try:
  address = str(sys.argv[1])
  port = int(sys.argv[2])

  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.settimeout(5.0)
  cpfpSocket = (address, port)
  sock.connect(cpfpSocket)

  readh = sock.makefile("r")
  writeh = sock.makefile("w")

  # authenticate when using Tor control port directly
  if str(sys.argv[3]) == '1':
    f = open('/var/run/tor/control.authcookie', 'rb')
    rawcookie = f.read(32)
    hexcookie = binascii.hexlify(rawcookie)
    writeh.write('AUTHENTICATE ' + hexcookie + '\n')
    writeh.flush()
    # don't check the answer
    answer = readh.readline().strip()

  writeh.write('GETINFO status/bootstrap-phase\n')
  writeh.flush()
  answer = readh.readline().strip()
  #print answer

  # Remove "[return code]-[request]=" from answer when using Tor control port directly.
  # Otherwise, the operation is done in CPFP.
  # This is because we write "GETINFO request" instead of 'controller.get_info("request")'
  # which returns the result only.
  if str(sys.argv[3]) == '1':
    index = answer.index('=') + 1
    bootstrap_status = answer[index:]
  else:
    bootstrap_status = answer

  print bootstrap_status

  progress_percent = re.match('.* PROGRESS=([0-9]+).*', bootstrap_status)
  exit_code = int(progress_percent.group(1))

except ValueError as e:
  print 'Value error: %s' % e
  exit_code=255
except NameError as e:
  print 'Name error: %s' % e
  exit_code=255
except socket.error as e:
  print 'Socket error: %s' % e
  exit_code=255

sys.exit(exit_code)
