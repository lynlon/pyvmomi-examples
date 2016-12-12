from pyVmomi import vim
from pyVim.connect import SmartConnect, Disconnect
import getpass
import vmutils

si = None
username = raw_input('Username: ')
password = getpass.getpass(prompt='Password: ')
vcenter = raw_input('vcenter: ')

try:
    si = SmartConnect(host=vcenter, user=username, pwd=password, port=443)
except IOError, e:
    pass

# Finding source VM
newvm = raw_input('New vm name: ')
template_vm = vmutils.get_vm_by_name(si, 'centos-6.5-x64')

'''
There are two roads for modifying a vm creation from a template
1. ConfigSpec -> CloneSpec
2. ConfigSpec -> (AdapterMapping -> GlobalIPSettings -> LinuxPrep) -> CustomSpec -> CloneSpec
Notes: 
    ConfigSpec and CustomSpecificiation are purely optional and
    independent
'''

# cpu/ram changes
#mem = 512 * 1024 # convert to GB
mem = 512  # MB
vmconf = vim.vm.ConfigSpec(numCPUs=1, memoryMB=mem)
ipConf='10.0.1.10'
netMask='255.255.255.0'
gateWay='10.0.0.1'
dnsDefault=['8.8.8.8', '114.114.114.114']
#vmconf.deviceChange = devices

# Network adapter settings
adaptermap = vim.vm.customization.AdapterMapping()
if vmutils.is_valid_ip(ipConf) and len(ipConf.strip()) > 0 and len(netMask.strip()) > 0:
	if not vmutils.is_online_ip(ipConf):
		print 'ERROR: %s IP address already exists!' %(ipConf)
		sys.exit()
	# static ip
	#adaptermap.adapter = vim.vm.customization.IPSettings(ip=vim.vm.customization.FixedIp(ipAddress='10.0.1.10'),
	#                                                     subnetMask='255.255.255.0', gateway='10.0.0.1')
	adaptermap.adapter = vim.vm.customization.IPSettings(ip=vim.vm.customization.FixedIp(ipAddress=ipConf),subnetMask=netMask, gateway=gateWay)
	print '%s VirtualMachine Static IP Configuration successfully!' %(newvm)

else:
	# DHCP Configuration
	adaptermap.adapter = vim.vm.customization.IPSettings(ip=vim.vm.customization.DhcpIpGenerator(), dnsDomain='domain.local')
	print '%s VirtualMachine DHCP Configuration successfully!' %(newvm)


# IP
#globalip = vim.vm.customization.GlobalIPSettings()
# for static ip
#globalip = vim.vm.customization.GlobalIPSettings(dnsServerList=['10.0.1.4', '10.0.1.1'])
globalip = vim.vm.customization.GlobalIPSettings(dnsServerList=dnsDefault)

# Hostname settings
ident = vim.vm.customization.LinuxPrep(domain='domain.local', hostName=vim.vm.customization.FixedName(name=newvm))

# Putting all these pieces together in a custom spec
customspec = vim.vm.customization.Specification(nicSettingMap=[adaptermap], globalIPSettings=globalip, identity=ident)


# Creating relocate spec and clone spec
resource_pool = vmutils.get_resource_pool(si, 'DEV')
relocateSpec = vim.vm.RelocateSpec(pool=resource_pool)
#cloneSpec = vim.vm.CloneSpec(powerOn=True, template=False, location=relocateSpec, customization=customspec, config=vmconf)
cloneSpec = vim.vm.CloneSpec(powerOn=True, template=False, location=relocateSpec, customization=None, config=vmconf)

# Creating clone task
clone = template_vm.Clone(name=newvm, folder=template_vm.parent, spec=cloneSpec)

# close out connection
Disconnect(si)
