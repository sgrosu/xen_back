from __future__ import print_function
from subprocess import Popen, PIPE
import logging
import datetime

# Create the Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create the Handler for logging data to a file
logger_handler = logging.FileHandler('/root/' + 'backup.log')
logger_handler.setLevel(logging.INFO)

# Create a Formatter for formatting the log messages
logger_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')

# Add the Formatter to the Handler
logger_handler.setFormatter(logger_formatter)

# Add the Handler to the Logger
logger.addHandler(logger_handler)
# logger.info('Completed configuring logger()!')

logger.info('Started backup program at %s', datetime.datetime.now())

backup_path = '/run/sr-mount/da2d3b47-be79-d62a-f34d-97814eb7f293/VM/Current/'

# get all the VMs on the server


command = Popen(['xe', 'vm-list'], stdout=PIPE)
response, err = command.communicate()

vmlist = []
if not err:
    machines = {}
    #vmlist = response.split('\n\n')

    for vm in response.split('\n\n'):
        vmlist.append([x.strip() for x in vm.strip().split('\n')])
    vmlist = vmlist[:-1]
    #print(vmlist)
    for machine in vmlist:
        machines[machine[1][machine[1].find(':')+1:].strip()] = {'uuid':machine[0][machine[0].find(':')+1:].strip(),'state':machine[2][machine[2].find(':')+1:].strip()}
    #print(machines)
    for k, v in machines.items():
        if ('Control' not in k) and ('XOA' not in k) and ('Andres' not in k) and  v['state'] != 'halted':
            snap_name = k + '-snap'
            snap_id = v['uuid']
            cmd = ['xe', 'vm-snapshot', 'new-name-label='+snap_name, 'vm='+snap_id]
            #print(cmd)
            command = Popen(cmd, stdout=PIPE,stderr=PIPE)
            response, err = command.communicate()
            if not err:
                logger.info('Created snapshot for VM {}, at: {}'.format(k,datetime.datetime.now()))
                export_comm = ['xe', 'vm-export', 'vm='+response, 'filename='+backup_path+k+str(datetime.date.today())+'.xva']
                c = Popen(export_comm, stdout=PIPE)
                r, e = c.communicate()
                if not e:
                    logger.info('Snapshot for VM ' + k + '->' + r + ' ' + str(datetime.datetime.now()))
                    destroy_comm = ['xe', 'snapshot-uninstall', 'uuid='+response, 'force=true']
                    proc = Popen(destroy_comm, stdout=PIPE)
                    res, er = proc.communicate()
                    if not er:
                        logger.info('Snapshot for VM '+ k + ' deleted! ' + str(datetime.datetime.now()))
                    else:
                        logger.error('Error: ' + er + ' ' + str(datetime.datetime.now()))
                else:
                    logger.error('Error ' + e + ' ' + str(datetime.datetime.now()))
            else:
                logger.error('Error ' + err + ' ' + str(datetime.datetime.now()))
            #break
else:
    logger.error('The vm-list command encountered an error: {}'.format(err))


#print(vmlist)


