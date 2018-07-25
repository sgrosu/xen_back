from __future__ import print_function
from subprocess import Popen, PIPE
import logging
import datetime

# Create the Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create the Handler for logging data to a file
logger_handler = logging.FileHandler('/root/' + 'backup_hosts.log')
logger_handler.setLevel(logging.INFO)

# Create a Formatter for formatting the log messages
logger_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')

# Add the Formatter to the Handler
logger_handler.setFormatter(logger_formatter)

# Add the Handler to the Logger
logger.addHandler(logger_handler)
# logger.info('Completed configuring logger()!')

logger.info('Started backup program at %s', datetime.datetime.now())

pool_path = '/run/sr-mount/da2d3b47-be79-d62a-f34d-97814eb7f293/VM/xen-server-itself/pool/'
host_path = '/run/sr-mount/da2d3b47-be79-d62a-f34d-97814eb7f293/VM/xen-server-itself/'

# back-up pool database


today = datetime.date.today()

command = Popen(['xe', 'pool-dump-database', 'file-name='+pool_path+'pool-database'+str(today)+'.bak'], stdout=PIPE)
response, err = command.communicate()

if not err:
    logger.info('Backup of the pool database successfully created: {}'.format(datetime.datetime.now()))
else:
    logger.error('Pool database backup unsuccessful - {}'.format(err))

# back-up host configuration and software

# get hosts

get_hosts = Popen(['xe', 'host-list'], stdout=PIPE)
get_resp, get_err = get_hosts.communicate()

hostlist = []

if not get_err:
    # print(repr(get_resp))
    # print(get_resp.rstrip('\n\n\n').split('\n\n'))
    for host in get_resp.rstrip('\n\n\n').split('\n\n'):
        hostlist.append(host.lstrip().split('\n')[1].strip().split(':')[1].strip())

    # backing up xen host itself

    for xenhost in hostlist:

        comm = Popen(['xe', 'host-backup', 'host='+xenhost ,'file-name='+host_path+xenhost+'_'+str(today)+'.xbk'], stdout=PIPE)
        resp, error = comm.communicate()

        if not err:
            logger.info('Server {0} backed up successfully" - {1}'.format(xenhost, datetime.datetime.now()))
        else:
            logger.error('Backing up server {0} failed! - {1} - {2}'.format(xenhost, err, datetime.datetime.now()))

else:
    logger.error("Getting the hosts command failed - {0} - {1}".format(get_err,datetime.datetime.now()))




