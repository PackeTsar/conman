# Conman

A CLI-based SSH/TELNET connection manager and scripting utility



-----------------------------------------
### Version
The version of Conman documented here is: **v0.0.1**



-----------------------------------------
### Table of Contents
1. [What is Conman?](#what-is-conman)
2. [Requirements](#requirements)
3. [Install Instructions](#install-instructions)
4. [Command Interface](#command-interface)
5. [Scripting](#scripting)


-----------------------------------------
### What is Conman?

Conman is a simply python-based SSH and TELNET connection manager and scripting utility. It is built to make the scripting of CLI-controlled devices easier and simpler for engineers. Conman primarily uses the Netmiko SSH/TELNET library to connect to and control remote devices.

##### What it DOES Do
- Supports both TELNET and SSH connection types
- Supports the use of username/password or username/private-key for SSH
- Supports and simple scripting syntax/framework to allow commandautomation
- Allows scripts to be run against individual devices or device-groups



--------------------------------------
### Requirements

OS:			**CentOS 7 for now. More to come!**

Python Interpreter:		**Python 2.7.X or 3.6.X**



----------------------------------------------
### Install Instructions

The install of Conman is very quick and straightforward using the built-in installer.
NOTE: You need to be logged in as root or have sudo privileges on the system to install Conman


1. Install OS with appropriate IP and OS settings and update to latest patches (recommended)
	- Check out the [CentOS Minimal Server - Post-Install Setup][centos-post-install] for help with some of the post-OS-install configuration steps.
2. Install the Git client (unless you already have the Conman files): `sudo yum install git -y` or `sudo apt install git -y`
3. Clone the Conman repo to any location on the box: `git clone https://github.com/PackeTsar/conman.git`
4. Change to the directory where the Conman main code file (conman.py) is stored: `cd conman`
5. Run the Conman program in install mode to perform the installation: `sudo python conman.py install`
6. Conman will install it's dependencies (epel-release, pip, Netmiko), create the config file at (/etc/conman/conman.cfg), create a conman executable file at (/bin/conman), and install a BASH completion script at (/etc/profile.d/conman-complete.sh)
	- Check the output of the command to see if any of the install functions failed
7. Log out of your SSH session and log back in to the terminal to activate the completion script
8. Type `conman` at the BASH prompt and hit ENTER to get a list of command options
	- Run the command `conman show config` to see the current configuration of the Conman app. You can also run the command `conman show config raw` to see the raw config file data
	- You should be able to use the TAB key to see the available command options and to help complete commands when typing them out



----------------------------------------------
### Command Interface

The Conman command line interface is built to be simple to use and understand. At any point, when typing out a command, you can use the TAB key to see the available options, or hit ENTER with a partial command entered to get some help with the syntax.

Below is the CLI guide for the Conman Utility

```
----------------------------------------------------------------------------------------------------------------------------------------------
                     ARGUMENTS                                 |                                  DESCRIPTIONS
----------------------------------------------------------------------------------------------------------------------------------------------
 - install                                                     |  Install the conman components and dependencies
 - upgrade                                                     |  Upgrade the conman core
----------------------------------------------------------------------------------------------------------------------------------------------
 - show (config|run) [raw]                                     |  Show the current conman configuration
----------------------------------------------------------------------------------------------------------------------------------------------
 - set debug (module|timestamp|tracepath|format) [options]     |  Set the debugging output options
 - set private-key <name> <delineator_char>                    |  Create/modify a RSA private-key to use for SSH authentication
 - set credential <name> username <name> [options]             |  Create/modify a credential set to use to log into devices
 - set device <name> host <ip/hostname> [options]              |  Create/modify a target device for connections
 - set device-group <name> member <device-name>                |  Create/Modify a device group by adding a member device
 - set script <name> step <step-id> <function> [options]       |  Create/modify a script to run against devices
 - set default credential <cred-obj-name>                      |  Set the default credential to use
 - set default device-type <device-type>                       |  Set the default device type to use on configured devices
----------------------------------------------------------------------------------------------------------------------------------------------
 - run script <script-name> device <device-name>               |  Create/modify a script to run against devices
----------------------------------------------------------------------------------------------------------------------------------------------
 - test script <script-name> <delineator>                      |  Test a script by acting as the device (providing output)
----------------------------------------------------------------------------------------------------------------------------------------------
 - clear private-key <name>                                    |  Delete a private-key from the config
 - clear credential <name>                                     |  Delete a credential from the config
 - clear device <name>                                         |  Delete a device from the config
 - clear device-group <name> (all|<member-name>)               |  Delete a device-group member or complete group from the config
 - clear script <name> (all|<step-id>)                         |  Delete a step or whole script from the config
----------------------------------------------------------------------------------------------------------------------------------------------
```



----------------------------------------------
### Scripting

The main use for Conman is its simple scripting functionality

#### Step Numbers
Step numbering forms the backbone of the Conman scripting system. Steps are broken into dot-decimal notation (ie: 10.10.1 or 52.64.1110) with no real limit to the value of each sub-step or the quantity of sub-steps (10.20.35.40.99999.1.... and so on).

The information in each step number is used in two primary ways:
1. The value of each sub-step is used to determine the position of the step between other steps in the script (where the left-most sub-step numbers in the step are the highest order ones)
2. The dot-decimal function is used to determine parent-child-grandchild... inheritance (step 1.1 is a child of step 1) with the following functionality
	- The output of a step is distributed to its children (and not to its grandchildren)
		- Example: If step 100 sends a CLI command, then the output back from the device will be fed into step 100.1 (if it exists)

#### Functions
Each step will contain a function. Each function accepts an input (which comes from its parent step) and will provide some kind of output which can either be discarded or used in child steps.

Below is a list of currently configurable scripting Functions

##### send
	- DESCRIPTION: Sends a statically configured string to a remote device
	- ARGUMENTS: Static string (ie: `show version`) after the function
	- INPUT: Discarded
	- OUTPUT: Any text data returned by the device after the command is run
	- EXAMPLE: `conman set script CISCO step 1 send "show version"`

##### dump-input
	- DESCRIPTION: Prints its input to the terminal for user viewing
	- ARGUMENTS: None
	- INPUT: Printed to screen
	- OUTPUT: Input data is passed on as output
	- EXAMPLE: `conman set script CISCO step 1.1 dump-input`

##### terminate
	- DESCRIPTION: Terminates the device socket and sets the terminate flag to stop rule processing
	- ARGUMENTS: None
	- INPUT: Discarded
	- OUTPUT: None
	- EXAMPLE: `conman set script CISCO step 2 terminate`

##### if-match
	- DESCRIPTION: Runs a regular expression (Regex) match against its input, if a match is found, the matched data is passed as output and child steps are allowed to run. If no match is found, child steps are discarded and not run.
	- ARGUMENTS: Static regular expression string (ie: `^interface.*$`) after the function. Match criterion (`partial` or `complete`) after the regex string.
	- INPUT: Searched using the regular expression
	- OUTPUT: The string returned by the regex match
	- EXAMPLE: `conman set script TEST step 100 if-match "^interface.*$" complete`

##### for-match
	- DESCRIPTION: Similar to `if-match` except that it processes the child steps in a for-loop against each regex match returned by the search
	- ARGUMENTS: Static regular expression string (ie: `^interface.*$`) after the function
	- INPUT: Searched using the regular expression
	- OUTPUT: The string returned by each of the matches returned by regex
	- EXAMPLE: `conman set script TEST step 100 for-match "^interface.*$"`

##### run-script
	- DESCRIPTION: Allows the script to run another script as a slave, passing its input into the slave script to be used by first-order steps
	- ARGUMENTS: Script name after the function
	- INPUT: Passed into the slave script to be used by first order steps (ie: step 1 or step 5)
	- OUTPUT: Final output of the slave script is passed to this steps children as inputs
	- EXAMPLE: `conman set script TEST step 100 run-script OTHER_SCRIPT`














[centos-post-install]: https://github.com/PackeTsar/scriptfury/blob/master/CentOS_Post_Install.md