#!/usr/bin/python


#####            Conman Utility             #####
#####       Written by John W Kerns         #####
#####      http://blog.packetsar.com        #####
#####  https://github.com/packetsar/conman  #####

import os
import re
import sys
import json
import netmiko
import paramiko


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
	defaultconfig = '''{}'''
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
        COMPREPLY=( $(compgen -W "credential device script private-key" -- $cur) )
        ;;
      "hidden")
        COMPREPLY=( $(compgen -W "show" -- $cur) )
        ;;
      "show")
        COMPREPLY=( $(compgen -W "config run" -- $cur) )
        ;;
      "set")
        COMPREPLY=( $(compgen -W "credential device script default private-key" -- $cur) )
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
          COMPREPLY=( $(compgen -W "credentials devices scripts script-steps supported-devices -" -- $cur) )
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
      fi
    fi
  elif [ $COMP_CWORD -eq 5 ]; then
    prev3=${COMP_WORDS[COMP_CWORD-3]}
    prev4=${COMP_WORDS[COMP_CWORD-4]}
    if [ "$prev4" == "set" ]; then
      if [ "$prev3" == "device" ]; then
        COMPREPLY=( $(compgen -W "<hostname-or-IP-address> -" -- $cur) )
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
        COMPREPLY=( $(compgen -W "${inserts} <step-id> -" -- $cur) )
      fi
    fi
  elif [ $COMP_CWORD -eq 6 ]; then
    prev4=${COMP_WORDS[COMP_CWORD-4]}
    prev5=${COMP_WORDS[COMP_CWORD-5]}
    if [ "$prev5" == "set" ]; then
      if [ "$prev4" == "device" ]; then
        COMPREPLY=( $(compgen -W "credential type <enter>" -- $cur) )
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
      fi
    fi
    if [ "$prev6" == "set" ]; then
      if [ "$prev5" == "credential" ]; then
        if [ "$prev" == "password" ]; then
          COMPREPLY=( $(compgen -W "<ssh-password> -" -- $cur) )
        fi
        if [ "$prev" == "private-key" ]; then
          COMPREPLY=( $(compgen -W "<private-key-object-name> -" -- $cur) )
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
          COMPREPLY=( $(compgen -W "type <enter>" -- $cur) )
        fi
        if [ "$prev2" == "type" ]; then
          COMPREPLY=( $(compgen -W "credential <enter>" -- $cur) )
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
		from netmiko.ssh_dispatcher import CLASS_MAPPER_BASE as supported_devices
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
		privatekeytext = ""
		for key in self.running["private-keys"]:
			current = config_private_key({key: self.running["private-keys"][key]})
			privatekeytext += current.set_cmd+"\n"
		privatekeytext += "!\n########################\n!\n"
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
		devicetext += "!\n########################\n!\n"
		####################
		scripttext = ""
		for script in self.running["scripts"]:
			current = script_class({script: self.running["scripts"][script]}, None)
			curscript = ""
			for cmd in current.set_cmd_list:
				curscript += " ".join(cmd)+"\n"
			scripttext += curscript
		scripttext += "!\n########################\n!\n"
		####################
		defaulttext = ""
		current = config_default({"defaults": self.running["defaults"]})
		defaulttext += current.set_cmd+"\n"
		defaulttext += "!\n########################\n"
		####################
		configtext += privatekeytext
		configtext += credentialtext
		configtext += devicetext
		configtext += scripttext
		configtext += defaulttext
		print(configtext)
	def hidden(self, args):
		item = args[3]
		simple = ["credentials", "devices", "scripts", "private-keys"]
		if item in simple:
			self.hidden_show_simple(item)
		elif item == "script-steps":
			self.hidden_show_script_steps(args)
		elif item == "supported-devices":
			for each in self.supported_devices:
				print(each)
	def hidden_show_simple(self, item):
		if item in list(self.running):
			for each in self.running[item]:
				print(each)
	def hidden_show_script_steps(self, args):
		script = item = args[4]
		if "scripts" in list(self.running):
			if script in list(self.running["scripts"]):
				for step in self.running["scripts"][script]["steps"]:
					print step
	def clear(self, args):
		function = args[2]
		simple = ["device", "credential", "private-key"]
		if function in simple:
			self.clear_simple(args)
		elif function == "script":
			self.clear_script(args)
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
	def set(self, args):
		maps = {
		"device": config_device,
		"credential": config_credential,
		"script": script_class,
		"default": config_default,
		"private-key": config_private_key
		}
		function = args[2]
		if function in maps:
			newobj = maps[function](args)
			if function+"s" not in list(self.running):
				self.running.update({function+"s": {}})
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
		self.credentialname = self.attrib()
		self.credential = None
		self.type = self.attrib()
		#self._input_profile = {
		#	3: self._obj_name_chk,
		#	4: "credential",
		#	5: self._obj_name_chk,
		#	6: "host",
		#	8: None}
		self._input_profile = {
			3: self._obj_name_chk,
			4: "host",
			6: ["credential", "type"]}
		self._attribs = {
			"credential": self.credentialname, "host": self.host, "type": self.type}
		self._attrib_order = ["host", "credential", "type"]
		############
		self._sort_input(inputdata)
		############
		self._check_type()
	def _check_type(self):
		if str(self.type) == "":
			self.type = config.running["defaults"]["device-type"]
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
			"host": str(self.host)}
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


# Class for interpreting and executing configured scripts
class script_class(config_common):
	def __init__(self, inputdata, sock=None, globalinput=None):
		self._commons()  # Build common vars
		############
		self.function = "script"
		self.sock = sock  # Save the socket as a local variable
		self.globalinput = globalinput
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
			return self
		def __next__(self): # Python 3: def __next__(self)
			if self._iterindex == len(self._list):
				self._iterindex = 0
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
		def nullify(self, step=None):  # Nullify current and child steps
			if not step:
				step = self._list[self._iterindex-1]
			for each in self._get_stepset_list(step):
				each.valid = False
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
	def __output(self, outputdata):
		self.steps.store_output(outputdata)  # Write to child steps
		self.lastoutput = outputdata  # Write to last output store
	def _send(self, step):
		command = step.instructions["send"]
		output = self.sock.send_command_timing(command)
		self.__output(output)
	def _terminate(self, step):
		self.sock.disconnect()  # Kill socket
		self.__output(step.input)  # Pass on inputdata
		self.terminate = True  # Set termination flag
	def _dump_input(self, step):
		# No required args here
		ui.write_log(step.input)
		self.__output(step.input)  # Pass to children
	def _if_match(self, step):
		regex = step.instructions["if-match"]["regex"]
		criterion = step.instructions["if-match"]["criterion"]
		search = search_class(regex, step.input)
		ui.write_log("Regex match returned: %s" % search.matchlist)
		if (criterion == "partial" and search.partial
			) or (criterion == "complete" and search.complete):
			ui.write_log("Match confirmed")
			self.__output(step.input)  # Pass to children
		else:
			ui.write_log("No pattern matched")
			self.steps.nullify()  # Invalidate all offspring
	def _for_match(self, step):
		regex = step.instructions["for-match"]["regex"]
		search = search_class(regex, step.input)
		childinst = self.steps.get_offspring_config()
		for match in search.matchlist:
			newscript = script_class({step.str: {"steps": childinst}}, self.sock, globalinput=match)
			newscript.run()
		self.steps.nullify() # Nullify offspring to prevent linear run
	def _run_script(self, step):
		script = step.instructions["run-script"]
		if script in config.running["scripts"]:
			newscript = script_class({script: config.running["scripts"][script]}, self.sock, globalinput=step.input)
			output = newscript.run()
			self.__output(output)
		else:
			ui.write_log("Script %s not found. Skipping" % script)
			self.steps.nullify()
	def run(self):
		lastoutput = None
		funcmap = {  # Map config function names to actual methods
			"send": self._send,
			"dump-input": self._dump_input,
			"if-match": self._if_match,
			"terminate": self._terminate,
			"for-match": self._for_match,
			"run-script": self._run_script
		}
		for step in self.steps:  # Iter through step objects in order
			if not self.terminate:
				#####
				ui.write_log("Executing step %s" % step.origstr)
				inputdata = step.input  # Pull output from last loop
				function = list(step.instructions)[0]  # Set function name
				ui.write_log("Instructions: %s" % step.instructions)
				#####
				if not step.valid:  # If it has been marked invalid
					ui.write_log("Step %s has been invalidated. Skipping" 
						% step.origstr)
				else:
					ui.write_log("Step %s is valid. Continuing" % step.origstr)
					funcmap[function](step)
				ui.write_log("Step %s complete" % step.origstr)
				ui.write_log("\n\n\n")
			else:
				ui.write_log("Terminate flag set. Terminating script")
				return self.lastoutput
		return self.lastoutput  # Return the socket after complete

#c = {'SHORT': {u'steps': {u'1': {u'send': u'show ver'}, u'1.1': {u'dump-input': None}}}}
#
#a = script_class(b, None)
#b = ['conman', 'set', 'script', 'SHORT', 'step', '1', u'send', u'"show ver"']


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
		if args[2] == "script":
			scriptname = args[3]
			devicename = args[5]
			self.run_script(scriptname, devicename)
	def test_script(self, scriptname, delineator):
		if scriptname not in list(config.running["scripts"]):
			print("Script (%s) not in configuration" % scriptname)
			return None
		sock = test_sock(delineator)
		script = script_class({scriptname: config.running["scripts"][scriptname]}, sock)
		script.run()
	def run_script(self, scriptname, devicename):
		if scriptname not in list(config.running["scripts"]):
			print("Script (%s) not in configuration" % scriptname)
			return None
		if devicename not in list(config.running["devices"]):
			print("Device (%s) not in configuration" % devicename)
			return None
		device = config_device({devicename: config.running["devices"][devicename]})
		sock = device.make_sock()
		script = script_class({scriptname: config.running["scripts"][scriptname]}, sock)
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
netmiko.base_connection.BaseConnection._connect_params_dict = _new_connect_params_dict


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
	operations = operations_class()
	if arguments == "test":
		print("testing")
	if arguments == "next":
		print("- Create working recursive script")
		print("- script_class should be able to skip steps (after a loop) all together (not nullify)")
		print("- Build private-key config objects (or string processing in scripts)")
		print("- Integrate Munge engine into system")
		print("- Clean up text output handling (remove all prints)")
		print("- More script functions: elif-match, else, set-variable, enter-config, exit-config")
		print("- Build: credential-groups, device-groups")
		print("- Add debug to script run. Quiet if not")
		print("- SSH with custom port")
		print("- Apply scripts as login scripts")
		print("- ISSUE: A bad RSA key throws a TypeError from Paramiko")
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
		console(" - set private-key <name> <delineator_char>                    |  Create/modify a RSA private-key to use for SSH authentication")
		console(" - set credential <name> username <name> [options]             |  Create/modify a credential set to use to log into devices")
		console(" - set device <name> host <ip or hostname> [options]           |  Create/modify a configured target device for connections")
		console(" - set script <name> step <step-id> <function> [options]       |  Create/modify a script to run against devices")
		console(" - set default credential <cred-obj-name>                      |  Set the default credential to use")
		console(" - set default device-type <device-type>                       |  Set the default device type to use on configured devices")
	elif (arguments[:15] == "set private-key" and len(sys.argv) < 5):
		console(" - set private-key <name> <delineator_char>                    |  Create/modify a RSA private-key to use for SSH authentication")
	elif (arguments[:14] == "set credential" and len(sys.argv) < 8) or arguments == "set credential":
		console(" - set credential <name> username <name> (password|private-key) <value>")
	elif (arguments[:10] == "set device" and len(sys.argv) < 6) or arguments == "set device":
		console(" - set device <name> host <ip or hostname> (credential <name>)")
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
		console(" - clear script <name> [step-id]                               |  Delete a step or whole script from the config")
	elif (arguments[:17] == "clear private-key" and len(sys.argv) < 4):
		console(" - clear private-key <name>                                    |  Delete a private-key from the config")
	elif (arguments[:16] == "clear credential" and len(sys.argv) < 4) or arguments == "clear credential":
		console(" - clear credential <name>                                     |  Delete a credential from the config")
	elif (arguments[:12] == "clear device" and len(sys.argv) < 4) or arguments == "clear device":
		console(" - clear device <name>                                         |  Delete a device from the config")
	elif (arguments[:12] == "clear script" and len(sys.argv) < 4) or arguments == "clear script":
		console(" - clear script <name> [step-id]                               |  Delete a step or whole script from the config")
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
		console(" - set private-key <name> <delineator_char>                    |  Create/modify a RSA private-key to use for SSH authentication")
		console(" - set credential <name> username <name> [options]             |  Create/modify a credential set to use to log into devices")
		console(" - set device <name> credential <cred-obj> host <ip/hostname>  |  Create/modify a target device for connections")
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
		console(" - clear script <name> [step-id]                               |  Delete a step or whole script from the config")
		console("----------------------------------------------------------------------------------------------------------------------------------------------")


if __name__ == "__main__":
	ui = cli()
	interpreter()
	#s = script_class(config["scripts"]["MY_SCRIPT"], "")
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


