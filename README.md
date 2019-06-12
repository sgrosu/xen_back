# xen_back v3
This program is supposed to run on a XEN VM host. You need to tweak the backup_path variable to point to your Storage Repository 
and also populate the vms_to_backup list with the names of the virtual machines included in the backup schedule.
If the backup completes successfuly it calls for the del_back.sh bash script that deletes backups older than 2 days.

v3 is adapted to work on XCP-NG 7.5. I expect it to work on vanilla installations of Xen 7.5 as well.
