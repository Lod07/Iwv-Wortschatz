
import psutil
import os
import threading
import time
import datetime
import timeit
import numpy as np
from queue import Queue

import cProfile
import pstats



# this class can be used to create a full profile for the runtime of your script
# it uses the cProfile library
class CProfiler:

    def __init__(self):
        pass

    # this function profiles a given function call with the specified arguments and writes the results into the specified log
    # param: func - the function you want to profile (could be your scripts main function for a complete profile)
    # param: args - a dict including all arguments needed for the function call ( {"paramName" : paramValue} )
    # param: n_outputs - the number of of output lines you want to have, the lines will be sorted by the cumulative time spent in that function
    #                    set to 0 to print full output (recommended in most scenarios)
    # param: log_path - the path of the target log to print the results to
    def profileCall(self, func, args = {}, n_outputs = 0, log_path="cProfileLog.txt"):
        # TODO: this function does not need to be specified in a class, but in case we would want to
        # extend this class with some more tools for analyzing the output, we could put everything in here
        profiler = cProfile.Profile()
        profiler.enable()
    
        func(**args)

        profiler.disable()

        stream = open(log_path, 'w')
        stats: pstats.Stats = pstats.Stats(profiler, stream=stream)
        stats.sort_stats('cumtime')
        if(n_outputs > 0):
            stats.print_stats(n_outputs)
        else:
            stats.print_stats()
        stream.close()

# this class consists of a couple fo founctions to make internal measures of your scripts performance,
# all of the results will be printed into a log file
class PerformanceTracker:

    ################################
    # initializing and destroying

    # class constructor
    # param: log_path - specifies the path where the logfile should be saved
    def __init__(self, log_path="log.txt"):
        self.logQueue = Queue()

        self.killLogThread = threading.Event()
        self.killSysMonThread = threading.Event()
        self.psutilThread = None

        self.loggerThread= threading.Thread(target=self.loggerThreadFunc, args=[log_path])
        self.loggerThread.start()

        self.timeSections = {}

    # this MUST be called when the logging is finished, this handles shutting down all running threads
    def close(self):
        if(self.psutilThread != None):
            self.stopSystemMonitor()

        self.killLogThread.set()
        if self.loggerThread.is_alive():
            self.loggerThread.join()

        self.started = False

    ################################
    # TIME
    # calling this function marks the beginning of a time section with a specified name
    def startTimeSection(self, name):
        if name in self.timeSections:
            print(f"[Error] tried to start allready started time section: {name}")
            return
        self._LOG(f"Starting Section: {name}")
        self.timeSections[name] = time.time()

    # this will end the time segment recording for a specific name, the time for the segment gets logged into the log file 
    def endTimeSection(self, name):
        if not name in self.timeSections:
            print(f"[Error] time section {name} can not be terminated as it was not started")
            return
        
        value = time.time() - self.timeSections[name]
        self.timeSections.pop(name)
        self._LOG(f"Finished Section: {name}")
        self._LOG((f'Section {name}: {(value * 1000):.02f}ms'))

    ################################
    # timeit

    # this can be used to test the runtime of very short code snippets
    # param: func (string) - this is the code you want to be timed
    # param: iterations (number) - the number of iterations you want the code to run through during time measurement
    def iterationTime(self, func, iterations = 1):
        laufzeit = timeit.timeit(func, number=iterations)
        self._LOG(f'Func: "{func}" with {iterations} Iterations: {(laufzeit) * 1000:.04f}ms')

    ################################
    # psutil

    # to not completely overload the log file it can be usefull
    # to only log this during specific parts of the code, ending the system
    # monitor also produces some basic statistics over the runtime of the 
    # monitored segment (see the system monitor thread implementation for detail)

    # this starts the system monitor thread
    # param: scan_interval - the time between to data points in milliseconds
    def startSystemMonitor(self, scan_interval = 1000):
        self.psutilThread= threading.Thread(target=self.psutilThreadFunc, args=[scan_interval])
        self._LOG("Started System Monitor")
        self.killSysMonThread.clear()
        self.psutilThread.start()

    # this stops the system monitor
    def stopSystemMonitor(self):
        self._LOG("Stopped System Monitor")
        self.killSysMonThread.set()
        if self.psutilThread.is_alive():
            self.psutilThread.join()

    ################################
    # Thread functions for system monitor and logging

    # the logging is done on a seperate thread to synchronize the file access
    # between the main thread and the system monitor thread

    # implementation of the logging thread
    def loggerThreadFunc(self, log_path):
        log_file = open(log_path, "w")
        while not self.killLogThread.is_set():
            time.sleep(0.01)
            while not self.logQueue.empty():
                log_file.write(self.logQueue.get())
                log_file.write("\n")
        log_file.close()

    # implementation of the system monitor thread
    # the thread records overall cpu load and the process memory load (process memory, not overall system memory)
    # when killed, the thread will log the peak memory load as well as peak CPU utilization
    def psutilThreadFunc(self, time_interval):
        process = psutil.Process(os.getpid())
        timestep = time_interval
        lastTick = time.time()*1000.0

        process_memory_ticks = [process.memory_percent() ]
        cpu_overall_ticks = [psutil.cpu_percent()]

        while not self.killSysMonThread.is_set():
            time.sleep(0.01)
            counter = time.time()*1000.0

            if(counter - lastTick > timestep):
                lastTick = counter

                mem = process.memory_percent()  
                cpu_utilis = psutil.cpu_percent()

                process_memory_ticks.append(mem)
                cpu_overall_ticks.append(cpu_utilis)

                self._LOG((f'Memory: {mem}'))
                self._LOG((f'CPU Overall: {cpu_utilis}'))

        pm_tick_arr = np.array(process_memory_ticks)
        cpu_tick_arr = np.array(cpu_overall_ticks)

        self._LOG((f'Memory Max: {pm_tick_arr.max()} - Median: {np.median(pm_tick_arr)} - Avg: {pm_tick_arr.mean()}'))
        self._LOG((f'CPU Max: {cpu_tick_arr.max()} - Median: {np.median(cpu_tick_arr)} - Avg: {cpu_tick_arr.mean()}'))

        # TODO: maybe do some visualization in here and save them, could be interesting for monitoring memory usage over time

    ################################
    # UTILITY FUNCTIONS FOR LOGGING
    # not inteded to be used from the outside
    def _LOG(self, msg):
        self.logQueue.put(self.getLogString(msg))

    def getLogString(self, str):
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        return f'[{timestamp}] - {str}'
    ################################

# some test code to make sure the script runs correctly
def hello(text):
    print(f"Hello {text}")

if __name__ == "__main__":
    tr = PerformanceTracker()

    tr.startTimeSection("section a")
    tr.startTimeSection("section b")

    tr.startSystemMonitor(500)
    time.sleep(3)
    tr.stopSystemMonitor()
    
    tr.endTimeSection("section a")
    tr.startTimeSection("section c")

    tr.iterationTime("x = 10**3 * 22", 100000000)
    
    tr.endTimeSection("section c")
    tr.endTimeSection("section b")

    tr.close()


    cp = CProfiler()

    args = {
        "text": "World"
    }

    cp.profileCall(hello, args)
