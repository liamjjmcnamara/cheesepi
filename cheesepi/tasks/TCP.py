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
KEY=0

# TCP flags
SYN = 0x02
FIN = 0X01
RST = 0x04
ACK = 0x10
PSH = 0x08

class Parser(object):
	def __init__(self, epoch_time, delta_time, pkt_type):
		""" @brief Initialize data. """
		super(Parser, self).__init__()
		self.epoch_time = epoch_time
		self.delta_time = delta_time
		self.pkt_type = pkt_type
	def __display__(self):
		return "\n\nCaptured Packet : Epoch time:'%s', Delta time:'%s', Packet type:'%s'" % (str(self.epoch_time), str(self.delta_time), str(self.pkt_type))

class TcpTrace(threading.Thread):
	""" @brief Class for capturing packets and information extraction.
	Requires python packages: pylibpcap
	http://ncu.dl.sourceforge.net/project/pylibpcap/pylibpcap/0.6.4/pylibpcap-0.6.4.tar.gz """

	def __init__(self):
		super(TcpTrace, self).__init__()
		self.list_captured = [] # List of {time, type} for all captured packets
		self.dic_captured = {}  # Dictionary of list_captured per HTTP request
		self.First_Epoch = 0.0
		self.SYN_count = 0
		self.data_dic = {}
		self.data_type = ""
		self.terminated = False
		threading.Thread.__init__(self)
		self.daemon = True

	def run(self):
		""" @brief Capture each packet and return list of filtered information.
		@param System Arguments: interface and port number to sniff on
		@return List of packets' arrival time, time from first arrived packet and the type of packet. """
		dev = "eth0"
		p = pcap.pcapObject()
		net, mask = pcap.lookupnet(dev)
		try:
			p.open_live(dev, 65535, 0, 100)
			p.setfilter(string.join(sys.argv[2:],' '), 0, 0)
			logging.debug("Started packet capture module: Listening on %s: net=%s, mask=%s" % (dev, net, mask))
		except Exception, e:
			logging.error("Started packet capture module: open_live() failed for device='%s'. Error: %s" % (dev, str(e)))

		if not p: return

		# try-except block to catch keyboard interrupt.
		try:
			while (not self.terminated): p.dispatch(1, self.filter_captured)
		except KeyboardInterrupt as e:
			print 'Shutting down: %s' % e
		print '%d packets received, %d packets dropped, %d packets dropped by interface' % p.stats()

	def filter_captured(self,pktlen,data,timestamp):
		""" @brief Filter packet and store epoch time, arrival time since first packet and packet type.
		@param Default arguments as indicated by dispatch function
		@return List of packets' arrival time, time from first arrived packet and the type of packet. """
		# If it is a tcp connection setup/ teardown/ ack
		if not data: return
		# Ensure packet type=IP and protocol=TCP
		if (data[12:14]!='\x08\x00') or (data[23:24]!='\x06'): return

		ip_parse = self.parse_IP_hdr(data[14:])
		# If the source addr or destination addr are server addr, then packet is relevant
		if (not self.is_intended_dst(ip_parse['src_address']) and not self.is_intended_dst(ip_parse['dst_address'])):
			return

		tcp_parse = self.parse_TCP_hdr(ip_parse['data'])
		self.data_dic = {}
		self.data_type = ""
		self.data_dic['time'] = timestamp

		if tcp_parse['flags'] & SYN:
			self.data_type += ' SYN'
		if tcp_parse['flags'] & FIN:
			self.data_type += ' FIN'
		if tcp_parse['flags'] & PSH:
			self.data_type += ' PSH'
		if tcp_parse['flags'] & ACK:
			self.data_type += ' ACK'
		if tcp_parse['flags'] & RST:
			self.data_type += ' RST'

		"Start storing from first SYN. Includes dropped SYNs"
		if (self.data_type == ' SYN'):
			self.SYN_count += 1
			if (self.SYN_count == 1): # First SYN, set initial timestamp
				self.First_Epoch = timestamp #<------------------------------

		if (self.SYN_count >= 1):
			self.data_dic['Delta Time'] = timestamp - self.First_Epoch	# Time since first captured frame
			self.data_dic['Type'] = self.data_type
			#print self.list_captured
			#print self.First_Epoch

			try:
				packet_parser = Parser(self.data_dic['Epoch Time'],self.data_dic['Delta Time'],self.data_dic['Type'])
				self.list_captured.append(self.data_dic)

				# Check if TCP connection terminated, reset SYN_count to have next
				# cycle's delta time as a reference from this new cycle's SYN
				length = len(self.list_captured)
				if (self.list_captured[length-2]['Type'] == ' FIN ACK')and(self.data_type == ' ACK'):
					#self.terminated = True
					self.SYN_count = 0
					#self.First_Epoch = timestamp
					print 'End of connection'

					i = 0
					for pkt in self.list_captured:
						i+=1
						print 'Count' , i , ' - ', pkt

					print "--------------------- LIST -----------------------"
					print self.list_captured
					self.dic_captured[KEY] = self.list_captured
					fo = open("dump.txt", "a")
					fo.write('\n\n' + str(self.dic_captured))
					fo.close()
					# wipe collected data
					self.dic_captured = {}
					self.list_captured = []
			except Exception, e:
				logging.error("Packet capture module: failed to construct dictionary with packet info. Exception: %s" % str(e))


	def parse_IP_hdr(self, pkt):
		""" @brief Filter packet's IP header fields.
		@param Binary data representing the IP header
		@return Parsed IP header fields' information. """
		iph = struct.unpack('!BBHHHBBH4s4s', pkt[0:20])
		hdr = {}
		hdr['version'] =	iph[0] >> 4
		hdr['header_len'] =		iph[0] & 0x0f
		hdr['tos'] =		iph[1]
		hdr['total_len'] =	iph[2]
		hdr['id'] =			iph[3]
		hdr['flags'] =		(iph[4] & 0xe000) >> 13
		hdr['fragment_offset']=	iph[4] & 0x1fff
		hdr['ttl'] =		iph[5]
		hdr['protocol'] =	iph[6]
		hdr['checksum'] =	iph[7]
		hdr['src_address'] =	socket.inet_ntoa(iph[8])
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
		@return Parsed TCP header fields' information. """
		tcph = struct.unpack('!HHLLBBHHH' , pkt[0:20])
		hdr = {}
		hdr['src_port'] =	tcph[0]
		hdr['dst_port'] =	tcph[1]
		hdr['seq'] =		tcph[2]
		hdr['ack'] =		tcph[3]
		hdr['dataOffset'] =		(tcph[4] & 0xf8)>> 3 # dataOffset and reserved fields shifted to get dataOffset
		hdr['flags'] =		tcph[5] & 0x3f
		hdr['window'] =		tcph[6]
		hdr['checksum'] =	tcph[7]
		hdr['urg'] =		tcph[8]
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
		try:
			if ip_addr == socket.gethostbyname("www.google.se"):
				return True
			return False
		except socket.gaierror, e:
			print "Cannot resolve hostname: ", "www.google.se", e

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
		logger.info("TCP capture: %s @ %f, PID: %d" % (self.spec['landmark'], time.time(), os.getpid()))
		pkt_capture= TcpTrace()
		pkt_capture.setDaemon(True)
		pkt_capture.start()
		if pkt_capture.isAlive():
			r = requests.get("http://"+self.spec['landmark'])
			print r
		pkt_capture.terminated = True
		pkt_capture.join()

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

