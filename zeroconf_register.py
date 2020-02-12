#!/usr/bin/env python3


#
# This does NOT use the Python zeroconf module, as getting the
# hostname/IP does not work reliably on macOS 10.14 so it's hard to
# register the service with correct information.
#
# Instead, we just call platform commands for Linux/macOS; this
# approach seems to work more reliably.
#


import platform, subprocess, sys, time


def print_usage(prog: str, prm: dict):
	"""Print some information on the use of thie program to stdout"""

	print()
	print('Usage:')
	print()
	print(f'{prog} svc_name ' + ' '.join(['[%s=x]'%(x) for x in prm]))
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


class ServiceRegister:
	"""Simple wrapper for DNS-SD registration on different platforms"""
	
	linux_args = ['avahi-publish', '--service', '--no-reverse']
	macos_args = ['dns-sd', '-R']

	def __init__(self, svc_name: str, svc_type: str, svc_port: str, svc_txt: str = None):
		"""Determine the current platform, and launch appropriate
		service registration program as a subprocess."""

		pltfm = platform.system()

		if pltfm == 'Linux':
			what = 'Linux'
			args = self.linux_args + [svc_name, svc_type, svc_port]
			if svc_txt != None:
				args = args + [svc_txt] # avahi-publish doesn't like empty txt input!

		elif pltfm == 'Darwin':
			what = 'macOS'
			args = self.macos_args + [svc_name, svc_type, "local", svc_port]
			if svc_txt != None:
				args = args + [svc_txt] # just to keep consistent with Linux path

		else:
			print(f'Unknown platform "{pltfm}"')
			sys.exit(-1)

		print(f'Platform "{pltfm}" assumed to be {what}, using {args} ...')

		try:
			self.process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
		except Exception as e:
			print(f'Cannot invoke registration command: {e}')
			sys.exit(-1)

	def cleanup(self):
		"""Attempt graceful shutdown of service registration program"""
		print('ServiceRegister cleanup started.')
		self.process.terminate()
		self.process.wait()
		print('ServiceRegister cleanup done.')


# Default values for optional parameters
params = {
	'svc_type': '_http._tcp',
	'svc_port': '666',
	'svc_txt': None,
}

# Print usage if run with no parameters
if (len(sys.argv)<2):
	print_usage(sys.argv[0],params)

# Service name is the first parameter (mandatory)
params['svc_name'] = sys.argv[1]

# Update the default values for any optional parameters
update_params(sys.argv, params)
print(params)

# Off we go!
sr = ServiceRegister(**params)

try:
	while True:
		time.sleep(5)
#		print('Tick')
except KeyboardInterrupt:
	print('Interrupt!')
finally:
	sr.cleanup()
