from __future__ import print_function
from subprocess import Popen, PIPE
import logging
import datetime
import pprint

'''
This is the updated version for XCP-NG 7.5
'''
# Create the Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create the Handler for logging data to a file
logger_handler = logging.FileHandler('/root/' + 'xen_backup.log')
logger_handler.setLevel(logging.INFO)

# Create a Formatter for formatting the log messages
logger_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')

# Add the Formatter to the Handler
logger_handler.setFormatter(logger_formatter)

# Add the Handler to the Logger
logger.addHandler(logger_handler)
# logger.info('Completed configuring logger()!')

logger.info('Started backup program at %s', datetime.datetime.now())

backup_path = '/run/sr-mount/c0749ff3-6f96-ebd7-9610-0ece005b7b9f/vm/'

vms_to_backup = ["phpchain01", "lnv1dkrsgc_clone", "wiki-yoda-docker", "lndlvpzabbproxy1", "ShotgunWebCgi", "lndlvlnp2back01"]

# get all the VMs on the server
command = Popen(['xe', 'vm-list'], stdout=PIPE)
response, err = command.communicate()

vmlist = []
if not err:
    machines = {}
 
    for vm in response.split('\n\n'):
        vmlist.append([x.strip() for x in vm.strip().split('\n')])

    vmlist = [x for x in vmlist if x != ['']]

    for machine in vmlist:
        machines[machine[1][machine[1].find(':')+1:].strip()] = {'uuid':machine[0][machine[0].find(':')+1:].strip(),'state':machine[2][machine[2].find(':')+1:].strip()}

    for k, v in machines.items():
        if k in vms_to_backup:
            snap_name = k + '-snap'
            snap_id = v['uuid']
            cmd = ['xe', 'vm-snapshot', 'new-name-label='+snap_name, 'vm='+snap_id]
            command = Popen(cmd, stdout=PIPE,stderr=PIPE)
            response, err = command.communicate()
            if not err:
                logger.info('Created snapshot for VM {}, at: {}'.format(k,datetime.datetime.now()))
                set_param = ['xe', 'template-param-set', 'is-a-template=false', 'uuid='+response.strip()]
                param_comm = Popen(set_param, stdout=PIPE)
                re, err = param_comm.communicate()
                export_comm = ['xe', 'vm-export', 'vm='+response.strip(), 'filename='+backup_path+k+str(datetime.date.today())+'.xva']
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
                        exit(1)
                else:
                    logger.error('Error ' + e + ' ' + str(datetime.datetime.now()))
                    exit(1)
            else:
                logger.error('Error ' + err + ' ' + str(datetime.datetime.now()))
                exit(1)
    logger.info('Backup completed sucessfully, deleting old backups')
    del_command = ['bash', '-c', '/root/del_back.sh']
    del_proc = Popen(del_command, stdout=PIPE)
    rex, ex = del_proc.communicate()
    if not ex:
        logger.info('Deleted old backups')
    else:
        logger.error('There was an error running the delete script: '+ex)
        exit(1)
else:
    logger.error('The vm-list command encountered an error: {}'.format(err))


