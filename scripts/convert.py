import glob

__author__ = 'jnejati'

import subprocess
import os
import shutil
import fileinput
import time


class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


class Convert():
   def __init__(self, run_no):
        self.run_no = run_no

   
   def clean_dir(self):
        dir_tobe_cleaned = [ './data/wprof_300_5_pro_1', './graphs', './temp_files/wprof_300_5_pro_1']
        for my_dir in dir_tobe_cleaned:
            if os.path.isdir(my_dir):
                for root, dirs, l_files in os.walk(my_dir):
                    for f in l_files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))
            else:
                os.makedirs(my_dir)

   def copy_all(self, src, dest):
        src_files = os.listdir(src)
        for file_name in src_files:
            full_file_name = os.path.join(src, file_name)
            if (os.path.isfile(full_file_name)):
                shutil.copy(full_file_name, dest)

   def do_analysis(self, profile, orig_modified, imp_type, site_name):
        return_value = True
        graphs_dir = ''
        if orig_modified == 'orig':
            graphs_dir = profile['device_type'] + '_' + profile['conn_type'] + '_' + profile['page_type'] + '_' + 'orig' + '_' + imp_type + '_' + site_name
        elif orig_modified == 'modified':
            graphs_dir = profile['device_type'] + '_' + profile['conn_type'] + '_' + profile['page_type'] + '_' + 'modified' + '_' + imp_type + '_' + site_name
        else:
            print('orig/modified?')
            return False
        if not os.path.isdir(graphs_dir):
            os.makedirs(graphs_dir)
            os.makedirs(os.path.join(graphs_dir, 'graphs'))
            #os.makedirs(os.path.join(graphs_dir, 'perf_logs'))
            os.makedirs(os.path.join(graphs_dir, 'perfsched_logs'))
            os.makedirs(os.path.join(graphs_dir, 'net_logs'))
            os.makedirs(os.path.join(graphs_dir, 'temp_files/pre_log_pro'))
            os.makedirs(os.path.join(graphs_dir, 'cgroups'))
        cgroups_dir = os.path.join(graphs_dir, 'cgroups')
        print(cgroups_dir, "Current directory:" + os.getcwd())
        cur_cgroup_dir = os.path.join(cgroups_dir, str(self.run_no))
        print(cur_cgroup_dir)
        os.mkdir(cur_cgroup_dir)
        os.makedirs(os.path.join(cur_cgroup_dir, 'cpu/browser'))
        os.makedirs(os.path.join(cur_cgroup_dir, 'cpuset/browser'))
        os.makedirs(os.path.join(cur_cgroup_dir, 'cpuacct/browser'))
        os.makedirs(os.path.join(cur_cgroup_dir, 'cpu/webserver'))
        os.makedirs(os.path.join(cur_cgroup_dir, 'cpuset/webserver'))
        os.makedirs(os.path.join(cur_cgroup_dir, 'cpuacct/webserver'))
        
        self.copy_all('/sys/fs/cgroup/cpu/browser/', os.path.join(cur_cgroup_dir, 'cpu/browser'))
        self.copy_all('/sys/fs/cgroup/cpuset/browser/', os.path.join(cur_cgroup_dir, 'cpuset/browser'))
        self.copy_all('/sys/fs/cgroup/cpuacct/browser/', os.path.join(cur_cgroup_dir, 'cpuacct/browser'))
        self.copy_all('/sys/fs/cgroup/cpu/webserver/', os.path.join(cur_cgroup_dir, 'cpu/webserver'))
        self.copy_all('/sys/fs/cgroup/cpuset/webserver/', os.path.join(cur_cgroup_dir, 'cpuset/webserver'))
        self.copy_all('/sys/fs/cgroup/cpuacct/webserver/', os.path.join(cur_cgroup_dir, 'cpuacct/webserver'))
        with cd('./tests/analysis_t'):
            self.clean_dir()
            print("Current directory:" + os.getcwd())
            if profile['device_type'] == 'desktop':
                com1 = 'perl' + ' ' + 'slice.pl' + ' ' + './pre_log'
            elif profile['device_type'] == 'mobile':
                com1 = 'perl' + ' ' + 'slicemobile-old.pl' + ' ' + './pre_log'

            #com2 = 'cp' + ' ' + './pre_log_pro/*' + ' ' + './data/wprof_300_5_pro_1/'
            com3 = 'perl' + ' ' + './analyze.pl'
            #com4 = 'cp' + ' ' + './graphs/* ' + graphs_dir + '/'
            """with cd('./pre_log'):
                for dirpath, dirnames, files in os.walk('./'):
                    if files:
                        print(dirpath, 'has files: ', files)
                        if orig_modified == 'orig':
                            print('current Directory:', os.getcwd())
                            for line in fileinput.input(files, inplace=1):
                                line = line.replace("original.testbed.localhost/", "")
                                line = line.replace("original.testbed.localhost_", "")
                                line = line.replace('original.testbed.localhost%2F', '')
                                print(line)
                        if orig_modified == 'modified':
                            for line in fileinput.input(files, inplace=1):
                                line = line.replace("modified.testbed.localhost/", "")
                                line = line.replace("modified.testbed.localhost_", "")
                                line = line.replace('modified.testbed.localhost%2F', '')
                                print(line)
                    if not files:
                        print(dirpath, 'is empty')"""
            try:
                proc = subprocess.call(com1.split(), shell=False, timeout=15)
                print("slicing")
                subprocess.call(['ls','./pre_log_pro'], shell=False, timeout=15)
            except subprocess.TimeoutExpired:
                print("Killed process " + " after timeout")
            print("slice done")
            for filename in glob.glob(os.path.join('./pre_log_pro/', '*.*')):
                shutil.copy(filename, './data/wprof_300_5_pro_1/')
            try:
                shutil.copytree('./pre_log_pro/', './data/pre_log_pro/')
            except FileExistsError:
                shutil.rmtree('./data/pre_log_pro/')
                shutil.copytree('./pre_log_pro/', './data/pre_log_pro/')

            start_time = time.time()
            try:
                proc = subprocess.call(com3.split(), shell=False, timeout=3000)
            except subprocess.TimeoutExpired:
                print("Killed process " + " after timeout")
            print("analyze done")
            print("--- %s seconds ---" % (time.time() - start_time))

        for dirpath, dirnames, files in os.walk('/home/jnejati/PLTSpeed/tests/analysis_t/graphs/'):
            if files:
                for filename in files:
                    if filename.endswith('.json'):
                        os.rename(os.path.join(dirpath, filename), os.path.join(dirpath, str(self.run_no) + '_' + filename))
                os.system('cp /home/jnejati/PLTSpeed/tests/analysis_t/graphs/* ' + os.path.join('/home/jnejati/PLTSpeed/' + graphs_dir, 'graphs/'))
                print("json files copied ")
                break
            else:
                print(dirpath, 'is empty, No Json file copied')
                return_value = False
        for dirpath, dirnames, files in os.walk('/home/jnejati/PLTSpeed/tests/analysis_t/perfsched_logs'):
            if files:
                for filename in files:
                    if filename.endswith('.data'):
                        os.rename(os.path.join(dirpath, filename), os.path.join(dirpath, str(self.run_no) + '_' + filename))
                os.system('cp /home/jnejati/PLTSpeed/tests/analysis_t/perfsched_logs/*.data ' + os.path.join('/home/jnejati/PLTSpeed/' + graphs_dir, 'perfsched_logs/'))
                print("perf sched files copied ")
                break
            else:
                print(dirpath, 'is empty, No perf sched file copied')

        """for dirpath, dirnames, files in os.walk('/home/jnejati/PLTSpeed/tests/analysis_t/chrometrace_logs'):
            if files:
                for filename in files:
                    if filename.endswith('.chrometrace'):
                        os.system('cp /home/jnejati/PLTSpeed/tests/analysis_t/chrometrace_logs/*.chrometrace ' + os.path.join('/home/jnejati/PLTSpeed/' + graphs_dir, 'chrometrace_logs/'))
                print("chrometrace files copied ")
                break
            else:
                print(dirpath, 'is empty, No chrometrace file copied')"""
       
        for dirpath, dirnames, files in os.walk('/home/jnejati/PLTSpeed/tests/analysis_t/net_logs'):
            if files:
                for filename in files:
                    if filename.endswith('.tcpdump'):
                        os.system('cp /home/jnejati/PLTSpeed/tests/analysis_t/net_logs/*.tcpdump ' + os.path.join('/home/jnejati/PLTSpeed/' + graphs_dir, 'net_logs/'))
                        #os.system('rm /home/jnejati/PLTSpeed/tests/analysis_t/net_logs/*.tcpdump ')
                print("tcpdump files copied ")
                break
            else:
                print(dirpath, 'is empty, No tcpdump file copied')
        """for dirpath, dirnames, files in os.walk('/home/jnejati/PLTSpeed/tests/analysis_t/net_logs'):
            if files:
                for filename in files:
                    if filename.endswith('.tcp'):
                        os.system('cp /home/jnejati/PLTSpeed/tests/analysis_t/net_logs/*.tcp ' + os.path.join('/home/jnejati/PLTSpeed/' + graphs_dir, 'net_logs/'))
                print("tcpprobe files copied ")
                break
            else:
                print(dirpath, 'is empty, No tcpprobe file copied')"""
        for dirpath, dirnames, files in os.walk('/home/jnejati/PLTSpeed/tests/analysis_t/temp_files/pre_log_pro/'):
            if files:
                for filename in files:
                    os.rename(os.path.join(dirpath, filename), os.path.join(dirpath, str(self.run_no) + '_' + filename))
                os.system('cp /home/jnejati/PLTSpeed/tests/analysis_t/temp_files/pre_log_pro/* ' + os.path.join('/home/jnejati/PLTSpeed/' + graphs_dir, 'temp_files/'))
                print("temp_files copied ")
                break
            else:
                print(dirpath, 'is empty, No Json file copied')

        with cd('./tests/analysis_t'):
            shutil.rmtree('./pre_log_pro')
            shutil.rmtree('./temp_files/pre_log_pro')
            shutil.rmtree('./data/pre_log_pro')
            perfsched_log_dir = '/home/jnejati/PLTSpeed/tests/analysis_t/perfsched_logs/'
            #chrometrace_log_dir = '/home/jnejati/PLTSpeed/tests/analysis_t/chrometrace_logs/'
            net_log_dir = '/home/jnejati/PLTSpeed/tests/analysis_t/net_logs/'
            if os.path.isdir(perfsched_log_dir):
                for root, dirs, l_files in os.walk(perfsched_log_dir):
                    for f in l_files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))
            else:
                os.makedirs(perfsched_log_dir)
            
            """if os.path.isdir(chrometrace_log_dir):
                for root, dirs, l_files in os.walk(chrometrace_log_dir):
                    for f in l_files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))
            else:
                os.makedirs(chrometrace_log_dir)"""
            if os.path.isdir(net_log_dir):
                for root, dirs, l_files in os.walk(net_log_dir):
                    for f in l_files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))
            else:
                os.makedirs(net_log_dir)
        return return_value
