
# writing method for automatic uploading and running AWG
import os 
import re,fnmatch
import subprocess
import sys
import threading
import itertools
import time
def upload(folder_path = None, timestamp = None):


	if folder_path is None:
		folder_path = os.getcwd()

	use_latest = True
	if timestamp is not None:
		use_latest = False



	dirname = fnmatch.filter(os.listdir(folder_path),"AwgFiles*")

	dirpath = None

	if use_latest:
		dirpath = os.path.join(os.getcwd(),dirname[-1])

	else:

		pattern = re.findall(r'\d+',timestamp)

		for dir in dirname:
			if pattern == re.findall(r'\d+',dir):
				dirpath = os.path.join(os.getcwd(),dir)

		if dirpath == None:
			raise IOError("Cannot find directory with timestamp {}".format(timestamp))


		os.chdir(dirpath)

		f = open('ftp.txt','w')
		f.write('open 192.168.1.51\n')
		f.write('\n')
		f.write('\n')
		f.write('binary\n')
		f.write('mput "*.wfm"\n')
		f.write('mput "*.seq"\n')
		f.write('disconnect\n')
		f.write('bye')

		f.close()
		t = threading.Thread(target=animate)
		t.start()
		if subprocess.call('ftp -v -i -s:ftp.txt') == 0:
			os.remove('ftp.txt')
			os.path.normpath(os.getcwd() + os.sep + os.pardir)



def animate():
	sys.stdout.write('uploading waveforms ' + '...')
	for c in itertools.cycle(['|', '/', '-', '\\']):
		if done:
			break
		sys.stdout.write('' + c)
		sys.stdout.flush()
		time.sleep(0.1)
	sys.stdout.write('\rDone!     ')


# def run():
# 	# default mode is triggered
# 	AWG.is_awg_ready()
# 	AWG.set_run_mode('TRIG')
# 	AWG.set_status('on',1)
# 	AWG.set_status('on',2)
# 	AWG.start()






done =  False
print(upload(timestamp= '2017-05-07-14-48-50'))
done = True