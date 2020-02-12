#!/usr/bin/env python3


#
# Monitors zeroconf service registration on the local network.
# It's possible to use platform-specific utilities to do this, but it's
# simpler to use the Python zeroconf package rather then parsing all
# sorts of output text that might change if the programs are upgraded.
#
# Needs zeroconf Python package, so e.g.:
#
# pip3 install zeroconf
#


import socket, sys, threading, time, zeroconf


def print_usage(prog: str, prm: dict):
	"""Print some information on the use of thie program to stdout"""

	print()
	print('Usage:')
	print()
	print(f'{prog} svc_type ' + ' '.join(['[%s=x]'%(x) for x in prm]))
	print()
	print('Example:')
	print()
	print(f'{prog} _http_.tcp heartbeat=1.5')
	print()
	print('Default values for optional parameters:')
	print()
	for k,v in prm.items(): print(f'{k} : {v}')
	print()
	sys.exit(-1)


def update_params(argv: list, prm: dict):
	"""Update default parameters using any command line arguments"""

	for a in argv[1:]:
		toks = a.split('=',1)
		if len(toks)<2: continue
		k,v = toks[:2]
		if k not in prm: continue
		prm[k] = v


class ServiceListener:
	"""This class listens for addition/removal of Zeroconf services"""

	def __init__(self, svc_type: str):
		"""Start Zeroconf service browser for specified service type"""
		self.services = {}
		self.counter = 0
		self.cv = threading.Condition()

		self.zeroconf = zeroconf.Zeroconf()
		self.browser = zeroconf.ServiceBrowser(self.zeroconf, svc_type, self)

	def wait(self, timeout: float = None):
		"""Called by user; returns true if service data changed"""
		self.cv.acquire()

		tmp = self.counter
		self.cv.wait(timeout)
		result = (self.counter != tmp)

		self.cv.release()

		return result

	def notify_modified(self):
		"""Notify anyone who called wait() that service data changed"""
		self.cv.acquire()
		self.counter += 1
		self.cv.notify_all()
		self.cv.release()

	def cleanup(self):
		"""Attempt graceful shutdown"""
		self.cv.acquire()
		self.zeroconf.close()
		self.cv.release()

	def remove_service(self, zeroconf, type, name):
		"""Used by Zeroconf serfice browser - not for user invocation!"""
		self.cv.acquire()
		if name in self.services:
			self.services.pop(name)
			self.notify_modified()
		self.cv.release()

	def add_service(self, zeroconf, type, name):
		"""Used by Zeroconf serfice browser - not for user invocation!"""
		info = self.zeroconf.get_service_info(type, name)
		#print(info)

		addresses = []
		for x in info.addresses:
			if len(x) == 4:
				addresses.append( socket.inet_ntop(socket.AF_INET,x) )
			elif len(x) == 16:
				addresses.append( socket.inet_ntop(socket.AF_INET6,x) )

		self.cv.acquire()
		self.services[name] = {
			'name': name,
			'addresses': addresses,
			'port': info.port,
			'host': info.server,
			'TXT': { k.decode('utf-8'): v.decode('utf-8') for k,v in info.properties.items() },
		}
		self.cv.release()

		self.notify_modified()


# Default values for optional parameters
params = {
	'heartbeat': '2.0',
}

# Print usage if run with no parameters
if (len(sys.argv)<2):
	print_usage(sys.argv[0],params)

# Service type is the first parameter (mandatory)
params['svc_type'] = sys.argv[1]

# Update the default values for any optional parameters
update_params(sys.argv, params)
print(params)

try:
	heartbeat = float(params['heartbeat'])
except:
	print(f'Bad heartbeat {params["heartbeat"]}; using 2s')
	heartbeat = 2.0
finally:
	if heartbeat <= 0:
		print(f'Bad heartbeat {heartbeat}s; using 2s')
		heartbeat = 2.0

# Off we go!
sl = ServiceListener(params['svc_type'] + '.local.')

while True:

	if sl.wait(heartbeat) == True: # have services changed?
		sl.cv.acquire()
		print('Services:')
		for svc_name,info in sl.services.items():
			print(f'  {svc_name} :')
			for k,v in info.items(): print(f'    {k} : {v}')
		print()
		sl.cv.release()
	else: # services same; hearbeat
		sl.cv.acquire()
		print(f'Heartbeat ( {sl.counter} service update messages )')
		sl.cv.release()

sl.cleanup()
