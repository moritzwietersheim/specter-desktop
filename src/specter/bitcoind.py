''' Stuff to control a bitcoind-instance. Either directly by access to a bitcoind-executable or
    via docker.
'''
import atexit
import logging
import shutil
import subprocess
import tempfile
import time

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

import docker
from helpers import which


class Btcd_conn:
    ''' An object to easily store connection data '''
    def __init__(self, rpcuser="bitcoin", rpcpassword="secret", rpcport=18543, ipaddress=None):
        self.rpcport = rpcport
        self.rpcuser = rpcuser
        self.rpcpassword = rpcpassword
        self._ipaddress = ipaddress

    @property
    def ipaddress(self):
        if self._ipaddress == None:
            raise Exception("ipadress is none")
        else:
            return self._ipaddress


    @ipaddress.setter
    def ipaddress(self,ipaddress):
        self._ipaddress = ipaddress

    def get_rpcconn(self):
        ''' returns a working AuthServiceProxy for the bitcoind '''
        url = self.render_url()
        rpc = AuthServiceProxy(url)
        rpc.getblockchaininfo()
        logging.debug("created bitcoind-url {} is working".format(url))
        return rpc

    def render_url(self):
        return 'http://{}:{}@{}:{}/wallet/'.format(self.rpcuser, self.rpcpassword, self.ipaddress, self.rpcport)
    
    def __repr__(self):
        return '<Btcd_conn {}>'.format(self.render_url())

class BitcoindController:
    ''' A kind of abstract class to simplify running a bitcoind with or without docker '''
    def __init__(self, rpcport=18443):
        self.rpcconn = Btcd_conn(rpcport=rpcport)
        self.bitcoind_exec = which('bitcoind')

    def start_bitcoind(self, cleanup_at_exit=False):
        ''' starts bitcoind with a specific rpcport=18543 by default.
            That's not the standard in order to make pytest running while
            developing locally against a different regtest-instance
            if bitcoind_path == docker, it'll run bitcoind via docker
        '''
        if self.check_existing() != None:
            return self.check_existing()

        self._start_bitcoind(cleanup_at_exit)

        self.wait_for_bitcoind(self.rpcconn)
        self.mine(block_count=100)
        return self.rpcconn

    def _start_bitcoind(self, cleanup_at_exit):
        raise Exception("This should not be used in the baseclass!")

    def check_existing(self):
        raise Exception("This should not be used in the baseclass!")

    def stop_bitcoind(self):
        raise Exception("This should not be used in the baseclass!")

    def mine(self, address=None, block_count=1):
        ''' Does mining to the attached address with as many as block_count blocks '''
        if address == None:
            address = self.rpcconn.get_rpcconn().getnewaddress()
        logging.debug("Mining!")
        self.rpcconn.get_rpcconn().generatetoaddress(block_count, address)
        
    @staticmethod
    def check_bitcoind(rpcconn):
        ''' returns true if bitcoind is running on that address/port '''
        try:
            rpcconn.get_rpcconn() # that call will also check the connection
            return True
        except ConnectionRefusedError:
            return False
        except TypeError:
            return False
        except JSONRPCException:
            return False

    @staticmethod
    def wait_for_bitcoind(rpcconn):
        ''' tries to reach the bitcoind via rpc. Will timeout after 10 seconds '''
        i = 0
        while True:
            if BitcoindController.check_bitcoind(rpcconn):
                break
            time.sleep(0.5)
            i = i + 1
            if i > 20:
                raise Exception("Timeout while trying to reach bitcoind at rpcport {} !".format(rpcconn))
        
    @staticmethod
    def render_rpc_options(rpcconn):
        options = " -rpcport={} -rpcuser={} -rpcpassword={} ".format(rpcconn.rpcport, rpcconn.rpcuser,rpcconn.rpcpassword)
        return options

    
    @classmethod
    def construct_bitcoind_cmd(cls, rpcconn, run_docker=True,datadir=None, bitcoind_path='bitcoind'):
        ''' returns a bitcoind-command to run bitcoind '''
        btcd_cmd = "{} ".format(bitcoind_path)
        btcd_cmd += " -regtest "
        btcd_cmd += " -port={} -rpcport={} -rpcbind=0.0.0.0 -rpcbind=0.0.0.0".format(rpcconn.rpcport-1,rpcconn.rpcport)
        btcd_cmd += " -rpcuser={} -rpcpassword={} ".format(rpcconn.rpcuser,rpcconn.rpcpassword)
        btcd_cmd += " -rpcallowip=0.0.0.0/0 -rpcallowip=172.17.0.0/16 "
        if not run_docker:
            btcd_cmd += " -noprinttoconsole"
            if datadir == None:
                datadir = tempfile.mkdtemp()
            btcd_cmd += " -datadir={} ".format(datadir)
        logging.debug(" constructed bitcoind-command: {}".format(btcd_cmd))
        return btcd_cmd

class BitcoindPlainController(BitcoindController):
    ''' A class controlling the bicoind-process directly on the machine '''
    def __init__(self, bitcoind_path='bitcoind', rpcport=18443):
        super().__init__(rpcport=rpcport)
        self.bitcoind_path = bitcoind_path
        self.rpcconn.ipaddress = 'localhost'

    def _start_bitcoind(self, cleanup_at_exit=False):
        datadir = tempfile.mkdtemp()
        bitcoind_cmd = self.construct_bitcoind_cmd(self.rpcconn, run_docker=False, datadir=datadir, bitcoind_path=self.bitcoind_path)
        logging.debug("About to execute: {}".format(bitcoind_cmd))
        # exec will prevent creating a child-process and will make bitcoind_proc.terminate() work as expected
        self.bitcoind_proc = subprocess.Popen("exec " + bitcoind_cmd, shell=True)  
        logging.debug("Running bitcoind-process with pid {}".format(self.bitcoind_proc.pid))
        def cleanup_bitcoind():
            self.bitcoind_proc.kill() # much faster then terminate() and speed is key here over being nice
            logging.debug("Killed bitcoind-process with pid {}".format(self.bitcoind_proc.pid))
            shutil.rmtree(datadir)
            logging.debug("removed temp-dir")
        if cleanup_at_exit:
            atexit.register(cleanup_bitcoind)
    
    def check_existing(self):
        ''' other then in docker, we won't check on the "instance-level". This will return true if if a 
            bitcoind is running on the default port. 
        '''
        if not self.check_bitcoind(self.rpcconn):
            return None
        else:
            return True

class BitcoindDockerController(BitcoindController):
    ''' A class specifically controlling a docker-based bitcoind-container '''
    def __init__(self,rpcport=18443):
        self.btcd_container = None
        super().__init__(rpcport=rpcport)
        self.docker_exec = which('docker')
        if self.docker_exec == None:
            raise("Docker not existing!")
        if self.detect_bitcoind_container(rpcport) != None:
            rpcconn, self.btcd_container = self.detect_bitcoind_container(rpcport)
            self.rpcconn = rpcconn

    def _start_bitcoind(self, cleanup_at_exit):
        bitcoind_path = self.construct_bitcoind_cmd(self.rpcconn )
        dclient = docker.from_env()
        logging.debug("Running (in docker): {}".format(bitcoind_path))
        ports={
            '{}/tcp'.format(self.rpcconn.rpcport-1): self.rpcconn.rpcport-1, 
            '{}/tcp'.format(self.rpcconn.rpcport): self.rpcconn.rpcport
        }
        logging.debug("portmapping: {}".format(ports))
        self.btcd_container = dclient.containers.run("registry.gitlab.com/k9ert/specter-desktop/python-bitcoind:latest", bitcoind_path,  ports=ports, detach=True)
        def cleanup_docker_bitcoind():
            self.btcd_container.stop()
            self.btcd_container.remove()
        if cleanup_at_exit:
            atexit.register(cleanup_docker_bitcoind)
        logging.debug("Waiting for container {} to come up".format(self.btcd_container.id))
        self.wait_for_container()
        rpcconn, _ = self.detect_bitcoind_container(self.rpcconn.rpcport)
        if rpcconn == None:
            raise Exception("Couldn't find container or it died already. Check the logs!")
        else:
            self.rpcconn = rpcconn
        

    def stop_bitcoind(self):
        if self.btcd_container != None:
            self.btcd_container.reload()
            if self.btcd_container.status == 'running':
                _, container = self.detect_bitcoind_container(self.rpcconn.rpcport)
                if container == self.btcd_container:
                    self.btcd_container.stop()
                    logging.info("Stopped btcd_container {}".format(self.btcd_container))
                    return 
        raise Exception('Ambigious Container running')

    def check_existing(self):
        ''' Checks whether self.btcd_container is up2date and not ambigious '''
        if self.btcd_container != None:
            self.btcd_container.reload()
            if self.btcd_container.status == 'running':
                rpcconn, container = self.detect_bitcoind_container(self.rpcconn.rpcport)
                if container == self.btcd_container:
                    return rpcconn
                raise Exception('Ambigious Container running')
        return None

    @staticmethod
    def search_bitcoind_container(all=False):
        ''' returns a list of containers which are running bitcoind '''
        d_client = docker.from_env()
        return [c for c in d_client.containers.list(all) if c.attrs['Config']['Cmd'][0]=='bitcoind']

    @staticmethod
    def detect_bitcoind_container(with_rpcport):
        ''' checks all the containers for a bitcoind one, parses the arguments and initializes 
            the object accordingly 
            returns rpcconn, btcd_container
        '''
        d_client = docker.from_env()
        potential_btcd_containers = BitcoindDockerController.search_bitcoind_container()
        if len(potential_btcd_containers) == 0:
            logging.debug("could not detect container. Candidates: {}".format(d_client.containers.list()))
            all_candidates = BitcoindDockerController.search_bitcoind_container(all=True)
            logging.debug("could not detect container. All Candidates: {}".format(all_candidates))
            if len(all_candidates) > 0:
                logging.debug("logs of first candidate")
                logging.debug(all_candidates[0].logs())
            return None
        for btcd_container in potential_btcd_containers:
            rpcport = int([arg for arg in btcd_container.attrs['Config']['Cmd'] if 'rpcport' in arg][0].split('=')[1])
            if rpcport != with_rpcport:
                logging.debug("checking port {} against searched port {}".format(type(rpcport), type(with_rpcport)))
                continue
            rpcpassword = [arg for arg in btcd_container.attrs['Config']['Cmd'] if 'rpcpassword' in arg][0].split('=')[1]
            rpcuser = [arg for arg in btcd_container.attrs['Config']['Cmd'] if 'rpcuser' in arg][0].split('=')[1]
            ipaddress = btcd_container.attrs['NetworkSettings']['IPAddress']
            rpcconn = Btcd_conn(rpcuser=rpcuser, rpcpassword=rpcpassword, rpcport=rpcport, ipaddress=ipaddress)
            logging.info("detected container {}".format(btcd_container.id))
            return rpcconn, btcd_container
        logging.debug("No matching container found")
        return None

    
    def wait_for_container(self):
        ''' waits for the docker-container to come up. Times out after 10 seconds '''
        i = 0
        while True:
            ip_address = self.btcd_container.attrs['NetworkSettings']['IPAddress']
            if ip_address.startswith("172"):
                self.rpcconn.ipaddress = ip_address
                break
            self.btcd_container.reload()
            time.sleep(0.5)
            i = i + 1
            if i > 20:
                raise Exception("Timeout while starting bitcoind-docker-container!")
