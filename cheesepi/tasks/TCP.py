import sys
import string
import time
import os
import logging
import socket
import struct
import requests
import threading

# http://ncu.dl.sourceforge.net/project/pylibpcap/pylibpcap/0.6.4/pylibpcap-0.6.4.tar.gz
import pcap

import cheesepi as cp
import Task

logger = cp.config.get_logger(__name__)

protocols={socket.IPPROTO_TCP:'tcp',}

# TCP flags
SYN = 0x02
FIN = 0X01
RST = 0x04
ACK = 0x10
PSH = 0x08


class Capturer(threading.Thread):
	""" @brief Class for capturing packets and information extraction.
	Requires python packages: pylibpcap
	http://ncu.dl.sourceforge.net/project/pylibpcap/pylibpcap/0.6.4/pylibpcap-0.6.4.tar.gz """

	def __init__(self, destination):
		super(Capturer, self).__init__()
		self.captured_pkts   = [] # list of packet summaries
		self.start_timestamp = -1
		self.destination = destination
		self.destination_ip = socket.gethostbyname(self.destination)
		self.terminated = False
		self.daemon     = True
		threading.Thread.__init__(self)

	def run(self):
		""" @brief Capture each packet and return list of filtered information.
		@param System Arguments: interface and port number to sniff on
		@return List of packets' arrival time, time from first arrived packet and the type of packet. """
		dev = "en0"
		p = pcap.pcapObject()
		net, mask = pcap.lookupnet(dev)
		try:
			p.open_live(dev, 65535, 0, 100)
			p.setfilter(string.join(sys.argv[2:],' '), 0, 0)
			logging.debug("Started packet capture module: Listening on %s: net=%s, mask=%s" % (dev, net, mask))
		except Exception, e:
			print "Started packet capture module: open_live() failed for device='%s'. Error: %s" % (dev, str(e))

		try:
			while (not self.terminated): p.dispatch(1, self.filter_captured)
		except KeyboardInterrupt as e:
			print 'Shutting down: %s' % e
		print '%d packets received, %d packets dropped, %d packets dropped by interface' % p.stats()

	def filter_captured(self, pktlen, data, timestamp):
		""" @brief Filter packet and store epoch time, arrival time since first packet and packet type.
		@param Default arguments as indicated by dispatch function
		@return List of packets' arrival time, time from first arrived packet and the type of packet. """
		# ensure we have a TCP IP data packet
		#if not data: return
		if (data[12:14]!='\x08\x00') or (data[23:24]!='\x06'):
			#print "wrong packet type"
			return

		ip_headers = self.parse_IP_hdr(data[14:])
		# If the source addr or destination addr are server addr, then packet is relevant
		if (not self.is_intended_dst(ip_headers['src_address']) and not self.is_intended_dst(ip_headers['dst_address'])):
			#print "wrong dest"
			return
		tcp_headers = self.parse_TCP_hdr(ip_headers['data'])

		summary = {} # our summary of the packet
		summary['flags'] = ""
		if tcp_headers['flags'] & SYN: summary['flags'] += 'SYN'
		if tcp_headers['flags'] & FIN: summary['flags'] += 'FIN'
		if tcp_headers['flags'] & PSH: summary['flags'] += 'PSH'
		if tcp_headers['flags'] & ACK: summary['flags'] += 'ACK'
		if tcp_headers['flags'] & RST: summary['flags'] += 'RST'

		#if self.data_type == 'SYN' and start_timestamp==-1: start_timestamp=timestamp
		#if (self.SYN_count >= 1):
		summary['time'] = timestamp
		if self.start_timestamp==-1: self.start_timestamp=timestamp
		summary['delay'] = timestamp - self.start_timestamp
		print summary
		self.captured_pkts.append(summary)


	def parse_IP_hdr(self, pkt):
		""" @brief Filter packet's IP header fields.
		@param Binary data representing the IP header
		@return Parsed IP header fields' information.
		"""
		iph = struct.unpack('!BBHHHBBH4s4s', pkt[0:20])
		hdr = {}
		hdr['version'] =    iph[0] >> 4
		hdr['header_len'] = iph[0] & 0x0f
		hdr['tos'] =        iph[1]
		hdr['total_len'] =  iph[2]
		hdr['id'] =         iph[3]
		hdr['flags'] =      (iph[4] & 0xe000) >> 13
		hdr['fragment_offset']= iph[4] & 0x1fff
		hdr['ttl'] =        iph[5]
		hdr['protocol'] =   iph[6]
		hdr['checksum'] =   iph[7]
		hdr['src_address'] = socket.inet_ntoa(iph[8])
		hdr['dst_address'] = socket.inet_ntoa(iph[9])

		if hdr['header_len'] > 5:
			hdr['options'] = pkt[20:4*(hdr['header_len']-5)]
		else:
			hdr['options'] = None
		hdr['data'] = pkt[4*hdr['header_len']:]
		return hdr


	def parse_TCP_hdr(self, pkt):
		""" @brief Filter packet's TCP header fields.
		@param Binary data representing the TCP header
		@return Parsed TCP header fields' information.
		"""
		tcph = struct.unpack('!HHLLBBHHH' , pkt[0:20])
		hdr = {}
		hdr['src_port'] =   tcph[0]
		hdr['dst_port'] =   tcph[1]
		hdr['seq'] =        tcph[2]
		hdr['ack'] =        tcph[3]
		hdr['dataOffset'] =  (tcph[4] & 0xf8)>> 3 # dataOffset and reserved fields shifted to get dataOffset
		hdr['flags'] =      tcph[5] & 0x3f
		hdr['window'] =     tcph[6]
		hdr['checksum'] =   tcph[7]
		hdr['urg'] =        tcph[8]
		if hdr['dataOffset'] > 5:
			hdr['options'] = pkt[20:2*hdr['dataOffset']]
		else:
			hdr['options'] = None
		hdr['data'] = pkt[2*hdr['dataOffset']:]
		return hdr

	def is_intended_dst(self, ip_addr):
		""" @brief Determines if IP address in src/dst address fields is the same .
		@param Binary data representing the IP header
		@return Parsed IP header fields' information. """
		if ip_addr == self.destination_ip:
			return True
		return False

	def dumphex(self, s):
		""" @brief Translates bytes into string
		@param Binary data
		@return String of data. """
		if s:
			bytes = map(lambda x: '%.2x' % x, map(ord, s))
			for i in xrange(0,len(bytes)/16):
				print '		   %s' % string.join(bytes[i*16:(i+1)*16],' ')
			print '		   %s' % string.join(bytes[(i+1)*16:],' ')
		else:
			print 'Empty'


	def print_packet(self, pktlen, data, timestamp):
		""" @brief Filter packet and display IP and TCP headers' contents.
		@param Default arguments as indicated by dispatch function
		@return IP and TCP headers' contents. """
		if not data: return
		" If the packet is type IP and has protocol type TCP "
		if (data[12:14]=='\x08\x00') and (data[23:24]=='\x06'):

			ip_parse = self.parse_IP_hdr(data[14:])
			print '\n%s.%f %s > %s' % (time.strftime('%H:%M',
						time.localtime(timestamp)),
						timestamp % 60,
						ip_parse['src_address'],
						ip_parse['dst_address'])
			for key in ['version', 'header_len', 'tos', 'total_len', 'id',
						'flags', 'fragment_offset', 'ttl']:
				print '    %s: %d' % (key, ip_parse[key])
			print '    protocol: %s' % protocols[ip_parse['protocol']]
			print '    header checksum: %d' % ip_parse['checksum']
			#print '	data:'
			#dumphex(ip_parse['data'])
			tcp_parse = self.parse_TCP_hdr(ip_parse['data'])
			for key in ['src_port', 'dst_port', 'seq', 'ack', 'dataOffset', 'flags', 'window', 'urg']:
				print '    %s: %d' % (key, tcp_parse[key])
			print '    data:'
			self.dumphex(tcp_parse['data'])


class TCP(Task.Task):
	# construct the process and perform pre-work
	def __init__(self, dao, spec):
		Task.Task.__init__(self, dao, spec)
		self.spec['taskname']    = "tcp"
		if not 'landmark'    in self.spec: self.spec['landmark']    = "www.sics.se"

	# actually perform the measurements, no arguments required
	def run(self):
		print "TCP capture: %s @ %f, PID: %d" % (self.spec['landmark'], time.time(), os.getpid())
		pkt_capture = Capturer(self.spec['landmark'])
		pkt_capture.setDaemon(True)
		pkt_capture.start()
		if pkt_capture.isAlive():
			time.sleep(3)
			requests.get("http://"+self.spec['landmark'])
		else:
			print "Error HTTP problem"
		pkt_capture.terminated = True
		pkt_capture.join()
		print pkt_capture.captured_pkts

	# measure and record funtion
	def measure(self):
		start_time = cp.utils.now()
		op_output = self.perform(self.spec['landmark'], self.spec['ping_count'], self.spec['packet_size'])
		end_time = cp.utils.now()

		logger.debug(op_output)
		if op_output!=None: # we succeeded
			self.parse_output(op_output, self.spec['landmark'],
				start_time, end_time, self.spec['packet_size'], self.spec['ping_count'])
		self.dao.write_op(self.spec['taskname'], self.spec)



if __name__ == "__main__":
	#general logging here? unable to connect etc
	dao = cp.config.get_dao()

	spec = {'landmark':'www.sics.se'}
	tcp_task = TCP(dao, spec)
	tcp_task.run()

