import sys
import time
import os
from subprocess import Popen, PIPE
import dns.query
import dns.resolver
from dns.exception import DNSException

sys.path.append("/usr/local/")
import cheesepi.utils
import Task

class DNS(Task.Task):

	# construct the process and perform pre-work
	def __init__(self, dao, parameters):
		Task.Task.__init__(self, dao, parameters)
		self.taskname	 = "dns"

	def toDict(self):
		return {'taskname' :self.taskname,
			}

	# actually perform the measurements, no arguments required
	def run(self):
		print "DNS: @ %f, PID: %d" % (self.landmark, time.time(), os.getpid())
		self.measure(self.landmark, self.ping_count, self.packet_size)

	# measure and record funtion
	def measure(self, landmark, ping_count, packet_size):
		start_time = cheesepi.utils.now()
		op_output = self.perform()
		end_time = cheesepi.utils.now()
		#print op_output

		parsed_output = self.parse_output(op_output, start_time, end_time)
		self.dao.write_op(self.taskname, parsed_output)

# http://stackoverflow.com/questions/4066614/how-can-i-find-the-authoritative-dns-server-for-a-domain-using-dnspython
def query_authoritative_ns(domain, log=lambda msg: None):
	default = dns.resolver.get_default_resolver()
	ns = default.nameservers[0]
	n = domain.split('.')

	for i in xrange(len(n), 0, -1):
		sub = '.'.join(n[i-1:])
		log('Looking up %s on %s' % (sub, ns))
		query = dns.message.make_query(sub, dns.rdatatype.NS)
		response = dns.query.udp(query, ns)

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
			for rr in rrset:
				if rr.rdtype == dns.rdatatype.SOA:
					log('Same server is authoritative for %s' % (sub))
				elif rr.rdtype == dns.rdatatype.A:
					ns = rr.items[0].address
					log('Glue record for %s: %s' % (rr.name, ns))
				elif rr.rdtype == dns.rdatatype.NS:
					authority = rr.target
					ns = default.query(authority).rrset[0].to_text()
					log('%s [%s] is authoritative for %s; ttl %i' %
						(authority, ns, sub, rrset.ttl))
					result = rrset
				else:
					# IPv6 glue records etc
					#log('Ignoring %s' % (rr))
					pass

	return result



	#ping function
	def perform(self):
		execute = "ping "
		logging.info("Executing: "+execute)
		print execute
		result = Popen(execute ,stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
		ret = result.stdout.read()
		result.stdout.flush()
		return ret

	#read the data from ping and reformat for database entry
	def parse_output(self, data, landmark, start_time, end_time, packet_size, ping_count):
		ret = {}
		ret["start_time"]  = start_time
		ret["end_time"]    = end_time
		delays=[]

		return ret


def log (msg):
	sys.stderr.write(msg + u'\n')


if __name__ == "__main__":
	#general logging here? unable to connect etc
	dao = cheesepi.config.get_dao()

	print query_authoritative_ns("google.com", log)
	parameters = {'landmark':'google.com'}
	dns_task = DNS(dao, parameters)
	dns_task.run()
