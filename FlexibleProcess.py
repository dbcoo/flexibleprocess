import multiprocessing, time

class StoppableProcess(multiprocessing.Process):
	# multiprocessing.Process class but can be stopped with the stop() method.
	def __init__(self, function, kwargs=False, daemon=True):
		multiprocessing.Process.__init__(self, daemon=True)
		self.kwargs = kwargs
		self.function = function
		self.kill_pill = multiprocessing.Event()

	def stop(self):
		self.kill_pill.set()

	def run(self):
		# DO NOT USE. Use start() instead. This is an override of multiprocessing.Process run() method.
		while not self.kill_pill.is_set():
			if self.kwargs:
				self.function(**self.kwargs)
			else:
				self.function()

class FlexibleProcess():
	def __init__(self, function, kwargs=False, timeout=False, grace_period=0.1):
		self.function = function
		self.kwargs = kwargs
		self.running = False
		self.timeout = timeout
		self.grace_period = grace_period

	def kill(self):
		# force terminating the process.
		self.process.terminate()

	def start(self):
		# start runing the function in a loop.
		if not self.running:
			self.process = StoppableProcess(self.function, kwargs=self.kwargs)
			self.process.start()
			self.running = True
		else:
			print('process already running.')

	def stop(self):
		# break the loop.
		self.process.stop()
		time.sleep(self.grace_period)
		if self.process.is_alive():
			self.kill()
		self.running = False

	def run_once(self):
		# runs the function, if it doesn't finish in the defined timeout, it get's killed.
		if self.kwargs:
			self.process = multiprocessing.Process(target=self.function, kwargs=self.kwargs)
		else:
			self.process = multiprocessing.Process(target=self.function)
		self.process.start()
		self.runing = True
		if self.timeout:
			kill_time = time.time() + self.timeout
			while time.time() < kill_time:
				time.sleep(self.grace_period)
				if not self.process.is_alive():
					self.runing = False
					return
			self.kill()
			self.runing = False
			return 'TERMINATED'

