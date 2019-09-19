'''
Sources : http://pmg.csail.mit.edu/papers/vr-to-bft.pdf (paper 1) vr-bft
          https://dspace.mit.edu/bitstream/handle/1721.1/71763/MIT-CSAIL-TR-2012-021.pdf?sequence=1 (paper 2) vr-revis
	  
Command : python -m da vr_revisited_new.da <max failure supported> <num clients> <num_requests_per_client> <client timeout> <replica timeout>   
	  Default Arguments are :
	  <max failure supported> = 1
	  <num clients> = 5
	  <num_requests_per_client> = 10
	  <client timeout> = 10
	  <replica timeout> = 5
'''
import sys
import os
import time
import random

monitor = import_da('Monitor')

MAX_NOPS = 10

def operation(i): return lambda state: (state+[i], ['result',i,'on',state])
operations = {i: operation(i) for i in range(MAX_NOPS)}

#****************************************************************************************************************
# 													Client
# 		 The configuration and the current view-number allows it to know which replica is currently the primary.
#		 Each msg sent to the client informs it of the current view num.
#		 Client can have atmost one outstanding request at any time. Later request should have larger req numbers
#****************************************************************************************************************

class Client(process):
	def setup(replicas:Replica,n_requests:int,tout:float):
		self.state = None												# Current State of the client
		self.config = list(replicas)
		config.sort()													# Configuration setting of the current replica group
		self.v = 0														# View Number for the current request
		self.c = self													# Client Id
		self.s  = 0														# Request Number
		self.primary = config[v]
		self.results = dict()
		print("Client::", self, "Setup Complete")


		# DS for measuring Performance
		self.perf_data = []
		self.cur_req = 0

	def run():
		output("==============Client Running ====================")
		success = True
		for i in range(n_requests):
			perf_data.append(time.perf_counter())
			curr_op = random.randint(0, MAX_NOPS-1)						# Operation to be carried out 
			output("==============Sending request to primary :", s, curr_op)
			send(('REQUEST',(curr_op, c, s)), to=primary)
			success = False
			if await(s in results):
				s += 1
				success = True
			elif timeout(tout):											# Need to reinitiate transfer of last request
				output("CLIENT::Timeout Occured on REPLY for op", curr_op)
				output('Resending request to all replicas')
				while success != True:
					send(('REQUEST',(curr_op, self, s)),to=replicas)
					if await(s in results):
						output('For request number ->', s, results[s])
						success = True
						s += 1 
					elif timeout(tout):
						output('Im Client, Seems like the system is still under view change or something bad has happened. Keep resending to all replicas')	
			
		await(each(op in range(s), has= op in results))
		output('All operations are done. Client is terminating')
		send(('done',), to=parent())
		await(received(('done')))

	def receive(msg= ('REPLY', viewNum, cid, result)):
		output("CLIENT :: Got response:", result,"for request number:",cid)
		tend = time.perf_counter()
		perf_data[cur_req] = tend - perf_data[cur_req]
		cur_req = cur_req + 1
		if v  != viewNum:
			v = viewNum
			primary = config[v]
		
		output("======I'm client and I think the current view is :", v)
		if cid not in results:
			results[cid] = result
		elif results[cid] != result:
			output('different result for request', cid, result, 'than', results[cid])

	def receive(msg= ('send_log'), from_= tm):
		send(('client_log',self,perf_data), to =tm)

#****************************************************************************************************************
# 													Replica
# 		 Replicas participate in processing of client requests only when their status is normal.
#		 All participating replicas are in the same view.
#		 Initial view number is 0
#		 Status can be "NORMAL , "VIEW_CHANGE" or "RECOVERY". Always starts in Normal mode.
# 		 Sends Commit Message incase there are no REQUEST from client within timwout period
#
#****************************************************************************************************************

class Replica(process):

#************************************************************************************************************
#                            			 VR - State at  Replica
# • The configuration: This is a sorted array containing the IP addresses of each of the 2f + 1 replicas.
# • The replica number: This is the index into the con- figuration where this replica’s IP address is stored.
# • The current view-number, initially 0.
# • The current status, either normal, view-change, or recovering.
# • The op-number assigned to the most recently received request, initially 0.
# • The log. This is an array containing op-number entries. The entries contain the requests that have been 
#   received so far in their assigned order.
# • The commit-number is the op-number of the most recently committed operation.
# • The client-table: This records for each client the number of its most recent request, plus, if the re- 
#   quest has been executed, the result sent for that re- quest.
#*************************************************************************************************************

	def setup(replicas:set, quorumsize:int, tout:float):

		#State vsriables for the replica
		# We don't need The replica number. This is the index into the con- figuration where this replica’s IP address is stored.

		self.status = "normal"			# The current status, either normal, view-change, or recovering.
		self.v = 0						# The current view-number, initially 0.
		self.s = 0
		self.n = 0						# The op-number assigned to the most recently received request, initially 0.
		self.k = 0						# The commit-number is the op-number of the most recently committed operation.
		self.logs = list()				# The log. This is an array containing op-number entries. The entries contain the requests that have been received so far in their assigned order.
		self.client_table = dict() 		# The client-table. This records for each client the number of its most recent request, plus, if the request has been executed, the result sent for that request.
		self.config = list(replicas)	# Theconfiguration. This is a sorted array containing the IP addresses of each of the 2f + 1 replicas.
		self.config.sort()
		replicas = replicas - {self}

		#Timeout and heartbeat Implementation variables
		self.num_req_latest = 0
		self.num_req_obsolete = 0
		self.num_prepare_latest = 0
		self.num_prepare_obsolete = 0
		self.heartbeat = 0;
		self.last_commit_num = 0


		# View Change implementation variable
		self.start_view_change_req = set()
		self.last_normal_view = 0

		#Control Variables
		self.done = False

		output("SETUP:: Successfully Completed ")

	def run():
		while not done:
			if status == "normal":
				if(self == config[v]):
					start_primary_timer()
				else:
					start_backup_timer()
			else:
				await((status == "normal" or done == True))

		output("Received done from parent. Terminating Now!")

	def commit_prev_oper():
		"""
		Section 4, page 4, Point 7
		When a backup learns of a commit, it waits un- til it has the request in its log (which may require state transfer)
		and until it has executed all earlier operations. Then it executes the operation by per- forming the up-call to the
		service code, increments its commit-number, updates the client’s entry in the client-table, but does not send the 
		reply to the client.
		"""
		if(k < last_commit_num and some((op,m) in logs, has= op == last_commit_num)):	   							# waits un- til it has the request in its log 
			my_commit = k + 1
			output("Backup: Some pending operations will be committed now ")
								#  and until it has executed all earlier operations.
			for op in range(my_commit,last_commit_num):
				message = setof(msg, (oper,msg) in logs, oper == op )
				message = list(message)
				cur_msg = message[0]
				k = k + 1																							# increments its commit-number,

				client_table[cur_msg[1]][1] = True																	# updates the client’s entry in the client-table,
				client_table[cur_msg[1]][2] = "answer = "+ str(cur_msg[2])
				output("#### Backup: Completing old operations..current commit number and op", k, cur_msg[0])
							#Then it executes the operation by per- forming the up-call to the service code,
			k = k + 1																								# increments its commit-number
			client_table[m[1]][1] = True																			# updates the client’s entry in the client-table
			client_table[m[1]][2] = "answer = "+ str(m[2])
			output("#### Backup: Latest Commit number  and operation ",k , m[0])

	def start_backup_timer():
		debug("Length of set of op-nums: ",len(setof(n, received(('PREPARE', _,_,n,_), from_=primary))))
		debug("Received Prepares latest: ",num_prepare_latest)
		
		"""
		Section 4, normal operation, point 4, page 7
		Backups process PREPARE messages in order: a backup won’t accept a prepare with op-number n until 
		it has entries for all earlier requests in its log. When a backup i receives a PREPARE message, it 
		waits until it has entries in its log for all earlier requests (doing state transfer if necessary 
		to get the missing information). 
		"""
		output("Waiting for Prepare having next op num: ", n+1)

		if await(some(received(('PREPARE',_v,m,n+1,_), from_=config[v]))):              #await till it has all entries
			commit_prev_oper()
			n = n + 1    										# Then it increments it's opnumber 
			logs.append((n,m))									# Adds the request to the end of its log,
			output("--------------Logs: ",logs)
			client_table[m[1]] = [m[2], False, None]			# updates the client’s information in the client-table,
			output("---------------------------First Instance::", client_table[m[1]])
			output("Sending PREPARE_OK to primary")
			send(('PREPARE_OK', v, n, self), to= config[v])		# sends a (PREPAREOK v, n, i) message to the pri- mary to indicate that this operation and all earlier ones have prepared locally.
		
		elif ( (num_prepare_latest > num_prepare_obsolete) or heartbeat == 1):
			num_prepare_obsolete = num_prepare_latest
			output("============prepare message/heartbeat from the primary received==============")
			commit_prev_oper()				
			heartbeat = 0

		elif timeout(tout+2):
			last_normal_view = v
			start_view_change_req.clear()
			v = (v + 1)%len(replicas)								# A replica i that notices the need for a view change advances its view-number
			status = "view_change"									# Sets its status to view_change
			output("============REQUESTING VIEW CHANGE===========", v)
			send(('START_VIEW_CHANGE', v, self), to=replicas)
			#send(('DO-VIEW-CHANGE', v, logs, k, self), to=config[v])

	def start_primary_timer():
		#output("Inside start_req_timer")
		if await(num_req_latest > num_req_obsolete):
			num_req_obsolete = num_req_latest
		elif timeout(tout):
			send(('COMMIT',v,k), to= replicas)


	def perform(p):
		debug('### perform', p)
		client, s, op = p
		debug('===', state, op)
		next, result = operations[op](state)
		debug('===', next, result)
		state = next
		return result

	def get_vs_max(c):
		if c not in client_table.keys():
			vs_max = -1
		else:
			vs_max =  client_table[c][0]			#max(setof(req, received(('REQUEST',_,_c, req))))
		
		return vs_max

	def receive(msg=('REQUEST', m,), from_= client):
		if self == config[v] and status == "normal":
			#output("Inside REQUEST Hndlr")
			output("==============received request from client =============", client)
			num_req_latest += 1
			(op, c, s) = m
			
			"""
			Section 4, normal operation, point 2, page 7
			When the primary receives the request, it compares the request-number in the request with the information in the client table.
			If the request-number s isn’t bigger than the information in the table it drops the request, but it will re-send the response 
			if the re- quest is the most recent one from this client and it has already been executed.

			The primary advances op-number, adds the request to the end of the log, and updates the information for this client in the 
			client-table to contain the new request number, s. Then it sends a (PREPARE v, m, n, k) message to the other replicas, 
			where v is the current view-number, m is the message it received from the client, n is the op-number it assigned to the request, 
			and k is the commit-number.
			"""
			vs_max =  get_vs_max(c)			# It compares the request-number in the request with the information in the client table.
			if s > vs_max:					# If the request-number s isn’t bigger than the information in the table it drops the request	
				n = n + 1										# The primary advances op-number
				logs.append((n,m))					# adds the request to the end of the log
				client_table[c]  = (s, False, None)				# Updates the information for this client in the client-table to contain the new request number 's'
				send(('PREPARE', v, m, n, k), to=replicas)		# Then it sends a (PREPARE v, m, n, k) message to the other replicas, n is the op-num it assigned to the request, k is the commit num
				#if(self == config[0] and n == 1):
					#output("**********************CRRRAAAAAASSSSSSHHHHHHEEEEEEDDDDDDDD************************")
					#crash(100000)

			# It will re-send the response, if the request is the most recent one from this client and it has already been executed.
			elif s == vs_max and client_table[c][1] != "#":
				send(('REPLY',(v, m[2], client_table[m[1]][1])), to= client)

			# If the request-number s isn’t bigger than the information in the table it drops the request
			else:
				pass
	
	def receive(msg=('PREPARE',view_num, m, op_num, commit_num), from_= primary):
		if self != config[v] and status == "normal":
			output("Received prepare from primary with op num:", op_num, "for client:", m[1])
			num_prepare_latest += 1
			
			"""
			Section 4, normal operation, point 4, page 7
			Backups process PREPARE messages in order: a backup won’t accept a prepare with op-number n until 
			it has entries for all earlier requests in its log. When a backup i receives a PREPARE message, it 
			waits until it has entries in its log for all earlier requests (doing state transfer if necessary 
			to get the missing information). 
			Handling this inside the run method as its a bad idea to wait inside the event handler.
			"""
			output("PREPARE::",view_num, m, op_num, commit_num)
			if commit_num > last_commit_num:
				last_commit_num = commit_num


	def receive(msg=('PREPARE_OK',view_num, op_num, i), from_= replica):
	
		"""
		Section 4, normal operation, point 5, page 7
		The primary waits for f PREPAREOK messages from different backups; at this point it considers the operation 
		(and all earlier ones) to be committed. Then, after it has executed all earlier operations (those assigned 
		smaller op-numbers), the primary executes the operation by making an up-call to the service code, and increments 
		its commit-number. Then it sends a hREPLY v, s, xi message to the client; here v is the view-number, s is the 
		number the client provided in the request, and x is the result of the up-call. The primary also updates the 
		client’s entry in the client-table to contain the result.
		"""
		if self == config[v] and status == "normal":
			#output("Inside PREPARE_OK hndlr")
			if (len(setof(rep, received(('PREPARE_OK', _, _op_num, rep)))) >= quorumsize):     #check for f 'PREPAREOK messages
				start = k + 1
				for operation in range(start, op_num+1):
					output("Primary has some uncommited operations. Will Commit now")
					client_info = setof(m, (op,m) in logs, op == operation)
					ci = list(client_info)
					(oper, client, req) = ci[0]
					if (req > client_table[client][0]) or (client_table[client][1] == False):
						# Do the client operation here
						client_table[client] = (req, True, "answer = "+ str(client)+ " " +str(oper))
						k = k + 1
						output("### PRIMARY: Commit Number and operation:", k, oper)
						send(('REPLY', v, req, client_table[client][2]), to= client)


	def receive(msg=('COMMIT',v,k), from_=primary):
		if self != config[v] and status == 'normal':
			output("Received Heartbeat/COMMIT from the primary:", primary, k)
			heartbeat = 1
			if k > last_commit_num:						#Ignore older commit messages and only consider the latest one.
				last_commit_num = k

	
	def receive(msg=('START_VIEW', viewNum, l, op_num, commit_num, rep), from_=primary):
		'''
		Section 4, view change mode, point 5 page 6
		When other replicas receive the STARTVIEW message, they replace their log 
		with the one in the message, set their op-number to that of the latest entry 
		in the log, set their view-number to the view num- ber in the message, change 
		their status to normal, and update the information in their client-table.
		Then they execute all op- erations known to be committed that they haven’t 
		executed previously, advance their commit-number, and update the information 
		in their client-table.
		'''
		if config[viewNum] != rep:
			output("ERROR:: Primary Mismatch")
			while 1:
				pass
		if status == "view_change":
			status = "normal"
			v = viewNum
			output("=================Moved to New view===========",v, commit_num)
			output("Logs = ", l)
			n = op_num
			logs = l

			if commit_num < n:
				output("Sending PREPARE_OK to primary", v, n)
				send(('PREPARE_OK', v, n, self), to= config[v])
				start = k+1
				for commit in range(start, commit_num+1):
					message = setof(msg, (oper,msg) in logs,  oper == commit )
					message = list(message)

					cur_msg = message[0]																				# increments its commit-number,
					# ToDo: Perform actual client operation at this place.
					client_table[cur_msg[1]][1] = True																	# updates the client’s entry in the client-table,
					client_table[cur_msg[1]][2] = "answer = "+ str(cur_msg[2])
					output("#### START_VIEW: Completing old operations..current commit number and op", k, cur_msg[0])
					k = k + 1


	def receive(msg=('DO_VIEW_CHANGE', view, log, l_view, op_number, commit_number, r)):
		'''
		(From vr-revis, page 5, 4.2 View Changes, point 3)
		When the new primary receives f + 1 DOVIEWCHANGE messages from different replicas 
		including itself, it sets its view-number to that in the messages and selects 
		as the new log the one contained in the message with the largest v′; if several 
		messages have the same v′ it selects the one among them with the largest n. It 
		sets its op-number to that of the topmost entry in the new log, sets its commit-number 
		to the largest such number it received in the DOVIEWCHANGE mes- sages, changes its 
		status to normal, and informs the other replicas of the completion of the view 
		change by sending ⟨STARTVIEW v, l, n, k⟩ messages to the other replicas, where 
		l is the new log, n is the op-number, and k is the commit-number.

		(From vr-revis, page 6, 4.2 View Changes, point 4)
		The new primary starts accepting client requests. It also executes (in order) any 
		committed operations that it hadn’t executed previously, updates its client table, 
		and sends the replies to the clients.
		'''
		if status == "view_change":
			output("=========== INSIDE DoViewChange method ================")
			# ToDo:  Modify below to have the condition that messaqge if received from itself.
			if len(setof(rep, received(('DO_VIEW_CHANGE',_view,_,_,_,_,rep)))) > quorumsize:
				v = view
				output("============VIEW CHANGE HAPPENING ===========")
				vn = max(setof(prev_view, received(('DO_VIEW_CHANGE', _v, _, prev_view, _, _, _)))) 
				output("Largest prev_view =", vn)
				new_op = max(setof(n, some(received(('DO_VIEW_CHANGE', _v , _, previous_view, _, _, _)), has= previous_view == vn)) or {0}) 
				output("Largest op number in largest prev_view :", vn, " is :", new_op)
				logs = list(list(setof(tuple(log1), received(('DO_VIEW_CHANGE', _v, log1, _vn, _new_op, _, _)), len(log1) != 0))[0])
				output("Largest Log = ", logs)
				if len(logs) > 0:
					n = logs[-1][0]
					output("Setting op number to = ", n)
				latest_commit = max(setof(k, some(received(('DO_VIEW_CHANGE',_v ,_, _, _, k, _)))) or {0})
				k = latest_commit
				output ("the latest commit :", k)
				status = "normal"
				
				output("==================sending startview to replicas==========",replicas)
				send(('START_VIEW', v, logs, n, k, self),to=replicas)

	def receive(msg=('START_VIEW_CHANGE', viewNum, r)):
		'''
		(From vr-revis, page 5, 4.2 View Changes, point 1
		A replica notices the need for a view change either based on its own timer, or because
		it receives a STARTVIEWCHANGE or DOVIEWCHANGE message for a view with a larger number 
		than its own view-number.
		'''
		output("Received START_VIEW_CHANGE message", viewNum, r, v)
		if viewNum > v and status == 'normal':
			last_normal_view = v
			v = viewNum
			start_view_change_req.clear()
			status = "view_change"
			output("=========== INSIDE START_VIEW_CHANGE handler ================")
			output("============REQUESTING VIEW CHANGE===========")
			send(('START_VIEW_CHANGE', v),to=replicas)
		'''
		(From vr-revis, page 5, 4.2 View Changes, point 2)[LOC 104-117]
		When replica i receives STARTVIEWCHANGE messages for its view-number from f other 
		replicas, it sends a ⟨DOVIEWCHANGE v, l, v’, n, k, i⟩ message to the node that 
		will be the primary in the new view. Here v is its view-number, l is its log, 
		v′ is the view number of the latest view in which its status was normal, n is 
		the op-number, and k is the commit- number.
		'''
		if viewNum == v and status == "view_change":
			start_view_change_req.add(r)
			if len(start_view_change_req) >= quorumsize:
				output("**********Sending message: DO_VIEW_CHANGE**********")
				send(('DO_VIEW_CHANGE', v, logs, last_normal_view, n, k, self),to=config[v])

			
			
	'''
	(From vr-revis, page 6, section 4.3: Recovery, point 2)
	A replica j replies to a RECOVERY message only when its status is normal. 
	In this case the replica sends a RECOVERYRESPONSE <v, x, l, n, k, j> mes- sage to the recovering replica,
	where v is its view- number and x is the nonce in the RECOVERY mes- sage. 
	If j is the primary of its view, l is its log, n is its op-number, and k is the commit-number; 
	other- wise these values are nil.
	'''
	def receive(msg=('Recovery', node, nonce)):
		if status == "normal":
			if self == config[v]:          #check if process is replica
				send(('RecoveryResponse', v, nonce, log, n, k, self), to=node)      #send recovery response
			else:
				send(('RecoveryResponse', v, nonce, None, op, commit, self), to=node)


	'''
	(From vr-revis, page 6, section 4,3: Recovery, point 3)
	The recovering replica waits to receive at least f + 1 RECOVERYRESPONSE messages from different replicas, 
	all containing the nonce it sent in its RE- COVERY message, 
	including one from the primary of the latest view it learns of in these messages. 
	Then it updates its state using the information from the primary, changes its status to normal, 
	and the recovery protocol is complete.
	'''
	def receive(msg=('RecoveryResponse', view, nonce, log, op, commit, r)):

		if len(setof(rep ,received(('RecoveryResponse',_,_x,_,_,_,rep)))) > f \
			and some(received(('RecoveryResponse',_, x1, l, op_num, backup)), has= backup == config[v]):
			v = view
			logs = log
			n = op
			k = commit
			status = "normal"
			output("=============the recovery replica has been updated and has joined the cluster ================",self)

	"""
	NOTE:
	Below mentioned API's/ henadlers are reqiored for validatation and performance measurement only
	They are not part of the algorithm
	"""

	# Call this when there is a crash to be injected
	def crash(tout):
		status = "dead"
		if await(done == True):
			exit(0)
		elif timeout(tout):
			status = "recovering"
			x = x + 1 
			send(('Recovery',self,x), to= replicas)


	def receive(msg=('send_log'), from_=p):
		mylist = []
		for val in  logs:
			mylist.append(val[0])
		send(('replica_log', self, mylist), to=p)


	def receive(msg=('done'), from_=parent()):
		done = True
		output("Received Done from parent.")
		exit()



def main():
	n = len(sys.argv)
	args = []				# List containing the arguments passed to this scrip
	
	script_name = sys.argv[0]
	print("Running main() of " + script_name)
	
	i = 1
	while i < n:
		print("Argument " + str(i) + " is " + sys.argv[i])
		args.append(int(sys.argv[i]))
		i = i + 1

	#We should have all the arguments in the list by now, Start execution
	f = args[0] if n > 1 else 1
	n_clients = args[1] if n > 2 else 5
	n_requests = args[2] if n > 3 else 10
	c_timeout = args[3] if n > 4 else 10
	r_timeout = args[4] if n > 5 else 5

	n_replicas = 2*f + 1
	quorumsize = f + 1
	
	manager = new(monitor.TestManager, num=1)
	replicas = new (Replica, num=n_replicas)
	clients  = new (Client, num=n_clients)
	setup(manager, (replicas, clients, "test.cfg"))
	setup(replicas,(replicas, f, r_timeout))
	setup(clients,(replicas, n_requests, c_timeout))
	start(manager)
	start(replicas)
	start(clients)

	await(each(c in clients, has=received(('done',), from_=c)))
	output('All Clients have finished doing operations')
	send(('start_validation'), to= manager) 
	await((received('done')))
	send(('done'), to= replicas|clients)

"""
Notes: In case the primary fails, the client will timeout and the backup replicas will initiate the view change protocol. 
		client will resend the request to all the replicas and waiut for the new primary to respond. View change protociol will 
		ensure that the new primary is decided. The new primary then reply back with the updated view number so that the client can
		update that as well.
		
		1. Create an external process which will be used for error injection. this will automate the error scenarios.
		2. Selected processes will crash and they will enter into recovery mode after a certain timeout which will be decided by the test node.
		3. Message Loss can be tested
		4. Reconfiguration - Not Supported

"""
