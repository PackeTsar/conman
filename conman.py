#!/usr/bin/python


#####            Conman Utility             #####
#####       Written by John W Kerns         #####
#####      http://blog.packetsar.com        #####
#####  https://github.com/packetsar/conman  #####

import os
import re
import sys
import time
import json
import inspect




try:
	import netmiko
	import paramiko
except:
	print("Netmiko/Paramiko import failed. Make sure to run the installer")


##### Inform version here #####
version = "v0.0.1"


class test_sock:
	def __init__(self, delineator):
		self.connected = True
		self.delineator = delineator
	def send(self, data):
		print("#"*50)
		print(data)
		print("#"*50)
		return self.multilineinput()
	def multilineinput(self):
		result = ""
		print("Enter each line of input End the input with '%s' on a line by itself" % self.delineator)
		for line in iter(raw_input, self.delineator):
			result += line+"\n"
		return result[0:len(result)-1]
	def send_command_timing(self, data):
		return self.send(data)
	def disconnect(self):
		self.connected = True


class cli:
	def __init__(self):
		global console
		console = self.console
	def write_log(self, data):
		print(data)
	def console(self, data):
		print(data)


##### Installer class: A simple holder class which contains all of the    #####
#####   installation scripts used to install/upgrade the ZTP server       #####
class installer:
	defaultconfig = '''{
    "credentials": {
        "ADMIN": {
            "password": "admin1234", 
            "username": "admin"
        }
    }, 
    "debugs": {
        "format": "timestamp (linenumber) [tracepath] {level}: data", 
        "modules": {
            "config_script": "1", 
            "operations_class": "1"
        }, 
        "timestamp": "year-month-dayThour-minute-secondZ", 
        "tracepath": "caller"
    }, 
    "defaults": {
        "credential": "ADMIN", 
        "device-type": "cisco_ios"
    }, 
    "device-groups": {}, 
    "devices": {}, 
    "private-keys": {}, 
    "scripts": {
        "CISCO": {
            "steps": {
                "1": {
                    "send": "show ver"
                }, 
                "1.1": {
                    "dump-input": null
                }
            }
        }, 
        "LINUX": {
            "steps": {
                "1": {
                    "send": "ps"
                }, 
                "1.1": {
                    "dump-input": null
                }
            }
        }
    }
}'''
	def minor_update_script(self):
		pass
	def copy_binary(self):
		binpath = "/bin/"
		binname = "conman"
		os.system('cp conman.py ' + binpath + binname)
		os.system('chmod 777 ' + binpath + binname)
		console("Binary file installed at " + binpath + binname)
	def create_configfile(self):
		config = json.loads(self.defaultconfig)
		rawconfig = json.dumps(config, indent=4, sort_keys=True)
		configfilepath = "/etc/conman/"
		configfilename = "conman.cfg"
		os.system('mkdir -p ' + configfilepath)
		f = open(configfilepath + configfilename, "w")
		f.write(rawconfig)
		f.close()
		console("Config File Created at " + configfilepath + configfilename)
	def install_dependencies(self):
		os.system("yum install epel-release -y")
		os.system("yum install python-pip -y")
		os.system("pip install netmiko")
	def install_completion(self):
		##### BASH SCRIPT DATA START #####
		bash_complete_script = """#!/bin/bash

#####      Conman BASH Complete Script      #####
#####        Written by John W Kerns        #####
#####       http://blog.packetsar.com       #####
#####  https://github.com/PackeTsar/conman  #####

_conman_complete()
{
  local cur prev
  COMPREPLY=()
  cur=${COMP_WORDS[COMP_CWORD]}
  prev=${COMP_WORDS[COMP_CWORD-1]}
  prev2=${COMP_WORDS[COMP_CWORD-2]}
  if [ $COMP_CWORD -eq 1 ]; then
    COMPREPLY=( $(compgen -W "clear set show run test" -- $cur) )
  elif [ $COMP_CWORD -eq 2 ]; then
    case "$prev" in
      "clear")
        COMPREPLY=( $(compgen -W "credential debug device device-group script private-key" -- $cur) )
        ;;
      "hidden")
        COMPREPLY=( $(compgen -W "show" -- $cur) )
        ;;
      "show")
        COMPREPLY=( $(compgen -W "config run" -- $cur) )
        ;;
      "set")
        COMPREPLY=( $(compgen -W "credential debug device device-group script default private-key" -- $cur) )
        ;;
      "run")
        COMPREPLY=( $(compgen -W "script" -- $cur) )
        ;;
      "test")
        COMPREPLY=( $(compgen -W "script" -- $cur) )
        ;;
      *)
        ;;
    esac
  elif [ $COMP_CWORD -eq 3 ]; then
    case "$prev" in
      config)
        if [ "$prev2" == "show" ]; then
          COMPREPLY=( $(compgen -W "raw -" -- $cur) )
        fi
        ;;
      run)
        if [ "$prev2" == "show" ]; then
          COMPREPLY=( $(compgen -W "raw -" -- $cur) )
        fi
        ;;
      default)
        if [ "$prev2" == "set" ]; then
          COMPREPLY=( $(compgen -W "credential device-type" -- $cur) )
        fi
        ;;
      private-key)
        local inserts=$(for k in `conman hidden show private-keys`; do echo $k ; done)
        if [ "$prev2" == "set" ]; then
          COMPREPLY=( $(compgen -W "${inserts} <private-key-name> -" -- $cur) )
        fi
        if [ "$prev2" == "clear" ]; then
          COMPREPLY=( $(compgen -W "${inserts}" -- $cur) )
        fi
        ;;
      credential)
        local inserts=$(for k in `conman hidden show credentials`; do echo $k ; done)
        if [ "$prev2" == "set" ]; then
          COMPREPLY=( $(compgen -W "${inserts} <credential-name> -" -- $cur) )
        fi
        if [ "$prev2" == "clear" ]; then
          COMPREPLY=( $(compgen -W "${inserts}" -- $cur) )
        fi
        ;;
      device)
        local inserts=$(for k in `conman hidden show devices`; do echo $k ; done)
        if [ "$prev2" == "set" ]; then
          COMPREPLY=( $(compgen -W "${inserts} <device-name> -" -- $cur) )
        fi
        if [ "$prev2" == "clear" ]; then
          COMPREPLY=( $(compgen -W "${inserts}" -- $cur) )
        fi
        ;;
      device-group)
        local inserts=$(for k in `conman hidden show device-groups`; do echo $k ; done)
        if [ "$prev2" == "set" ]; then
          COMPREPLY=( $(compgen -W "${inserts} <device-group-name> -" -- $cur) )
        fi
        if [ "$prev2" == "clear" ]; then
          COMPREPLY=( $(compgen -W "${inserts}" -- $cur) )
        fi
        ;;
      debug)
        if [ "$prev2" == "set" ]; then
          COMPREPLY=( $(compgen -W "module timestamp tracepath format" -- $cur) )
        fi
        if [ "$prev2" == "clear" ]; then
          COMPREPLY=( $(compgen -W "module" -- $cur) )
        fi
        ;;
      script)
        local inserts=$(for k in `conman hidden show scripts`; do echo $k ; done)
        if [ "$prev2" == "set" ]; then
          COMPREPLY=( $(compgen -W "${inserts} <script-name> -" -- $cur) )
        fi
        if [ "$prev2" == "clear" ]; then
          COMPREPLY=( $(compgen -W "${inserts}" -- $cur) )
        fi
        if [ "$prev2" == "run" ]; then
          COMPREPLY=( $(compgen -W "${inserts}" -- $cur) )
        fi
        if [ "$prev2" == "test" ]; then
          COMPREPLY=( $(compgen -W "${inserts}" -- $cur) )
        fi
        ;;
      show)
        if [ "$prev2" == "hidden" ]; then
          COMPREPLY=( $(compgen -W "credentials devices device-groups device-group-members scripts script-steps supported-devices possible-debugs current-debugs -" -- $cur) )
        fi
        ;;
      *)
        ;;
    esac
  elif [ $COMP_CWORD -eq 4 ]; then
    prev3=${COMP_WORDS[COMP_CWORD-3]}
    if [ "$prev2" == "credential" ]; then
      if [ "$prev3" == "set" ]; then
        COMPREPLY=( $(compgen -W "username" -- $cur) )
      fi
    fi
    if [ "$prev2" == "private-key" ]; then
      if [ "$prev3" == "set" ]; then
        COMPREPLY=( $(compgen -W "<delineator-char> -" -- $cur) )
      fi
    fi
    if [ "$prev2" == "device" ]; then
      if [ "$prev3" == "set" ]; then
        COMPREPLY=( $(compgen -W "host" -- $cur) )
      fi
    fi
    if [ "$prev2" == "device-group" ]; then
      if [ "$prev3" == "set" ]; then
        COMPREPLY=( $(compgen -W "member" -- $cur) )
      fi
      if [ "$prev3" == "clear" ]; then
        local inserts=$(for k in `conman hidden show device-group-members $prev`; do echo $k ; done)
        COMPREPLY=( $(compgen -W "${inserts} all" -- $cur) )
      fi
    fi
    if [ "$prev2" == "default" ]; then
      if [ "$prev3" == "set" ]; then
        if [ "$prev" == "credential" ]; then
          local inserts=$(for k in `conman hidden show credentials`; do echo $k ; done)
          COMPREPLY=( $(compgen -W "${inserts} <credential-name> -" -- $cur) )
        fi
        if [ "$prev" == "device-type" ]; then
          local inserts=$(for k in `conman hidden show supported-devices`; do echo $k ; done)
          COMPREPLY=( $(compgen -W "${inserts}  -" -- $cur) )
        fi
      fi
    fi
    if [ "$prev2" == "debug" ]; then
      if [ "$prev3" == "set" ]; then
        if [ "$prev" == "module" ]; then
          local inserts=$(for k in `conman hidden show possible-debugs`; do echo $k ; done)
          COMPREPLY=( $(compgen -W "${inserts}" -- $cur) )
        fi
        if [ "$prev" == "timestamp" ]; then
          COMPREPLY=( $(compgen -W "<timestamp-format> -" -- $cur) )
        fi
        if [ "$prev" == "tracepath" ]; then
          COMPREPLY=( $(compgen -W "full caller" -- $cur) )
        fi
        if [ "$prev" == "format" ]; then
          COMPREPLY=( $(compgen -W "<debugging-format> -" -- $cur) )
        fi
      fi
      if [ "$prev3" == "clear" ]; then
        if [ "$prev" == "module" ]; then
          local inserts=$(for k in `conman hidden show current-debugs`; do echo $k ; done)
          COMPREPLY=( $(compgen -W "${inserts}" -- $cur) )
        fi
      fi
    fi
    if [ "$prev2" == "script" ]; then
      if [ "$prev3" == "set" ]; then
        COMPREPLY=( $(compgen -W "step" -- $cur) )
      fi
      if [ "$prev3" == "clear" ]; then
        local inserts=$(for k in `conman hidden show script-steps $prev`; do echo $k ; done)
        COMPREPLY=( $(compgen -W "${inserts} all -" -- $cur) )
      fi
      if [ "$prev3" == "run" ]; then
        COMPREPLY=( $(compgen -W "device" -- $cur) )
      fi
      if [ "$prev3" == "test" ]; then
        COMPREPLY=( $(compgen -W "<delineator-char> -" -- $cur) )
      fi
    fi
    if [ "$prev2" == "show" ]; then
      if [ "$prev3" == "hidden" ]; then
        if [ "$prev" == "script-steps" ]; then
          local inserts=$(for k in `conman hidden show scripts`; do echo $k ; done)
          COMPREPLY=( $(compgen -W "${inserts}" -- $cur) )
        fi
        if [ "$prev" == "device-group-members" ]; then
          local inserts=$(for k in `conman hidden show device-groups`; do echo $k ; done)
          COMPREPLY=( $(compgen -W "${inserts}" -- $cur) )
        fi
      fi
    fi
  elif [ $COMP_CWORD -eq 5 ]; then
    prev3=${COMP_WORDS[COMP_CWORD-3]}
    prev4=${COMP_WORDS[COMP_CWORD-4]}
    if [ "$prev4" == "set" ]; then
      if [ "$prev3" == "debug" ]; then
        COMPREPLY=( $(compgen -W "level" -- $cur) )
      fi
    fi
    if [ "$prev4" == "set" ]; then
      if [ "$prev3" == "device" ]; then
        COMPREPLY=( $(compgen -W "<hostname-or-IP-address> -" -- $cur) )
      fi
    fi
    if [ "$prev4" == "set" ]; then
      if [ "$prev3" == "device-group" ]; then
        if [ "$prev" == "member" ]; then
          local inserts=$(for k in `conman hidden show devices`; do echo $k ; done)
          local inserts2=$(for k in `conman hidden show device-groups`; do echo $k ; done)
          COMPREPLY=( $(compgen -W "${inserts} ${inserts2} <device-name> -" -- $cur) )
        fi
      fi
    fi
    if [ "$prev4" == "set" ]; then
      if [ "$prev3" == "credential" ]; then
        COMPREPLY=( $(compgen -W "<ssh-login-user-name> -" -- $cur) )
      fi
    fi
    if [ "$prev4" == "set" ]; then
      if [ "$prev3" == "script" ]; then
        local inserts=$(for k in `conman hidden show script-steps $prev2`; do echo $k ; done)
        COMPREPLY=( $(compgen -W "${inserts} <step-id> -" -- $cur) )
      fi
    fi
    if [ "$prev4" == "run" ]; then
      if [ "$prev3" == "script" ]; then
        local inserts=$(for k in `conman hidden show devices`; do echo $k ; done)
        local inserts2=$(for k in `conman hidden show device-groups`; do echo $k ; done)
        COMPREPLY=( $(compgen -W "${inserts} ${inserts2} -" -- $cur) )
      fi
    fi
  elif [ $COMP_CWORD -eq 6 ]; then
    prev4=${COMP_WORDS[COMP_CWORD-4]}
    prev5=${COMP_WORDS[COMP_CWORD-5]}
    if [ "$prev5" == "set" ]; then
      if [ "$prev4" == "debug" ]; then
        COMPREPLY=( $(compgen -W "<debug-level> -" -- $cur) )
      fi
    fi
    if [ "$prev5" == "set" ]; then
      if [ "$prev4" == "device" ]; then
        COMPREPLY=( $(compgen -W "credential type port <enter>" -- $cur) )
      fi
    fi
    if [ "$prev5" == "set" ]; then
      if [ "$prev4" == "credential" ]; then
        COMPREPLY=( $(compgen -W "password private-key" -- $cur) )
      fi
    fi
    if [ "$prev5" == "set" ]; then
      if [ "$prev4" == "script" ]; then
        COMPREPLY=( $(compgen -W "send if-match for-match terminate run-script set-output dump-input" -- $cur) )
      fi
    fi
  elif [ $COMP_CWORD -eq 7 ]; then
    prev5=${COMP_WORDS[COMP_CWORD-5]}
    prev6=${COMP_WORDS[COMP_CWORD-6]}
    if [ "$prev6" == "set" ]; then
      if [ "$prev5" == "device" ]; then
        if [ "$prev" == "credential" ]; then
          local inserts=$(for k in `conman hidden show credentials`; do echo $k ; done)
          COMPREPLY=( $(compgen -W "${inserts} <credential-object-name> -" -- $cur) )
        fi
        if [ "$prev" == "type" ]; then
          local inserts=$(for k in `conman hidden show supported-devices`; do echo $k ; done)
          COMPREPLY=( $(compgen -W "${inserts} <device-type> -" -- $cur) )
        fi
        if [ "$prev" == "port" ]; then
          COMPREPLY=( $(compgen -W "<tcp-port-number> -" -- $cur) )
        fi
      fi
    fi
    if [ "$prev6" == "set" ]; then
      if [ "$prev5" == "credential" ]; then
        if [ "$prev" == "password" ]; then
          COMPREPLY=( $(compgen -W "<ssh-password> -" -- $cur) )
        fi
        if [ "$prev" == "private-key" ]; then
          local inserts=$(for k in `conman hidden show private-keys`; do echo $k ; done)
          COMPREPLY=( $(compgen -W "${inserts}" -- $cur) )
        fi
      fi
    fi
    if [ "$prev6" == "set" ]; then
      if [ "$prev5" == "script" ]; then
        if [ "$prev" == "send" ]; then
          COMPREPLY=( $(compgen -W "<string-to-send> -" -- $cur) )
        fi
        if [ "$prev" == "if-match" ]; then
          COMPREPLY=( $(compgen -W "<regex-pattern> -" -- $cur) )
        fi
        if [ "$prev" == "for-match" ]; then
          COMPREPLY=( $(compgen -W "<regex-pattern> -" -- $cur) )
        fi
        if [ "$prev" == "run-script" ]; then
          local inserts=$(for k in `conman hidden show scripts`; do echo $k ; done)
          COMPREPLY=( $(compgen -W "${inserts} <script-object-name> -" -- $cur) )
        fi
        if [ "$prev" == "set-output" ]; then
          COMPREPLY=( $(compgen -W "<string-to-set> -" -- $cur) )
        fi
      fi
    fi
  elif [ $COMP_CWORD -eq 8 ]; then
    prev2=${COMP_WORDS[COMP_CWORD-2]}
    prev6=${COMP_WORDS[COMP_CWORD-6]}
    prev7=${COMP_WORDS[COMP_CWORD-7]}
    if [ "$prev7" == "set" ]; then
      if [ "$prev6" == "script" ]; then
        if [ "$prev2" == "if-match" ]; then
          COMPREPLY=( $(compgen -W "partial complete -" -- $cur) )
        fi
      fi
      if [ "$prev6" == "device" ]; then
        if [ "$prev2" == "credential" ]; then
          COMPREPLY=( $(compgen -W "type port <enter>" -- $cur) )
        fi
        if [ "$prev2" == "type" ]; then
          COMPREPLY=( $(compgen -W "credential port <enter>" -- $cur) )
        fi
        if [ "$prev2" == "port" ]; then
          COMPREPLY=( $(compgen -W "credential type <enter>" -- $cur) )
        fi
      fi
    fi
  elif [ $COMP_CWORD -eq 9 ]; then
    prev2=${COMP_WORDS[COMP_CWORD-2]}
    prev7=${COMP_WORDS[COMP_CWORD-7]}
    prev8=${COMP_WORDS[COMP_CWORD-8]}
    if [ "$prev8" == "set" ]; then
      if [ "$prev7" == "device" ]; then
        if [ "$prev" == "credential" ]; then
          local inserts=$(for k in `conman hidden show credentials`; do echo $k ; done)
          COMPREPLY=( $(compgen -W "${inserts} <credential-object-name> -" -- $cur) )
        fi
        if [ "$prev" == "type" ]; then
          local inserts=$(for k in `conman hidden show supported-devices`; do echo $k ; done)
          COMPREPLY=( $(compgen -W "${inserts} <device-type> -" -- $cur) )
        fi
        if [ "$prev" == "port" ]; then
          COMPREPLY=( $(compgen -W "<tcp-port-number> -" -- $cur) )
        fi
      fi
    fi
  elif [ $COMP_CWORD -eq 10 ]; then
    prev2=${COMP_WORDS[COMP_CWORD-2]}
    prev4=${COMP_WORDS[COMP_CWORD-4]}
    prev8=${COMP_WORDS[COMP_CWORD-8]}
    prev9=${COMP_WORDS[COMP_CWORD-9]}
    if [ "$prev9" == "set" ]; then
      if [ "$prev8" == "device" ]; then
        if [ "$prev4" == "credential" ]; then
          if [ "$prev2" == "type" ]; then
            COMPREPLY=( $(compgen -W "port <enter>" -- $cur) )
          fi
          if [ "$prev2" == "port" ]; then
            COMPREPLY=( $(compgen -W "type <enter>" -- $cur) )
          fi
        fi
        if [ "$prev4" == "type" ]; then
          if [ "$prev2" == "port" ]; then
            COMPREPLY=( $(compgen -W "credential <enter>" -- $cur) )
          fi
          if [ "$prev2" == "credential" ]; then
            COMPREPLY=( $(compgen -W "port <enter>" -- $cur) )
          fi
        fi
        if [ "$prev4" == "port" ]; then
          if [ "$prev2" == "type" ]; then
            COMPREPLY=( $(compgen -W "credential <enter>" -- $cur) )
          fi
          if [ "$prev2" == "credential" ]; then
            COMPREPLY=( $(compgen -W "type <enter>" -- $cur) )
          fi
        fi
      fi
    fi
  elif [ $COMP_CWORD -eq 11 ]; then
    prev9=${COMP_WORDS[COMP_CWORD-9]}
    prev10=${COMP_WORDS[COMP_CWORD-10]}
    if [ "$prev10" == "set" ]; then
      if [ "$prev9" == "device" ]; then
        if [ "$prev" == "credential" ]; then
          local inserts=$(for k in `conman hidden show credentials`; do echo $k ; done)
          COMPREPLY=( $(compgen -W "${inserts} <credential-object-name> -" -- $cur) )
        fi
        if [ "$prev" == "type" ]; then
          local inserts=$(for k in `conman hidden show supported-devices`; do echo $k ; done)
          COMPREPLY=( $(compgen -W "${inserts} <device-type> -" -- $cur) )
        fi
        if [ "$prev" == "port" ]; then
          COMPREPLY=( $(compgen -W "<tcp-port-number> -" -- $cur) )
        fi
      fi
    fi
  fi
  return 0
} &&
complete -F _conman_complete conman &&
bind 'set show-all-if-ambiguous on'"""
		##### BASH SCRIPT DATA STOP #####
		##### Place script file #####
		installpath = '/etc/profile.d/conman-complete.sh'
		f = open(installpath, 'w')
		f.write(bash_complete_script)
		f.close()
		os.system('chmod 777 /etc/profile.d/conman-complete.sh')
		console("Auto-complete script installed to /etc/profile.d/conman-complete.sh")


class config_management:
	configfile = "conman.cfg"
	def __init__(self):
		self.configfile = self._get_config_file()
		self._publish()
		self._get_supported_devices()
	def _get_supported_devices(self):
		try:
			from netmiko.ssh_dispatcher import CLASS_MAPPER_BASE as supported_devices
		except:
			return None
		self.supported_devices = list(supported_devices)
		self.supported_devices.sort()
	def _get_config_file(self):
		configfilename = "conman.cfg"
		pathlist = ["/etc/conman", os.getcwd()]
		for path in pathlist:
			filepath = path + "/" + configfilename
			if os.path.isfile(filepath):
				return filepath
		f = open(configfilename, "w")  # If config file doesn exist, create it
		f.write("{}")
		f.close
		return configfilename
	def _publish(self):
		f = open(self.configfile, "r")
		self.rawconfig = f.read()
		f.close()
		self.running = json.loads(self.rawconfig)
	def save(self):
		self.rawconfig = json.dumps(self.running, indent=4, sort_keys=True)
		f = open(self.configfile, "w")
		self.rawconfig = f.write(self.rawconfig)
		f.close()
	def _check_step_number(self, stepnum):
		steplist = stepnum.split(".")
		for substep in steplist:
			try:
				int(substep)
			except ValueError:
				return False
		return True
	def _parse(self, args):
		name = args[0]
		result = {name: {}}
		del args[0]
		while len(args) >= 2:
			result[name].update({args[0]: args[1]})
			del args[:2]
		return result
	def show(self, args):
		function = args[2]
		if function == "config" or function == "run":
			self.show_config(args)
		else:
			print("Unknown Command!")
	def show_config(self, args):
		if len(args) > 3:
			if args[3].lower() == "raw":
				print(self.rawconfig)
				return None
		configtext = "########################\n!\n"
		####################
		debgtext = ""
		current = config_debug({"debugs": self.running["debugs"]})
		debgtext += current.set_cmd+"\n!\n"
		debgtext += "########################\n!\n"
		####################
		####################
		privatekeytext = ""
		for key in self.running["private-keys"]:
			current = config_private_key({key: self.running["private-keys"][key]})
			privatekeytext += current.set_cmd+"\n!\n"
		privatekeytext += "########################\n!\n"
		####################
		####################
		credentialtext = ""
		for credential in self.running["credentials"]:
			current = config_credential({credential: self.running["credentials"][credential]})
			credentialtext += current.set_cmd+"\n"
		credentialtext += "!\n########################\n!\n"
		####################
		devicetext = ""
		for device in self.running["devices"]:
			current = config_device({device: self.running["devices"][device]})
			devicetext += current.set_cmd+"\n"
		devicetext += "!\n!\n"
		#########
		for group in self.running["device-groups"]:
			current = config_device_group({group: self.running["device-groups"][group]})
			devicetext += current.set_cmd+"\n!\n"
		devicetext += "!\n########################\n!\n"
		####################
		scripttext = ""
		for script in self.running["scripts"]:
			current = config_script({script: self.running["scripts"][script]}, None)
			curscript = ""
			for cmd in current.set_cmd_list:
				curscript += " ".join(cmd)+"\n"
			scripttext += curscript+"!\n"
		scripttext += "########################\n!\n"
		####################
		defaulttext = ""
		current = config_default({"defaults": self.running["defaults"]})
		defaulttext += current.set_cmd+"\n"
		defaulttext += "!\n########################\n"
		####################
		configtext += debgtext
		configtext += privatekeytext
		configtext += credentialtext
		configtext += devicetext
		configtext += scripttext
		configtext += defaulttext
		print(configtext)
	def hidden(self, args):
		item = args[3]
		simple = ["credentials", "devices", "scripts", "private-keys", "device-groups"]
		if item in simple:
			self.hidden_show_simple(item)
		elif item == "possible-debugs":
			self.hidden_show_possible_debgs(args)
		elif item == "current-debugs":
			self.hidden_show_current_debgs(args)
		elif item == "script-steps":
			self.hidden_show_script_steps(args)
		elif item == "supported-devices":
			for each in self.supported_devices:
				print(each)
		elif item == "device-group-members":
			self.hidden_show_device_group_members(args)
	def hidden_show_simple(self, item):
		if item in list(self.running):
			for each in self.running[item]:
				print(each)
	def hidden_show_possible_debgs(self, args):
		print("all_modules")
		for mod in debug.get_mod_list():
			print(mod)
	def hidden_show_current_debgs(self, args):
		for mod in self.running["debugs"]["modules"]:
			print(mod)
	def hidden_show_script_steps(self, args):
		script = args[4]
		if "scripts" in list(self.running):
			if script in list(self.running["scripts"]):
				for step in self.running["scripts"][script]["steps"]:
					print(step)
	def hidden_show_device_group_members(self, args):
		group = args[4]
		if "device-groups" in list(self.running):
			if group in list(self.running["device-groups"]):
				for member in self.running["device-groups"][group]["members"]:
					print(member)
	def clear(self, args):
		function = args[2]
		simple = ["device", "credential", "private-key"]
		if function in simple:
			self.clear_simple(args)
		elif function == "script":
			self.clear_script(args)
		elif function == "device-group":
			self.clear_device_group(args)
		elif function == "debug":
			self.clear_debg(args)
		else:
			print("Unknown function!")
	def clear_simple(self, args):
		function = args[2]+"s"
		name = args[3]
		if function in list(self.running):
			if name in list(self.running[function]):
				del self.running[function][name]
				self.save()
			else:
				print("%s not in %s!" % (name, function))
		else:
			print("%s not in config!" % function)
	def clear_debg(self, args):
		module = args[4]
		if len(args) < 5:
			print("Incomplete command!")
			return None
		elif args[3] != "module":
			print("Cannot remove %s" % args[3])
			return None
		elif module not in self.running["debugs"]["modules"]:
			print("Module %s not set to debug!" % module)
			return None
		del self.running["debugs"]["modules"][module]
		self.save()
	def clear_script(self, args):
		if len(args) < 5:
			print("Incomplete command!")
			return None
		function = args[2]+"s"
		name = args[3]
		step = args[4]
		if function in list(self.running):
			if name in list(self.running[function]):
				if step == "all":
					del self.running[function][name]
					self.save()
				elif step in list(self.running[function][name]["steps"]):
					del self.running[function][name]["steps"][step]
					self.save()
				else:
					print("Step %s not in script %s!" % (step, name))
			else:
				print("%s not in %s!" % (name, function))
		else:
			print("%s not in config!" % function)
	def clear_device_group(self, args):
		if len(args) < 5:
			print("Incomplete command!")
			return None
		function = args[2]+"s"
		name = args[3]
		member = args[4]
		if function in list(self.running):
			if name in list(self.running[function]):
				if member == "all":
					del self.running[function][name]
					self.save()
				elif member in self.running[function][name]["members"]:
					index = 0
					for mem in self.running[function][name]["members"]:
						if mem == member:
							del self.running[function][name]["members"][index]
						index += 1
					self.save()
				else:
					print("member %s not in device-group %s!" % (member, name))
			else:
				print("%s not in %s!" % (name, function))
		else:
			print("%s not in config!" % function)
	def set(self, args):
		maps = {
		"device": config_device,
		"device-group": config_device_group,
		"credential": config_credential,
		"script": config_script,
		"default": config_default,
		"debug": config_debug,
		"private-key": config_private_key
		}
		function = args[2]
		if function in maps:
			if function+"s" not in list(self.running):
				self.running.update({function+"s": {}})
			newobj = maps[function](args)
			self.running[function+"s"].update(newobj.config)
			self.save()
		else:
			print("Unrecognized function (%s)" % function)


class config_common:
	class attrib:
		def __init__(self, data=""):
			self.data = data
		def __str__(self):
			return self.data
		def __repr__(self):
			return self.data
		def set(self, data):
			self.data = data
	def _commons(self):
		self.name = None
		self.set_cmd = None
		self.set_cmd_list = None
		self.config = None
		self.attrib_list = []
		self.attrib_dict = {}
		self._input_profile = {}
		self._attrib_order = None
		self._cmd_offset = 0
	def _obj_name_chk(self, objname):
		regex = "[A-Za-z0-9\_\-]+"
		search = re.findall(regex, objname)
		if len(search) != 1 or search[0] != objname:
			print("Bad Object Name: %s" % objname)
			return False
		else:
			return True
	def _input_check(self, inputdata, profile=None):
		result = True
		if not profile:
			profile = self._input_profile
		prolist = list(profile)
		prolist.sort()
		prolist.reverse()
		for check in prolist:
			try:
				if type(profile[check]) == type(""):
					if inputdata[check] != profile[check]:
						result = False
						print("Bad Argument: %s" % inputdata[check])
				elif type(profile[check]) == type([]):
					if inputdata[check] not in profile[check]:
						result = False
						print("Bad Argument: %s" % inputdata[check])
				elif type(profile[check]) == type(None):
					if len(inputdata) < check:
						result = False
						print("Incomplete Command!")
						break
				else:  # It is a check method
					if not profile[check](inputdata[check]):
						result = False
			except IndexError:
				pass
		return result
	def _sort_input(self, inputdata):
			if type(inputdata) == type([]):  # If input is a list
				# Then we are recieving a CLI command as args
				if self._input_check(inputdata):
					self._parse_command(inputdata)
				else:
					print("Quitting")
					quit()
			elif type(inputdata) == type({}):  # If input is a dict
				# Then we are recieving config from the configfile
				self._parse_config(inputdata)
			self._fill_in()
	def _parse_command(self, inputdata):
		self.name = inputdata[3+self._cmd_offset]
		self._get_attribs(inputdata[4+self._cmd_offset:], self._attribs)
	def _parse_config(self, inputdata):
		for name in inputdata:
			self.name = name
		self._get_attribs(inputdata[self.name], self._attribs)
	def attrib_dict_to_list(self):
		if not self._attrib_order:
			self._attrib_order = list(self.attrib_dict)
		for each in self._attrib_order:
			if each in self.attrib_dict:
				self.attrib_list.append(each)
				self.attrib_list.append(self.attrib_dict[each])
	def _fill_in(self):
		self.set_cmd_list = [
			'conman', 'set', self.function, self.name] + self.attrib_list
		self.set_cmd = " ".join(self.set_cmd_list)
		self.config = {self.name:{}}
		self.config[self.name].update(self.attrib_dict)
	def _get_attrib(self, attribs, attrib):
		if type(attribs) == type([]):
			index = 0
			while index+1 < len(attribs):
				if attribs[index] == attrib:
					if len(attribs) >= index+2:
						return {attribs[index]:attribs[index+1]}
						index += 1
				index += 1
		elif type(attribs) == type({}):
			for key in attribs:
				if key == attrib:
					return {key:attribs[key]}
	def _get_attribs(self, attribs, mapdict):
		for mapping in mapdict:
			if type(mapping) == type(()):  # If key is an "either/or" str tuple
				for each in mapping:
					attdict = self._get_attrib(attribs, each)
					if attdict:
						break
			else:  # If key is just a string
				attdict = self._get_attrib(attribs, mapping)
			if attdict:
				key = list(attdict)[0]
				value = attdict[key]
				if type(mapdict[mapping]) == type(()):  # If val is a tup
					mapdict[mapping][0].set(key)
					mapdict[mapping][1].set(value)
				else:  # If val is just a attrib object
					mapdict[mapping].set(value)
				self.attrib_dict.update({key:value})
		self.attrib_dict_to_list()



class config_default(config_common):
	def __init__(self, inputdata):
		self._commons()  # Build common vars
		############
		self._cmd_offset = -1
		self.function = "default"
		self.credential_name = self.attrib()
		self.device_type = self.attrib()
		self.credential = None
		self._input_profile = {
			3: ["credential", "device-type"],
			4: self._obj_name_chk}
		self._attribs = {
			"credential": self.credential_name,
			"device-type": self.device_type}
		############
		self._sort_input(inputdata)
		self.config = self.attrib_dict  # Override default named config
		self._populate()
	def _fill_in(self):
		self.set_cmd_list = [
			'conman', 'set', self.function, "credential", str(self.credential_name), "\n"
			'conman', 'set', self.function, "device-type", str(self.device_type)]
		self.set_cmd = " ".join(self.set_cmd_list)
		self.config = {self.name:{}}
		self.config[self.name].update(self.attrib_dict)
	def _populate(self):
		if str(self.credential_name) in list(config.running["credentials"]):
			self.credential = config_credential({str(self.credential_name): config.running["credentials"][str(self.credential_name)]})
			self.username = self.credential.username
			self.cred_method = self.credential.cred_method
			self.cred_value = self.credential.cred_value

#a = {"defaults": {"credential": "ADMIN", "device-type": "cisco-ios"}}
#c = config_default(a)


class config_debug(config_common):
	def __init__(self, inputdata):
		self._commons()  # Build common vars
		self._cmd_offset = -1
		############
		self.function = "debug"
		self.timestamp = self.attrib()
		self.tracepath = self.attrib()
		self.format = self.attrib()
		self._mod = self.attrib()
		self._lev = self.attrib()
		self.modules = {self._mod:self._lev}
		#############
		self._input_profile = {
			3: ["module", "timestamp", "tracepath", "format"],
			5: "level"}
		self._attribs = {
			"timestamp": self.timestamp,
			"tracepath": self.tracepath,
			"format": self.format,
			"module": self._mod,
			"level": self._lev}
		############
		self._sort_input(inputdata)
		#self.config = self.attrib_dict  # Override default named config
	def _parse_command(self, inputdata):
		self.name = inputdata[3+self._cmd_offset]
		self._get_attribs(inputdata[4+self._cmd_offset:], self._attribs)
		if "module" in self.attrib_dict:
			self._format_module()
		self.config = self.attrib_dict
	def _parse_config(self, inputdata):
		for name in inputdata:
			self.name = name
		self._get_attribs(inputdata[self.name], self._attribs)
		#self.attrib_dict["modules"] = inputdata[self.name]["modules"]
		self.modules = inputdata[self.name]["modules"]
		self.config = self.attrib_dict
		self.config.update({"modules": self.modules})
	def _fill_in(self):
		self.set_cmd_list = [
			["conman", "set", self.function, "timestamp", '"'+str(self.timestamp)+'"'],
			["conman", "set", self.function, "format", '"'+str(self.format)+'"'],
			["conman", "set", self.function, "tracepath", str(self.tracepath)],
		]
		for module in self.modules:
			temp = ["conman", "set", self.function, "module", str(module), "level", str(self.modules[module])]
			self.set_cmd_list.append(temp)
		self.set_cmd = ""
		for cmd in self.set_cmd_list:
			self.set_cmd += " ".join(cmd)+"\n"
		self.set_cmd = self.set_cmd[:len(self.set_cmd)-1]  # Rm last \n
	def _format_module(self):
		self.attrib_dict.update({"modules": config.running["debugs"]["modules"]})
		newmod = self.attrib_dict["module"]
		if "level" in self.attrib_dict:
			level = self.attrib_dict["level"]
			del self.attrib_dict["level"]
		else:
			level = "1"
		self.attrib_dict["modules"].update({newmod:level})
		del self.attrib_dict["module"]


class config_private_key(config_common):
	def __init__(self, inputdata):
		self._commons()  # Build common vars
		############
		self.function = "private-key"
		self.delineator = self.attrib()
		self.key = self.attrib()
		self._input_profile = {3: self._obj_name_chk}
		self._attribs = {
			"key": self.key,
			"delineator": self.delineator}
		############
		self._sort_input(inputdata)
		self.keyobj = paramiko.RSAKey.from_private_key(self) 
	def _parse_command(self, inputdata):
		self.name = inputdata[3]
		self.delineator = inputdata[4]
		self.key = self._multilineinput(self.delineator)
		self._create_attribs()
	def _parse_config(self, inputdata):
		for name in inputdata:
			self.name = name
		self.delineator = inputdata[self.name]["delineator"]
		self.key = inputdata[self.name]["key"]
		self._create_attribs()
	def _create_attribs(self):
		self.attrib_list = [self.delineator+"\n"+self.key+"\n"+self.delineator]
		self.attrib_dict = {"delineator": self.delineator, "key": self.key}
	def _multilineinput(self, ending):
		result = ""
		print("Enter each of the key. End the input with '%s' on a line by itself" % ending)
		for line in iter(raw_input, ending):
			result += line+"\n"
		return result[0:len(result)-1]
	def readlines(self):  # Used by Paramiko to read out key like a file
		return self.key.split("\n")


class config_credential(config_common):
	def __init__(self, inputdata):
		self._commons()  # Build common vars
		############
		self.function = "credential"
		self.username = self.attrib()
		self.cred_method = self.attrib()
		self.cred_value = self.attrib()
		self._input_profile = {
			3: self._obj_name_chk,
			4: "username",
			6: ["password", "private-key"],
			8: None}
		# self._attribs = {
		#	("either","or","in-order"): (key_here, val_here), 
		#	"simple": val_here}
		self._attribs = {
			"username": self.username,
			("password","private-key"): (self.cred_method, self.cred_value)}
		self._attrib_order = ["username", "password", "private-key"]
		############
		self._sort_input(inputdata)
	def connect_data(self):
		if str(self.cred_method) == "password":
			result = {
				"username": str(self.username),
				"password": str(self.cred_value)}
			return result
		elif str(self.cred_method) == "private-key":
			if str(self.cred_value) in config.running["private-keys"]:
				pkey = config_private_key({str(self.cred_value): config.running["private-keys"][str(self.cred_value)]})
				result = {
					"username": str(self.username),
					"use_keys": True,
					"key_file": pkey.keyobj
					}
				return result
		raise ValueError("Cannot make connect cred data!")

#a = ['conman', 'set', 'credential', 'SOMECRED', 'username', 'admin', 'password', 'admin123', "password", "other123", "private-key", "MY_KEY"]
#a = {'SOMECRED': {'username':'admin', 'password':'admin123', "private-key":"MYKEY"}}
#c = config_credential(a)
#print(c.name, "\n\n", c.username, "\n\n", c.cred_method, "\n\n", c.cred_value)
#print(c.set_cmd, "\n\n", c.set_cmd_list, "\n\n", c.config)
#print(c.attrib_list, "\n\n", c.attrib_dict)


class config_device(config_common):
	def __init__(self, inputdata):
		self._commons()  # Build common vars
		############
		self.function = "device"
		self.host = self.attrib()
		self.port = self.attrib()
		self.credentialname = self.attrib()
		self.credential = None
		self.type = self.attrib()
		self._input_profile = {
			3: self._obj_name_chk,
			4: "host",
			6: ["credential", "type", "port"]}
		self._attribs = {
			"credential": self.credentialname, "host": self.host, "type": self.type, "port":self.port}
		self._attrib_order = ["host", "port", "credential", "type"]
		############
		self._sort_input(inputdata)
		############
		self._check_attibs()
		self.next = self.__next__  # Python2 Compatibility
	def __iter__(self):
		self._iter_index = 0
		return self
	def __next__(self): # Python 3: def __next__(self)
		while self._iter_index == 0:
			self._iter_index += 1
			return self
		raise StopIteration
	def _check_attibs(self):
		if str(self.type) == "":
			self.type = config.running["defaults"]["device-type"]
		if str(self.port) == "":
			self.port = "22"
	def _get_credentials(self):
		current = str(self.credentialname)
		if str(current) == "":  # Blank, so use default creds
			if config.running["defaults"]["credential"] in config.running["credentials"]:  # If default cred exists in config
				name = config.running["defaults"]["credential"]
				self.credential = config_credential({name: config.running["credentials"][name]})
			else:
				raise ValueError("Credentials not found!")
		elif current in config.running["credentials"]:
			self.credential = config_credential({current: config.running["credentials"][current]})
		else:
			raise ValueError("Cannot instantiate credentials!")
	def _make_login(self):
		self._get_credentials()
		result = {
			"device_type": str(self.type),
			"host": str(self.host),
			"port": int(str(self.port))}
		result.update(self.credential.connect_data())
		return result
	def make_sock(self):
		return netmiko.ConnectHandler(**self._make_login())

#a = ['conman', 'set', 'device', 'SOMEDEVICE', 'host', '10.0.0.1', 'asdf', 'credential', 'MY_CREDS', "otheratt", "otherval", "othersomething2"]
#a = {'SOMEDEVICE': {'credential': 'MY_CREDS', 'host': '10.0.0.1'}}
#c = config_device(a)
#print(c.name, "\n\n", c.host, "\n\n", c.credential)
#print(c.set_cmd, "\n\n", c.set_cmd_list, "\n\n", c.config)
#print(c.attrib_list, "\n\n", c.attrib_dict)


class config_device_group(config_common):
	def __init__(self, inputdata):
		self._commons()  # Build common vars
		############
		self.function = "device-group"
		self.memberlist = []
		self.currentmember = None
		self._input_profile = {
			3: self._obj_name_chk,
			4: "member",
			6: self._obj_name_chk}
		#self._attribs = {
		#	"member": self.currentmember}
		#self._attrib_order = ["member"]
		############
		self._sort_input(inputdata)
		self.next = self.__next__  # Python2 Compatibility
	def __iter__(self):
		self._iter_index = 0
		return self
	def __next__(self): # Python 3: def __next__(self)
		while self._iter_index != len(self.memberlist):
			result = self._get_device(self.memberlist[self._iter_index])
			self._iter_index += 1
			if result:
				return result
		raise StopIteration
	def _parse_command(self, inputdata):
		name = inputdata[3]
		self.currentmember = inputdata[5]
		if name not in config.running["device-groups"]:
			self._parse_config({name: {"members": [str(self.currentmember)]}})
		else:
			self._parse_config({name: config.running["device-groups"][name]})
			if str(self.currentmember) not in self.config[name]["members"]:
				self.config[name]["members"].append(str(self.currentmember))
	def _parse_config(self, inputdata):
		for name in inputdata:
			self.name = name
		self.config = inputdata
		for member in self.config[self.name]["members"]:
			self.memberlist.append(member)
	def _fill_in(self):
		self.set_cmd_list = []
		for member in self.memberlist:
			temp = ["conman", "set", "device-group", self.name, "member", member]
			self.set_cmd_list.append(temp)
		self.set_cmd = ""
		for cmd in self.set_cmd_list:
			self.set_cmd += " ".join(cmd)+"\n"
		self.set_cmd = self.set_cmd[:len(self.set_cmd)-1]  # Rm last \n
	def _get_next_device(self):
		while self._iter_index != len(self.memberlist)-1:
			result = self._get_device(self.memberlist[self._iter_index])
			self._iter_index += 1
			if result:
				return result
		return None
	def _get_device(self, devicename):
		if devicename in list(config.running["devices"]):
			return config_device({devicename: config.running["devices"][devicename]})
		elif devicename in list(config.running["device-groups"]):
			return config_device_group({devicename: config.running["device-groups"][devicename]})
		else:
			print("Device (%s) doesn't exist!" % devicename)
			return None


# Class for interpreting and executing configured scripts
class config_script(config_common):
	def __init__(self, inputdata, sock=None, globalinput=None):
		self._commons()  # Build common vars
		############
		self.function = "script"
		self.sock = sock  # Save the socket as a local variable
		self.globalinput = globalinput  # Used when scripts call each other
		self.lastoutput = None  # Used when scripts call each other
		self.terminate = False
		self._sort_input(inputdata)
	class steps_class:
		# steps_class: Class (and subclass) to handle step numbers, passing inputs
		#	between steps, listing step offspring (config and items), and
		#	nullifying offspring steps when a parent fails
		def __init__(self, stepdict, globalinput):
			self.globalinput = globalinput
			self._list = self._order_steps(stepdict)
			self.tree = self._build_tree(self._list)
			self._treestr = json.dumps(self._convert_to_str(self.tree), 
				indent=4, sort_keys=True)
			self._liststr = self._convert_to_str(self._list)
			self.set_global_input()
			self._iterindex = 0
			self.next = self.__next__  # Python2 Compatibility
		def __iter__(self):
			self._iterindex = 0
			return self
		def __next__(self): # Python 3: def __next__(self)
			if self._iterindex == len(self._list):
				raise StopIteration
			else:
				self._iterindex += 1
				return self._list[self._iterindex-1]
		def get_offspring(self, step=None):  # Get list of all offspring steps
			result = []
			if not step:
				step = self._list[self._iterindex-1]
			for each in self._get_stepset_list(step)[1:]:
				result.append(each)
			return result
		def get_offspring_config(self, step=None):  # Get all offspring config
			result = {}
			for each in self.get_offspring(step):
				result.update(each.config)
			return result
		def nullify(self, currentstep=None):  # Nullify current and child steps
			if not currentstep:
				currentstep = self._list[self._iterindex-1]
			for each in self._get_stepset_list(currentstep):
				each.valid = False
		def skipify(self, currentstep=None):  # Nullify current and child steps
			if not currentstep:
				currentstep = self._list[self._iterindex-1]
			for each in self._get_stepset_list(currentstep):
				each.skip = True
		def store_output(self, inputdata, step=None):  # Set input on child (only) steps
			if not step:
				step = self._list[self._iterindex-1]
			parent = self._get_stepset_dict(step)
			children = parent[list(parent)[0]]
			if children != None:
				for each in children:  # Each direct child
					each.input = inputdata
		def set_global_input(self):
			for step in list(self.tree):  # For each root step
				step.input = self.globalinput
		class step_class:
			def __init__(self, args):
				self.origstr = args["string"]
				self.instructions = args["instructions"]
				self.config = args["config"]
				self.intlist = self._make_int_list()
				self.str = self._create_string()
				self.depth = len(self.intlist)
				self.input = None
				self.valid = True
				self.skip = False
				self.cmd_list = self._subcommand()
			def level(self, level):
				try:
					return (self.intlist[level], "continue")
				except IndexError:
					return (0, "end")
			def _make_int_list(self):
				result = []
				stringlist = self.origstr.split(".")
				for each in stringlist:
					result.append(int(each))
				return result
			def _create_string(self):
				templist = []
				for num in self.intlist:
					templist.append(str(num))
				return ".".join(templist)
			def _subcommand(self):
				inst = self.config[self.str]
				action = list(inst)[0]
				result = ["step", self.str, action]
				if inst[action] == None:  # If a simple action (ie: terminate)
					pass  # No need to append any commands
				elif type(inst[action]) == type(u""):  # If a string
					result.append('"%s"' % inst[action])  # Append one last cmd
				else:  # If a complex action with parameters
					if action == "if-match":
						result.append('"%s"' % inst[action]["regex"])
						result.append(inst[action]["criterion"])
					elif action == "for-match":
						result.append('"%s"' % inst[action]["regex"])
				return result
			######## END OF STEP_CLASS  ########
		def _bigger(self, a, b, l=0):
			asub = a.level(l)
			bsub = b.level(l)
			if asub[1] == "end" and bsub[1] == "end":
				print(l)
				raise ValueError("Steps are the same (%s) (%s)" % (a.origstr, b.origstr))
			else:
				if asub[0] == bsub[0]:  # If they are the same
					return self._bigger(a, b, l+1)  # Move down a level and recurse
				elif asub[0] > bsub[0]:
					return True
				elif asub[0] < bsub[0]:
					return False
		def _order_steps(self, stepdict):
			steplist = list(stepdict)
			firstargs = {
					"string": steplist[0],
					"instructions": stepdict[steplist[0]],
					"config": {
						steplist[0]: stepdict[steplist[0]]
					}
				}
			result = [self.step_class(firstargs)]
			for each in steplist[1:]:
				numargs = {
						"string": each,
						"instructions": stepdict[each],
						"config": {
							each: stepdict[each]
						}
					}
				num = self.step_class(numargs)
				index = 0
				for r in result:
					if index == len(result):
						result.append(num)
					elif self._bigger(num, r):
						if index == len(result)-1:
							result.insert(index+1, num)
							break
					elif self._bigger(r, num):
						result.insert(index, num)
						break
					index += 1
			return result
		def _convert_to_str(self, stepdict):
			if type(stepdict) == type([]):
				templist = []
				for step in stepdict:
					templist.append(step.str)
				return templist
			else:
				tempdict = {}
				for each in stepdict:
					if stepdict[each] == None:
						tempdict.update({each.str: None})
					else:
						tempdict.update({each.str: self._convert_to_str(stepdict[each])})
				return tempdict
		def _build_tree(self, datalist):
			def _is_child(parent, child):
				index = 0
				for level in parent.intlist:
					if level != child.intlist[index]:
						return False
					index += 1
				return True
			def _place_child(parentdict, child):
				for key in parentdict:
					if _is_child(key, child):
						if parentdict[key] == None:
							parentdict[key] = {child:None}
						else:
							_place_child(parentdict[key], child)
						return None
				parentdict.update({child:None})
			result = {}
			for step in datalist:
				_place_child(result, step)
			return result
		def _find_step_tree(self, step, root=False, index=0):
			if root == False:
				return self._find_step_tree(step, self.tree)
			elif root != None:
				for branch in root:
					if branch == None:
						pass
					elif branch == step:
						return {branch: root[branch]}
					else:
						srch = self._find_step_tree(step, root[branch], index=index+1)
						if srch:
							return srch
		def _get_stepset_list(self, step=None):  # List step and (grand) children
			if not step:
				step = self._list[self._iterindex-1]
			currentstepset = self._find_step_tree(step)
			return self._iter_steps(currentstepset, [])
		def _get_stepset_dict(self, step=None):  # Get dict step and (grand) chldrn
			result = []
			if not step:
				step = self._list[self._iterindex-1]
			return self._find_step_tree(step)
		def _iter_steps(self, stepdict, result=[]):
			if stepdict != None:
				for step in stepdict:
					result.append(step)
					if stepdict[step] != None:
						self._iter_steps(stepdict[step], result)
			return result
		######## END OF STEPS_CLASS  ########
	######## Script config handling methods ########
	def _parse_config(self, inputdata):
		for name in inputdata:
			self.name = name
		self.config = inputdata
	def _parse_command(self, inputdata):
		name = inputdata[3]
		newstep = self._interpret_cmd(inputdata)
		if name not in config.running["scripts"]:
			self._parse_config({name: {"steps": newstep}})
		else:
			self._parse_config({name: config.running["scripts"][name]})
			self.config[self.name]["steps"].update(newstep)
	def _fill_in(self):
		self.steps = self.steps_class(self.config[self.name]["steps"], self.globalinput)  # Instantiate steps
		self.set_cmd_list = self._make_cmds()
	def _make_cmds(self):
		result = []
		for step in self.steps._list:
			stepcmdlist = ["conman", "set", "script", self.name]
			stepcmdlist += step.cmd_list
			result.append(stepcmdlist)
		return result
	def _interpret_cmd(self, inputdata):
		def _length_check(args, length):
			if len(args) < length:
				print("Command Incomplete!")
				quit()
			else:
				return True
		def _no_args(inputdata):
			return {inputdata[5]: {inputdata[6]: None}}
		def _simple(inputdata):
			if _length_check(inputdata, 8):
				return {inputdata[5]: {inputdata[6]: inputdata[7]}}
		def _for_match(inputdata):
			if _length_check(inputdata, 8):
				return {inputdata[5]: {inputdata[6]: {"regex": inputdata[7]}}}
		def _if_match(inputdata):
			if _length_check(inputdata, 9):
				return {inputdata[5]: {inputdata[6]: {
					"regex": inputdata[7],
					"criterion": inputdata[8]}}}
		if _length_check(inputdata, 7):
			action = inputdata[6]
			maps = {
				"dump-input": _no_args,
				"terminate": _no_args,
				"run-script": _simple,
				"send": _simple,
				"set-output": _simple,
				"for-match": _for_match,
				"if-match": _if_match,
			}
			if action in maps:
				return maps[action](inputdata)
			else:
				print("Unknown action (%s)!" % action)
	######## Script execution methods ########
	def __output(self, outputdata, step):
		debug("(%s): Passing output to children steps" % step.str)
		self.steps.store_output(outputdata)  # Write to child steps
		self.lastoutput = outputdata  # Write to last output store
	def _send(self, step):
		command = step.instructions["send"]
		debug("(%s): Sending (%s)" % (step.str, command))
		output = self.sock.send_command_timing(command)
		self.__output(output, step)
	def _terminate(self, step):
		debug("(%s): Setting terminate flag and killing socket" % step.str)
		self.sock.disconnect()  # Kill socket
		self.__output(step.input, step)  # Pass on inputdata
		self.terminate = True  # Set termination flag
	def _dump_input(self, step):
		# No required args here
		debug("(%s): Dumping input" % step.str)
		console("#"*25 + " DUMPING INPUT " + "#"*25)
		console(step.input)
		console("#"*65)
		self.__output(step.input, step)  # Pass to children
	def _if_match(self, step):
		debug("(%s): Checking if-match" % step.str)
		regex = step.instructions["if-match"]["regex"]
		debug("(%s): Regex set to (%s)" % (step.str, regex))
		criterion = step.instructions["if-match"]["criterion"]
		debug("(%s): Criterion set to (%s)" % (step.str, criterion))
		search = search_class(regex, step.input)
		debug("(%s): Regex match returned: %s" % (step.str, search.matchlist))
		if (criterion == "partial" and search.partial
			) or (criterion == "complete" and search.complete):
			debug("(%s): Match confirmed" % step.str)
			self.__output(step.input, step)  # Pass to children
		else:
			debug("(%s): No pattern matched. Nullifying offspring" % step.str)
			self.steps.nullify()  # Invalidate all offspring
	def _for_match(self, step):
		debug("(%s): Checking for-match" % step.str)
		regex = step.instructions["for-match"]["regex"]
		debug("(%s): Regex set to (%s)" % (step.str, regex))
		search = search_class(regex, step.input)
		debug("(%s): Regex match returned: %s" % (step.str, search.matchlist))
		childinst = self.steps.get_offspring_config()
		debug("(%s): Pulled offspring step instructions: %s" % (step.str, childinst))
		debug("(%s): Beginning a loop on each match result" % step.str)
		for match in search.matchlist:
			debug("(%s): Looping on match (%s)" % (step.str, match))
			newscript = config_script({step.str: {"steps": childinst}}, self.sock, globalinput=match)
			debug("(%s): Spawn script instantiated. Running..." % step.str)
			newscript.run()
		debug("(%s): For-match loop complete. Setting offspring to skip" % step.str)
		self.steps.skipify() # Skip offspring to prevent linear run
	def _run_script(self, step):
		script = step.instructions["run-script"]
		if script in config.running["scripts"]:
			newscript = config_script({script: config.running["scripts"][script]}, self.sock, globalinput=step.input)
			output = newscript.run()
			self.__output(output, step)
		else:
			debug("Script %s not found. Skipping" % script)
			self.steps.nullify()
	def run(self):
		debug("Beginning script run")
		lastoutput = None
		debug("Script global input (lastoutput) is set to (%s)" % lastoutput)
		funcmap = {  # Map config function names to actual methods
			"send": self._send,
			"dump-input": self._dump_input,
			"if-match": self._if_match,
			"terminate": self._terminate,
			"for-match": self._for_match,
			"run-script": self._run_script
		}
		for step in self.steps:  # Iter through step objects in order
			if not step.skip:
				if not self.terminate:
					#####
					debug("(%s): Beginning step execution" % step.str)
					inputdata = step.input  # Pull output from last loop
					function = list(step.instructions)[0]  # Set function name
					debug("(%s): Step instructions: %s" % (step.str, step.instructions))
					#####
					if not step.valid:  # If it has been marked invalid
						pass
						debug("(%s): Step has been invalidated. Skipping" 
							% step.str)
					else:
						debug("(%s): Step is valid. Continuing" % step.str)
						funcmap[function](step)  # Execute step with method
					debug("(%s): Step complete \n\n\n" % step.str)
				else:
					debug("(%s): Terminate flag set. Terminating script" % step.str)
					return self.lastoutput
		return self.lastoutput  # Return the socket after complete

#c = {'SHORT': {u'steps': {u'1': {u'send': u'show ver'}, u'1.1': {u'dump-input': None}}}}
#
#a = config_script(b, None)
#b = ['conman', 'set', 'script', 'SHORT', 'step', '1', u'send', u'"show ver"']


class debugging:
	def __init__(self):
		self.mod_exclude_list = [
			'__builtins__', '__doc__', '__file__', '__name__', 
			'__package__', '_new_connect_params_dict', 
			'cat_list', 'config', 'inspect', 
			'installer', 'json', 'netmiko', 
			'os', 'paramiko', 're', 'sys', 'version', "debugging", "debug"]
		self.defaultconfig = {
			"debugs": {
				"format": "timestamp (linenumber) [tracepath] {level}: data",
				"modules": {},
				"timestamp": "year-month-dayThour-minute-secondZ",
				"tracepath": "caller"}}
		if "debugs" in config.running:
			self.config = config_debug({"debugs": config.running["debugs"]})
		else:
			self.config = config_debug(self.defaultconfig)
		self.enabled = True
	def __call__(self, data, level=1):
		if self.enabled:
			insp = self.inspection()
			if self._to_output(insp, level):
				print(self._build_outpt(insp, data, level))	
	class inspection:
		def __init__(self):
			self.stack = self._clean_stack()
			self.caller = self._build_caller()
			self.pathstring = self._build_pathstring()
			self.path = self._build_path()
		def _clean_stack(self):
			stack = inspect.stack()
			self.callingline = stack[3][2]
			stack.reverse()
			start = 0
			for frame in stack:
				if frame[3] == "interpreter":
					break
				start += 1
			return stack[start:len(stack)-3]
		def _get_class(self, frame):
			try:
				name = frame[0].f_locals["self"].__class__.__name__
				return name
			except:
				return None
		def _build_pathstring(self):
			result = ""
			current_class = None
			lastline = ""
			for frame in self.stack:
				parent = self._get_class(frame)
				method = frame[3]
				interclass = "--%s-->" % lastline
				intraclass = "-%s->" % lastline
				if parent:
					if parent != current_class:
						current_class = parent
						result += interclass+parent+"."+method
					else:
						result += intraclass+method
				else:
					result += interclass+method
				lastline = frame[2]
			return result[5:]
		def _build_caller(self):
			result = ""
			frame = self.stack[len(self.stack)-1]
			parent = self._get_class(frame)
			if parent:
				self.parent = parent
				result += parent+"."
			else:
				self.parent = frame[3]
			result += frame[3]
			return result
		def _build_path(self):
			if str(debug.config.tracepath) == "full":
				return self.pathstring
			elif str(debug.config.tracepath) == "caller":
				return self.caller
	def get_mod_list(self):
		result = []
		for mod in globals():
			if mod not in self.mod_exclude_list:
				result.append(mod)
		return result
	def _to_output(self, insp, level):
		if insp.parent in self.config.modules:
			if level <= int(self.config.modules[insp.parent]):
				return True
		elif "all_modules" in self.config.modules:
			if level <= int(self.config.modules["all_modules"]):
				return True
	def _tmstmp(self):
		mappings = {
			"year": "%Y",
			"month": "%m",
			"day": "%d",
			"hour": "%H",
			"minute": "%M",
			"second": "%S",
		}
		tformat = str(self.config.timestamp)
		for fmt in mappings:
			if fmt in tformat:
				tformat = tformat.replace(fmt, mappings[fmt])
		return time.strftime(tformat)
	def _build_outpt(self, insp, data, level):
		result = str(self.config.format)
		result = result.replace("level", str(level))
		result = result.replace("timestamp", self._tmstmp())
		result = result.replace("linenumber", str(insp.callingline))
		result = result.replace("tracepath", insp.path)
		result = result.replace("data", data)
		return result


class search_class:
	def __init__(self, regexdata, inputdata):
		self.regexdata = regexdata
		self.inputdata = inputdata
		self.matchlist = []
		self._search()
		self._search_partial()
		self._search_complete()
	def _search(self):
		if not self.inputdata:
			return None
		elif len(self.inputdata) == 0:
			return None
		else:
			self.matchlist = re.findall(self.regexdata, self.inputdata, re.MULTILINE)
	def _search_partial(self):
		if len(self.matchlist) > 0:
			self.partial = True
		else:
			self.partial = False
	def _search_complete(self):
		self.complete = False
		for match in self.matchlist:
			if match == self.inputdata:
				self.complete = True
				break

# s = search_class("[0-9]+", "cisco WS-C3750-48P (PowerPC405) processor")
# s.partial
# s.complete
# s.matchlist


class operations_class:  # Container class
	def test(self, args):
		if args[2] == "script":
			scriptname = args[3]
			delineator = args[4]
			self.test_script(scriptname, delineator)
	def run(self, args):
		debug("Starting a script run")
		if args[2] == "script":
			scriptname = args[3]
			devicename = args[5]
			debug("Running script (%s) against (%s)" % (scriptname, devicename))
			self.run_script(scriptname, devicename)
	def test_script(self, scriptname, delineator):
		debug("Starting a script test")
		if scriptname not in list(config.running["scripts"]):
			print("Script (%s) not in configuration" % scriptname)
			return None
		sock = test_sock(delineator)
		script = config_script({scriptname: config.running["scripts"][scriptname]}, sock)
		script.run()
	def _script_exists(self, scriptname):
		debug("Checking if script (%s) exists" % scriptname)
		if scriptname not in list(config.running["scripts"]):
			print("Script (%s) not in configuration" % scriptname)
			return False
		else:
			debug("Script (%s) does exist" % scriptname)
			return True
	def _get_device(self, devicename):
		debug("Checking if device (%s) exists" % devicename)
		if devicename in list(config.running["devices"]):
			debug("Device (%s) does exists as a device" % devicename)
			return config_device({devicename: config.running["devices"][devicename]})
		elif devicename in list(config.running["device-groups"]):
			debug("Device (%s) does exists as a device-group" % devicename)
			return config_device_group({devicename: config.running["device-groups"][devicename]})
		else:
			print("Device (%s) not in configuration" % devicename)
			return None
	def run_script(self, scriptname, devicename):
		debug("Beginning script pre-execution checks")
		if self._script_exists(scriptname):
			debug("Trying to instantiate device (%s) config" % devicename)
			devices = self._get_device(devicename)
			if devices:
				debug("Device (%s) config instantiation successful" % devicename)
				for device in devices:
					if device.function == "device-group":
						debug("Device (%s) is a device-group. Recursing to get actual device" % devicename)
						self.run_script(scriptname, device.name)
					else:
						debug("Device (%s) is not a device-group. Attempting to connect..." % devicename)
						sock = device.make_sock()
						debug("Connection to device (%s) successful! Instantiating the script (%s)" % (devicename, scriptname))
						script = config_script({scriptname:
							config.running["scripts"][scriptname]}, sock)
						debug("Script (%s) instantiation with device (%s) successful. Kicking off script execution" % (scriptname, devicename))
						script.run()


def _new_connect_params_dict(self):
	"""Generate dictionary of Paramiko connection parameters."""
	conn_dict = {
		'hostname': self.host,
		'port': self.port,
		'username': self.username,
		'password': self.password,
		'look_for_keys': self.use_keys,
		'allow_agent': self.allow_agent,
		'pkey': self.key_file,  ### Modified to pass pkey instead
		'timeout': self.timeout,
	}
	# Check if using SSH 'config' file mainly for SSH proxy support
	if self.ssh_config_file:
		conn_dict = self._use_ssh_config(conn_dict)
	return conn_dict

# Overwrite the netmiko method here
try:
	netmiko.base_connection.BaseConnection._connect_params_dict = _new_connect_params_dict
except:
	pass


##### Concatenate a list of words into a space-seperated string           #####
def cat_list(listname):
	result = ""
	counter = 0
	for word in listname:
		result = result + listname[counter].lower() + " "
		counter = counter + 1
	result = result[:len(result) - 1:]
	return result


##### Main CLI interpreter and helper function. Entry point for the app.  #####
def interpreter():
	arguments = cat_list(sys.argv[1:])
	global config
	config = config_management()
	global debug
	debug = debugging()
	if arguments[:6] == "hidden":
		debug.enabled = False
	debug("config and debugging instantiated", 3)
	operations = operations_class()
	if arguments == "next":
		print("""
	LOGGING/DEBUGGING:
		- Fix up config printing when empty parts
		- Add debug probes. Set proper levels
		- Build in logging
		- Clean up text output handling (remove all prints)
	CLEANUP/FIXES
		- Offload completion to native python
	TESTING
		- Create working recursive script
	NEW FEATURES
		- Add munge function (or string processing in scripts)
		- More script functions: elif-match, else, set-variable, enter-config, exit-config
		- Build: credential-groups
		- Apply scripts as login scripts
		- Add "connect" to get an interactive shell
			- Use native SSH client? Cannot do scripted logins?
			- Cannot find way to do interactive shell
	MAKING STRING PROCESSING ITS OWN ITEM (munge vs script)
		Pros:
			more modularity, easier to build and test
			Can be reused by multiple scripts or multiple times in the same script
			Can be integrated into more places

		Cons:
			Harder to understand how it works
			Confusing how rule numbering will work
			Could build string processing into scripts and just use run-script function for reuse
			Could reuse 
		""")
	##### HIDDEN #####
	elif arguments[:6] == "hidden" and len(sys.argv) > 3:
		config.hidden(sys.argv)
	##### INSTALL/UPGRADE #####
	elif arguments == "install":
		console("***** Are you sure you want to install ConMan using version %s?*****" % version)
		answer = raw_input(">>>>> If you are sure you want to do this, type in 'CONFIRM' and hit ENTER >>>>")
		if answer.lower() == "confirm":
			inst = installer()
			inst.copy_binary()
			inst.create_configfile()
			inst.install_completion()
			inst.install_dependencies()
			inst.minor_update_script()
			console("\nInstall complete! Logout and log back into SSH to activate auto-complete")
		else:
			console("Install cancelled")
	elif arguments == "upgrade":
		console("***** Are you sure you want to upgrade ConMan using version %s?*****" % version)
		answer = raw_input(">>>>> If you are sure you want to do this, type in 'CONFIRM' and hit ENTER >>>>")
		if answer.lower() == "confirm":
			inst = installer()
			inst.copy_binary()
			#inst.create_configfile()
			inst.install_completion()
			#inst.install_dependencies()
			inst.minor_update_script()
			console("Upgrade complete! Logout and log back into SSH to activate auto-complete")
		else:
			console("Upgrade cancelled")
	##### SHOW #####
	elif arguments == "show":
		console(" - show (config|run) [raw]                                     |  Show the current conman configuration")
	elif arguments[:4] == "show" and len(sys.argv) >= 3:
		config.show(sys.argv)
	##### SET #####
	elif arguments == "set":
		console(" - set debug (module|timestamp|tracepath|format) [options]     |  Set the debugging output options")
		console(" - set private-key <name> <delineator_char>                    |  Create/modify a RSA private-key to use for SSH authentication")
		console(" - set credential <name> username <name> [options]             |  Create/modify a credential set to use to log into devices")
		console(" - set device <name> host <ip/hostname> [options]              |  Create/modify a target device for connections")
		console(" - set device-group <name> member <device-name>                |  Create/Modify a device group by adding a member device")
		console(" - set script <name> step <step-id> <function> [options]       |  Create/modify a script to run against devices")
		console(" - set default credential <cred-obj-name>                      |  Set the default credential to use")
		console(" - set default device-type <device-type>                       |  Set the default device type to use on configured devices")
	elif (arguments[:9] == "set debug" and len(sys.argv) < 5):
		console(" - set debug (module|timestamp|tracepath|format) [options]     |  Set the debugging output options")
	elif (arguments[:15] == "set private-key" and len(sys.argv) < 5):
		console(" - set private-key <name> <delineator_char>                    |  Create/modify a RSA private-key to use for SSH authentication")
	elif (arguments[:14] == "set credential" and len(sys.argv) < 8) or arguments == "set credential":
		console(" - set credential <name> username <name> (password|private-key) <value>")
	elif arguments[:16] == "set device-group" and len(sys.argv) < 6:
		console(" - set device-group <name> member <device-name>                |  Create/Modify a device group by adding a member device")
	elif (arguments[:10] == "set device" and len(sys.argv) < 6) or arguments == "set device":
		console(" - set device <name> host <ip/hostname> [options]              |  Create/modify a target device for connections")
		console(" - set device-group <name> member <device-name>                |  Create/Modify a device group by adding a member device")
	elif (arguments[:10] == "set script" and len(sys.argv) < 7) or arguments == "set script":
		console(" - set script <name> step <step-id> <function> [options]       | Functions:")
	elif (arguments[:11] == "set default" and len(sys.argv) < 5) or arguments == "set default":
		console(" - set default credential <cred-obj-name>                      |  Set the default credential to use")
		console(" - set default device-type <device-type>                       |  Set the default device type to use on configured devices")
	elif arguments[:3] == "set" and len(sys.argv) >= 4:
		config.set(sys.argv)
	##### RUN #####
	elif arguments == "run":
		console(" - run script <script-name> device <device-name>               |  Create/modify a script to run against devices")
	elif (arguments[:10] == "run script" and len(sys.argv) < 6) or arguments == "run script":
		console(" - run script <script-name> device <device-name>               |  Create/modify a script to run against devices")
	elif arguments[:3] == "run" and len(sys.argv) >= 6:
		operations.run(sys.argv)
	##### TEST #####
	elif (arguments[:4] == "test" and len(sys.argv) < 5):
		console(" - test script <script-name> <delineator>                      |  Test a script by acting as the device (providing output)")
	elif arguments[:4] == "test" and len(sys.argv) >= 5:
		operations.test(sys.argv)
	##### CLEAR #####
	elif arguments == "clear":
		console(" - clear private-key <name>                                    |  Delete a private-key from the config")
		console(" - clear credential <name>                                     |  Delete a credential from the config")
		console(" - clear device <name>                                         |  Delete a device from the config")
		console(" - clear device-group <name> (all|<member-name>)               |  Delete a device-group member or group from the config")
		console(" - clear script <name> (all|<step-id>)                         |  Delete a step or whole script from the config")
	elif (arguments[:17] == "clear private-key" and len(sys.argv) < 4):
		console(" - clear private-key <name>                                    |  Delete a private-key from the config")
	elif (arguments[:16] == "clear credential" and len(sys.argv) < 4) or arguments == "clear credential":
		console(" - clear credential <name>                                     |  Delete a credential from the config")
	elif arguments[:18] == "clear device-group" and len(sys.argv) < 5:
		console(" - clear device-group <name> (all|<member-name>)               |  Delete a device-group member or group from the config")
	elif (arguments[:12] == "clear device" and len(sys.argv) < 4) or arguments == "clear device":
		console(" - clear device <name>                                         |  Delete a device from the config")
		console(" - clear device-group <name> (all|<member-name>)               |  Delete a device-group member or group from the config")
	elif (arguments[:12] == "clear script" and len(sys.argv) < 4) or arguments == "clear script":
		console(" - clear script <name> (all|<step-id>)                         |  Delete a step or whole script from the config")
	elif arguments[:5] == "clear" and len(sys.argv) >= 4:
		config.clear(sys.argv)
	######################
	######################
	else:
		console("----------------------------------------------------------------------------------------------------------------------------------------------")
		console("                     ARGUMENTS                                 |                                  DESCRIPTIONS")
		console("----------------------------------------------------------------------------------------------------------------------------------------------")
		console(" - install                                                     |  Install the conman components and dependencies")
		console(" - upgrade                                                     |  Upgrade the conman core")
		console("----------------------------------------------------------------------------------------------------------------------------------------------")
		console(" - show (config|run) [raw]                                     |  Show the current conman configuration")
		console("----------------------------------------------------------------------------------------------------------------------------------------------")
		console(" - set debug (module|timestamp|tracepath|format) [options]     |  Set the debugging output options")
		console(" - set private-key <name> <delineator_char>                    |  Create/modify a RSA private-key to use for SSH authentication")
		console(" - set credential <name> username <name> [options]             |  Create/modify a credential set to use to log into devices")
		console(" - set device <name> host <ip/hostname> [options]              |  Create/modify a target device for connections")
		console(" - set device-group <name> member <device-name>                |  Create/Modify a device group by adding a member device")
		console(" - set script <name> step <step-id> <function> [options]       |  Create/modify a script to run against devices")
		console(" - set default credential <cred-obj-name>                      |  Set the default credential to use")
		console(" - set default device-type <device-type>                       |  Set the default device type to use on configured devices")
		console("----------------------------------------------------------------------------------------------------------------------------------------------")
		console(" - run script <script-name> device <device-name>               |  Create/modify a script to run against devices")
		console("----------------------------------------------------------------------------------------------------------------------------------------------")
		console(" - test script <script-name> <delineator>                      |  Test a script by acting as the device (providing output)")
		console("----------------------------------------------------------------------------------------------------------------------------------------------")
		console(" - clear private-key <name>                                    |  Delete a private-key from the config")
		console(" - clear credential <name>                                     |  Delete a credential from the config")
		console(" - clear device <name>                                         |  Delete a device from the config")
		console(" - clear device-group <name> (all|<member-name>)               |  Delete a device-group member or complete group from the config")
		console(" - clear script <name> (all|<step-id>)                         |  Delete a step or whole script from the config")
		console("----------------------------------------------------------------------------------------------------------------------------------------------")


if __name__ == "__main__":
	ui = cli()
	interpreter()
	#s = config_script(config["scripts"]["MY_SCRIPT"], "")
	#s.run()




# UNIT TESTING #

# --- Script Steps Class --- #
		#config = {
		#			"steps": {
		#				"1.0": {"send": "show ip int br"},
		#				"1.0.1": {"dump-input": None},
		#				"2.0": {
		#					"if-match": {
		#						"regex": "interface.*$",
		#						"criterion": "partial"
		#					}
		#				}
		#			}
		#		}
		#


		#config = {
		#			"steps": {
		#				"2.1.1": {"send": "show ip int br"},
		#				"2.1": {"dump-input": None},
		#				"2": {"dump-input": None},
		#				"1.2": {"dump-input": None},
		#				"1.1": {"dump-input": None},
		#				"1.1.1": {"dump-input": None},
		#				"1.1.1.1": {"dump-input": None},
		#				"3.0.1": {"dump-input": None},
		#				"3.0.1.1": {"dump-input": None},
		#				"1.0.1.1.1": {"dump-input": None},
		#				"1": {"dump-input": None},
		#				"1.1.1.2": {"dump-input": None},
		#				"1.0.0.2": {"dump-input": None},
		#				"1.1.2": {"dump-input": None},
		#				"1.1.10": {"dump-input": None},
		#				"4": {"dump-input": None}
		#				}
		#		}
		#
		#
		#
		#
		#a = config["steps"]
		#b = steps_class(a)
		#
		#x = ['1', '1.1', '1.1.1', '1.2', '1.2.20', '2.1', '2.3', '10.0', '10.0.1.1', '10.1', '100']
		#x = ['100', "15.1", '15.100', '15', '1000', '1.5.43.23', '1.5.674.234', '1.5.7', '15.1.15', '1', '1.5.674.100', '1.5.674.1', '1.5.674', '1.5.674.1.1.1.1.1']
		#
		#a = config["steps"]
		#s = steps_class(a)
		##datalist = z.orderedobj
		##i = build_tree(datalist)
		#print(s._treestr)
		##b = s._get_stepset_dict(s._list[0])
		##s._convert_to_str(b).keys()
		#
		#
		#s._list[5].str



		#s.nullify(s._list[3])
		#s.set_input("SOMETHING HERE22222222", s._list[4])
		##s._list[5].valid
		#
		#
		#for each in range(16):
		#	print(s._list[each].str, s._list[each].input)

		#s.find_step_tree(s._list[1])
		#for each in range(10):
		#	b = s._find_step_tree(s._list[each])
		#	s._convert_to_str(b)
		#
		#
		# 
		# ['1.0', '1.0.1', '1.0.1.1', '1.1', '2', '2.1', '2.1.1', '3.0.1', '3.0.1.1', '4']
		#
		#



# conman set script CHANGE_VLAN_10_TO_20 credential MY_CREDS
# conman set script CHANGE_VLAN_10_TO_20 step 1 send "show run | in interface|switchport access vlan 30"
# conman set script CHANGE_VLAN_10_TO_20 step 1.1 for-match "FastEthernet1/0/..\n switchport access vlan 30" partial
# conman set script CHANGE_VLAN_10_TO_20 step 1.1.1 send munge SCRUB_CONFIG
# conman set script CHANGE_VLAN_10_TO_20 step 2 terminate




# conman set munge SCRUB_CONFIG 1.0 match any
# conman set munge SCRUB_CONFIG 1.1 set-variable DATA from-match "FastEthernet1/0/..\n switchport access vlan "
# conman set munge SCRUB_CONFIG 1.2 set-variable IFACE from-string "interface "
# conman set munge SCRUB_CONFIG 1.3 set-variable VLAN from-string " 40"
# conman set munge SCRUB_CONFIG 1.4 assemble IFACE DATA VLAN



# conman set private-key DEVEL_KEY ^
# -----BEGIN RSA PRIVATE KEY-----
# asdfasdfasdfasdf
# asdfasdfasdfasdf
# asdfasdfasdfasdf
# asdfasdfasdfasdf
# asdfasdfasdfasdf
# -----END RSA PRIVATE KEY-----
# ^

# conman set credential MY_CREDS username "admin"
# conman set credential MY_CREDS password "password123"

# conman set credential DEVEL_CRED username "ec2-user"
# conman set credential DEVEL_CRED private-key DEVEL_KEY

# conman set device MY_SWITCH host 10.0.0.1 credential MY_CREDS
# conman set device YOUR_SWITCH host yourswitch.kernshosting.com credential MY_CREDS

# conman set device-group SWITCHES member MY_SWITCH
# conman set device-group SWITCHES member YOUR_SWITCH

# conman set script REBOOT_SWITCH step 1 send "write"
# conman set script REBOOT_SWITCH step 1.1 if-match "[OK]" partial
# conman set script REBOOT_SWITCH step 1.1.1 send "reload"
# conman set script REBOOT_SWITCH step 1.2 else
# conman set script REBOOT_SWITCH step 1.2.1 terminate
# conman set script REBOOT_SWITCH step 2 send "reload"
# conman set script REBOOT_SWITCH step 2.1 if-match "[confirm]" partial
# conman set script REBOOT_SWITCH step 2.1.1 send "\n"
# conman set script REBOOT_SWITCH step 2.2 else
# conman set script REBOOT_SWITCH step 2.2.1 terminate

# conman set script SOMETHING step 1 send "show ip interface br"
# conman set script SOMETHING step 1.1 if-match "Gigibit" partial
# conman set script SOMETHING step 1.1.1 send "write mem"
# conman set script SOMETHING step 1.1.2 send "show version"
# conman set script SOMETHING step 1.1.1.1 if-match "15.0.1"
# conman set script SOMETHING step 1.1.1.1.1 send "show inventory"

# conman set script CHANGE_VLAN_10_TO_20 credential MY_CREDS
# conman set script CHANGE_VLAN_10_TO_20 step 1 send "show run | in interface|switchport access vlan 30"
# conman set script CHANGE_VLAN_10_TO_20 step 1.1 for-match "FastEthernet1/0/..\n switchport access vlan 30" partial
# conman set script CHANGE_VLAN_10_TO_20 step 1.1.1 send munge SCRUB_CONFIG
# conman set script CHANGE_VLAN_10_TO_20 step 2 terminate

# conman set munge SCRUB_CONFIG 1.0 match any
# conman set munge SCRUB_CONFIG 1.1 set-variable DATA from-match "FastEthernet1/0/..\n switchport access vlan "
# conman set munge SCRUB_CONFIG 1.2 set-variable IFACE from-string "interface "
# conman set munge SCRUB_CONFIG 1.3 set-variable VLAN from-string " 40"
# conman set munge SCRUB_CONFIG 1.4 assemble IFACE DATA VLAN

# conman set script REBOOT_SWITCH step 1 send "write"
# conman set script REBOOT_SWITCH step 1.1 if-match "[OK]" partial
# conman set script REBOOT_SWITCH step 1.1.1 send "reload"
# conman set script REBOOT_SWITCH step 1.2 else
# conman set script REBOOT_SWITCH step 1.2.1 terminate
# conman set script REBOOT_SWITCH step 2 send "reload"
# conman set script REBOOT_SWITCH step 2.1 if-match "[confirm]" partial
# conman set script REBOOT_SWITCH step 2.1.1 send "\n"
# conman set script REBOOT_SWITCH step 2.2 else
# conman set script REBOOT_SWITCH step 2.2.1 terminate


