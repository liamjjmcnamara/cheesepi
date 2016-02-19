import time
import os

# http://www.dnspython.org/examples.html
import dns.query
import dns.resolver
#from dns.exception import DNSException

#import cheesepi as cp
import cheesepi.config as config
import cheesepi.utils as utils
import Task

logger = config.get_logger(__name__)

class DNS(Task.Task):

	# construct the process and perform pre-work
	def __init__(self, dao, spec):
		Task.Task.__init__(self, dao, spec)
		self.spec['taskname'] = "dns"
		if not 'landmark' in spec: self.spec['landmark'] = "sics.se"

	# actually perform the measurements, no arguments required
	def run(self):
		logger.info("DNS: @ %f, PID: %d" % (time.time(), os.getpid()))
		self.measure()

	# measure and record funtion
	def measure(self):
		try:
			op_output = self.query_authoritative_ns(self.spec['landmark'], log)
			#print op_output
		except Exception as e:
			logger.error("DNS query failed: %s" % e)
			return
		logger.debug(op_output)
		parsed_output = self.parse_output(op_output, self.spec['landmark'])
		self.dao.write_op(self.spec['taskname'], parsed_output)

	#read the data from ping and reformat for database entry
	def parse_output(self, delays, domain):
		self.spec['delays'] = str(delays)
		self.spec['sum']    = sum(delays)
		return self.spec

	# http://stackoverflow.com/questions/4066614/how-can-i-find-the-authoritative-dns-server-for-a-domain-using-dnspython
	def query_authoritative_ns(self, domain, log=lambda msg: None):
		default = dns.resolver.get_default_resolver()
		ns = default.nameservers[0]
		n = domain.split('.')
		delays = [] # right to left delays in DNS resolution

		for i in xrange(len(n), 0, -1):
			sub = '.'.join(n[i-1:])
			log('Looking up %s on %s' % (sub, ns))
			start_time = utils.now()
			query = dns.message.make_query(sub, dns.rdatatype.NS)
			response = dns.query.udp(query, ns)
			end_time = utils.now()
			delay = end_time - start_time
			#logger.info("time: %f" % (delay))
			delays.append(delay)

			rcode = response.rcode()
			if rcode != dns.rcode.NOERROR:
				if rcode == dns.rcode.NXDOMAIN:
					raise Exception('%s does not exist.' % (sub))
				else:
					raise Exception('Error %s' % (dns.rcode.to_text(rcode)))

			if len(response.authority) > 0:
				rrsets = response.authority
			elif len(response.additional) > 0:
				rrsets = [response.additional]
			else:
				rrsets = response.answer

			# Handle all RRsets, not just the first one
			for rrset in rrsets:
				#print rrset
				for rr in rrset:
					if rr.rdtype == dns.rdatatype.SOA:
						#log('Same server is authoritative for %s' % (sub))
						pass
					elif rr.rdtype == dns.rdatatype.A:
						ns = rr.items[0].address
						#log('Glue record for %s: %s' % (rr.name, ns))
					elif rr.rdtype == dns.rdatatype.NS:
						authority = rr.target
						ns = default.query(authority).rrset[0].to_text()
						#log('%s [%s] is authoritative for %s; ttl %i' % (authority, ns, sub, rrset.ttl))
						#result = rrset
					else:
						# IPv6 glue records etc
						#log('Ignoring %s' % (rr))
						pass
		#return result
		return delays


def log (msg):
	pass
	#sys.stderr.write(msg + u'\n')


if __name__ == "__main__":
	#general logging here? unable to connect etc
	dao = config.get_dao()

	spec = {'landmark':"www.abc.net.au"}
	dns_task = DNS(dao, spec)
	dns_task.run()

