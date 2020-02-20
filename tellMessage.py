##   Python !tell script for Hexchat
##   by Cycloneblaze

__module_name__ = "tellMessage"
__module_version__ = "4.4"
__module_description__ = "Store messages for users and deliver them later. Use !tell"
# required info

##
##   version history:
##      0.1 - first version
##          - just writing the thing
##          - additions listed like so
##      1.0 - first working version :P
##          - tells work with !tell
##      1.1 - now only catches !tell at the start of the messages, rather than anywhere
##          - proper load / unload text
##          - uses /say rather than /botserv say
##      2.0 - tells are split into public tells (using !tell) and private tells (using /notice botname @tell)
##          - tells are stored seperately for public / private
##      3.0 - new preference to define whether the user running the script or botserv repeats the stored
##            messages
##          - now catches all OSErrors, which should include PermissionErrors, FileNotFoundErrors and any
##            other error which would pop up and continually send, with try-except clauses
##          - banned nicknames consolidated into a set of variables for easier modifications
##          - plugin preferences can now be set and modified with commands (cuurently only 1 exists)
##          - deprecated private tells (the @tell function), they don't work very well and aren't very private
##      3.1 - changed the reply message
##      3.2 - fixed a bug caused by not capturing all text events (hilights)
##          - removed private tells (almost) entirely
##      4.0 - added a confirmation message when a tell is sent
##          - added a message telling the time since the message was stored, given when the message is delivered
##          - added prefs for both of these so they can be turned off
##          - consolidated pref settings into one function
##          - grammar: repeat -> deliver, tell -> messaage
##          - added a command to list the nicknames messages awaiting delivery
##      4.1 - now option 2 for /confirm uses /notice to deliver the confirmation privately
##          - removed zeroes
##          - new format for files: old messages will crash the script (but I won't fix it cause there aren't any 7:^])
##      4.2 - removed zeroes again, in less lines
##          - now case-insensitive for all commands and names
##      4.3 - consolidated some functions for less duplication of stuff
##          - fixed seconds(s)s(s)ss(s)
##      4.4 - added confirmation messages if the sender / recipient is banned
##          - commented all the things
##          - changed prefs such that 2 is the default value for CONFIRM
##
##
##  todo:
##      - Change bans so they are added / removed via prefs rather than hardcoded (although I imagine you'd just give a channel ban)
##      - Remove sub1 and sub2

import hexchat
import os
# import modules

hexchat.prnt("{} script v{} loaded. python code by Cycloneblaze".format(__module_name__, __module_version__))
# print loading message (using global values)

directory = 'C:/tells/'
sub1 = 'C:/tells/public/'
sub2 = 'C:/tells/private/'
# define where the tells are kept, somewhere we can access with no permissions
if not os.path.exists(directory):
    try:
        os.makedirs(directory)
        os.makedirs(sub1)
        os.makedirs(sub2)
# create the directories if they don't exist
    except(OSError):
        pass
# ignore errors

if hexchat.get_pluginpref('tellMessage_botserv') == None:
    hexchat.set_pluginpref('tellMessage_botserv', 1)
if hexchat.get_pluginpref('tellMessage_confirm') == None:
    hexchat.set_pluginpref('tellMessage_confirm', 2)
if hexchat.get_pluginpref('tellMessage_time') == None:
    hexchat.set_pluginpref('tellMessage_time', 1)
# initialise script preferences with defaults

services = ('Global', 'OperServ', 'BotServ', 'ChanServ',  'HostServ', 'MemoServ', 'NickServ')
# can't message Services - I don't think I've missed any
bots = ('Q', 'X', 'Porygon2', 'ChanStat', 'ChanStat-2')
# channel bots can't tell or be told, to avoid recursive spam stuff (add the bot if it's not one of these)
banned_users = ('tellbot', 'tellbot2')
# add nicknames who cannot use !tell (notably the user of the script, just in case). Must have at least 2 names (because it is a tuple)
banned = (services + bots + banned_users)

def timesince(seconds):
# function to convert a number of seconds to days hours minutes and seconds
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
# modular arithmetic
    global since
    if d < 0 or h < 0 or m < 0 or s < 0:
        since = ['E', 'E', 'E', 'E']
    else:
        since = [d, h, m ,s]
# store the values in a list, unless they are negative

def public_cb_tell_store(word, word_eol, userdata):
# function to find messages and write them to disk
    mesg = [0, 1]
# instantiate
    mesg[0] = hexchat.strip(word[0], -1, 3)
    mesg[1] = hexchat.strip(word[1], -1, 3)
    nick = hexchat.strip(mesg[0], -1, 3)
# separate the nickname and the message
    chan = hexchat.get_info("channel")
# get the channel name that the message was sent in
    userlist = hexchat.get_list('users')
    for i in userlist:
        if i.nick == nick:
            storetime = int(i.lasttalk)
# get the timestamp that the message was sent at (a unix time, like 1462736411)
    if not nick in banned and mesg[1].find("!") == 0 and mesg[1].lower().find('tell') == 1:
# ensure the sender is allowed to use tell and that the message is actually a !tell
        message = mesg[1].split()
        tonick = message[1]
        fromnick = hexchat.strip(mesg[0])
# get the sender and recipient by splitting the message into a list and taking the first and second index
        store_msg = ' '.join(message[2:])
# put the message back together
        store_msg = fromnick + ' ' + str(storetime) + ' ' +  store_msg
        store_msg = store_msg + '\n'
# create the message in a form we can read it later, with all the necessary info
        filename = str(sub1 + tonick.lower() + '.txt')
# the file we will store it in
        if not tonick in banned:
            try:
                with open(filename, 'a') as tells:
                    tells.write(store_msg)
# try to create the file and write the message / append the message to an existing list of messages
                    if hexchat.get_pluginpref('tellMessage_confirm') == 1:
                        if hexchat.get_pluginpref('tellMessage_botserv') == 1:
# if we want a confirmation and we want the bot to send it:
                            hexchat.command("botserv say {0} Your message to \002{1}\017 was stored successfully. They will receive it the next time they speak under that nickname (case insensitive).".format(chan, tonick))
                        elif hexchat.get_pluginpref('tellMessage_botserv') == 0:
# if we want a confirmation and we want to send it ourselves:
                            hexchat.command("say Your message to \002{0}\017 was stored successfully. They will receive it the next time they speak under that nickname (case insensitive).".format(tonick))
                    elif hexchat.get_pluginpref('tellMessage_confirm') == 2:
# if we want a confirmation via notice (so, not spamming the channel)
                        hexchat.command("notice {0} Your message to \002{1}\017 was stored successfully. They will receive it the next time they speak under that nickname (case insensitive).".format(fromnick, tonick))
            except(OSError):
                pass
# ignore errors
        elif tonick in banned:
# if the nickname is banned, give a message that sending didn't work
            if tonick in services:
                if hexchat.get_pluginpref('tellMessage_confirm') == 1:
                    if hexchat.get_pluginpref('tellMessage_botserv') == 1:
                        hexchat.command("botserv say {0} \002{1}\017 cannot recieve messages from this script because: \002{1}\017 is Network Services".format(chan, tonick))
                    elif hexchat.get_pluginpref('tellMessage_botserv') == 0:
                        hexchat.command("say \002{}\017 cannot recieve messages from this script because: \002{}\017 is Network Services".format(tonick))
                elif hexchat.get_pluginpref('tellMessage_confirm') == 2:
                    hexchat.command("notice {0} \002{1}\017 cannot recieve messages from this script because: \002{1}\017 is Network Services".format(fromnick, tonick))
            elif tonick in bots:
                if hexchat.get_pluginpref('tellMessage_confirm') == 1:
                    if hexchat.get_pluginpref('tellMessage_botserv') == 1:
                        hexchat.command("botserv say {0} \002{1}\017 cannot recieve messages from this script because: \002{1}\017 is channel bot".format(chan, tonick))
                    elif hexchat.get_pluginpref('tellMessage_botserv') == 0:
                        hexchat.command("say \002{}\017 cannot recieve messages from this script because: \002{}\017 is channel bot".format(tonick))
                elif hexchat.get_pluginpref('tellMessage_confirm') == 2:
                    hexchat.command("notice {0} \002{1}\017 cannot recieve messages from this script because: \002{1}\017 is channel bot".format(fromnick, tonick))
            elif tonick in banned_users:
                if hexchat.get_pluginpref('tellMessage_confirm') == 1:
                    if hexchat.get_pluginpref('tellMessage_botserv') == 1:
                       hexchat.command("botserv say {0} \002{1}\017 cannot recieve messages from this script because: \002{1}\017 is banned".format(chan, tonick))
                    elif hexchat.get_pluginpref('tellMessage_botserv') == 0:
                        hexchat.command("say \002{}\017 cannot recieve messages from this script because: \002{}\017 is banned".format(tonick))
                elif hexchat.get_pluginpref('tellMessage_confirm') == 2:
                    hexchat.command("notice {0} \002{1}\017 cannot recieve messages from this script because: \002{1}\017 is banned".format(fromnick, tonick))
        
    elif nick in banned and mesg[1].find("!") == 0 and mesg[1].lower().find('tell') == 1:
# if the user is banned tell them so, and why
        message = mesg[1].split()
        tonick = message[1]
        fromnick = hexchat.strip(mesg[0])
        if nick in services:
            if hexchat.get_pluginpref('tellMessage_confirm') == 1:
                if hexchat.get_pluginpref('tellMessage_botserv') == 1:
                    hexchat.command("botserv say {0} You are Network Services".format(chan))
                elif hexchat.get_pluginpref('tellMessage_botserv') == 0:
                    hexchat.command("say You are Network Services")
            elif hexchat.get_pluginpref('tellMessage_confirm') == 2:
                hexchat.command("notice {0} You are Network Services".format(fromnick))
        elif nick in bots:
            if hexchat.get_pluginpref('tellMessage_confirm') == 1:
                if hexchat.get_pluginpref('tellMessage_botserv') == 1:
                    hexchat.command("botserv say {0} You are a channel bot".format(chan))
                elif hexchat.get_pluginpref('tellMessage_botserv') == 0:
                    hexchat.command("say You are a channel bot")
            elif hexchat.get_pluginpref('tellMessage_confirm') == 2:
                hexchat.command("notice {0} You are a channel bot".format(fromnick))
        elif nick in banned_users:
            if hexchat.get_pluginpref('tellMessage_confirm') == 1:
                if hexchat.get_pluginpref('tellMessage_botserv') == 1:
                    hexchat.command("botserv say {0} You are not allowed to use this script".format(chan))
                elif hexchat.get_pluginpref('tellMessage_botserv') == 0:
                    hexchat.command("say You are not allowed to use this script")
            elif hexchat.get_pluginpref('tellMessage_confirm') == 2:
                hexchat.command("notice {0} You are not allowed to use this script: contact me for information".format(fromnick))
        
    return hexchat.EAT_NONE
# don't eat the event; let it print and other plugins get it

trying = 0
since = 0
# instantiate some variables

def public_cb_tell_return(word, word_eol, userdata):
# function to retrieve and deliver stored messages
    nick = hexchat.strip(word[0])
    chan = hexchat.get_info("channel")
    path = (sub1 + nick.lower() + '.txt')
# find the nickname that sent the message and the channel it was sent in; create the expected path to look for messages
    receivedtime = 0
    userlist = hexchat.get_list('users')
    for i in userlist:
        if i.nick == nick:
            receivedtime = int(i.lasttalk)
# instantiate, then find the time the message was recieved
    global trying
# use the 'trying' variable we created earlier, rather than making a new one
    if not nick in banned and os.path.exists(path) and trying == 0:
# if the nickname can recieve messages; if a file exists that contains messages; if we are not already delivering someone's messages
        try:
            tells = open(path, 'r+')
            trying = 1
# we are delivering messages now; set this variable so we don't try to do two things at once (heavy-handed I know)
            for line in tells:
# for each message, which is stored on its own line in the file, deliver the message
                linein = line.replace('\n', '')
# get rid of the newline character before we print
                seq = linein.split(' ')
                sentby = seq[0]
                storetime = int(seq[1])
                msg = ' '.join(seq[2:])
# split the message into a list, extract the sender's name and timestamp as the first two indices of this, put the message back together 
                diff = (receivedtime - storetime)
                timesince(diff)
# find the time (in seconds) since the message was sent, then convert it to a number of days, hours, mins and seconds
                if hexchat.get_pluginpref('tellMessage_botserv') == 1:
                    hexchat.command("botserv say {0} \002{1}\017 left a message for {2}: \'{3}\'".format(chan, sentby, nick, msg))
                elif hexchat.get_pluginpref('tellMessage_botserv') == 0:
                    hexchat.command("say \002{0}\017 left a message for {1}: \'{2}\'".format(sentby, nick, msg))
# send the message to chat, either using the channel bot or personally
                if hexchat.get_pluginpref('tellMessage_time') == 1:
# if we are giving a timestamp:
                    d, h, m, s = since[0], since[1], since[2], since[3]
                    first = "This message was left "
                    second_d, second_ds = "\002" + str(d) + "\017 day ", "\002" + str(d) + "\017 days "
                    second_h, second_hs = "\002" + str(h) + "\017 hour ", "\002" + str(h) + "\017 hours "
                    second_m, second_ms = "\002" + str(m) + "\017 minute ", "\002" + str(m) + "\017 minutes "
                    second_s, second_ss = "\002" + str(s) + "\017 second ", "\002" + str(s) + "\017 seconds "
                    third = "ago."
# create the possible bits of the message
                    final = first
                    if d != 0 and d != 1:
                        final = final + second_ds
                    elif d != 0 and d == 1:
                        final = final + second_d
                    if h != 0 and h != 1:
                        final = final + second_hs
                    elif h != 0 and h == 1:
                        final = final + second_h
                    if m != 0 and m != 1:
                        final = final + second_ms
                    elif m != 0 and m == 1:
                        final = final + second_m
                    if s != 0 and s != 1:
                        final = final + second_ss
                    elif s != 0 and s == 1:
                        final = final + second_s
                    final = final + third
# assemble the message depending on if we want to say 'day' or 'days', etc.
                    if d == 0 and h == 0 and m == 0 and s == 0:
                        final = first + "just moments " + third
# and provide a message if we delivered the tell in under one second!
                    if hexchat.get_pluginpref('tellMessage_botserv') == 1:
                        hexchat.command("botserv say {} {}".format(chan, final))
                    elif hexchat.get_pluginpref('tellMessage_botserv') == 0:
                        hexchat.command("say {}".format(final))
# finally deliver the message of how long it's been since the tell was stored, using the bot or not.
                    if d == 'E' or h == 'E' or m == 'E' or s == 'E':
                        print("Something went wrong creating the since (probably your system clock changed)")
# if the time was somehow negative... 
            tells.close()
            if tells.closed == True:
                try:
                    os.remove(path)
                except(OSError):
                    pass
            trying = 0
        except(OSError):
            pass
# close the (now-empty) file and remove it, ignore errors, reset 'trying' to allow us to deliver more messages.

    return hexchat.EAT_NONE

def prefs_cb(word, word_eol, userdata):
# function to set and retrieve the plugin's preferences
    if word[0].upper() == 'USEBOT':
# if we're trying to do something with the 'botserv' preference:
        if hexchat.get_pluginpref('tellMessage_botserv') == None:
            print('The value did not exist, initialising as 1...')
            hexchat.set_pluginpref('tellMessage_botserv', 1)
# if it somehow didn't exist, instantiate it as a default value
        elif len(word) == 1:
            print('Setting is', hexchat.get_pluginpref('tellMessage_botserv'))
# if we didn't provide a value to set the pref to, simply inform of the current value
        elif word[1] == '1' or word[1] == '0':
            value = hexchat.strip(word[1], -1, 3)
            hexchat.set_pluginpref('tellMessage_botserv', value)
# if we *did*, set the pref to that value
            if hexchat.get_pluginpref('tellMessage_botserv') == int(value):
                print('Setting set to', value)
            else:
                print('The plugin value was somehow not set to what you tried to set it to!')
# then print if it matches what we set it to (or if it doesn't?)
        else:
            print('Usage: /usebot <value>\nValid settings are 0 (you deliver the messages) and 1 (the bot delivers the messages)')
# complain if something invalid was given (e.g. '/usebot 111111' or '/usebot 0 ')

# do exactly the same thing two more times                                       
    elif word[0].upper() == 'SINCE':
        if hexchat.get_pluginpref('tellMessage_time') == None:
            print('The value did not exist, initialising as 1...')
            hexchat.set_pluginpref('tellMessage_time', 1)
        elif len(word) == 1:
            print('Setting is', hexchat.get_pluginpref('tellMessage_time'))
        elif word[1] == '1' or word[1] == '0':
            value = hexchat.strip(word[1], -1, 3)
            hexchat.set_pluginpref('tellMessage_time', value)
            if hexchat.get_pluginpref('tellMessage_time') == int(value):
                print('Setting set to', value)
            else:
                print('The plugin value was somehow not set to what you tried to set it to!')
        else:
            print('Usage: /usebot <value>\nValid settings are 0 (nothing is given) and 1 (time since storage is given)')
                                       
    elif word[0].upper() == 'CONFIRM':
        if hexchat.get_pluginpref('tellMessage_confirm') == None:
            print('The value did not exist, initialising as 2...')
            hexchat.set_pluginpref('tellMessage_confirm', 2)
        elif len(word) == 1:
            print('Setting is', hexchat.get_pluginpref('tellMessage_confirm'))
        elif word[1] == '2' or word[1] == '1' or word[1] == '0':
            value = hexchat.strip(word[1], -1, 3)
            hexchat.set_pluginpref('tellMessage_confirm', value)
            if hexchat.get_pluginpref('tellMessage_confirm') == int(value):
                print('Setting set to', value)
            else:
                print('The plugin value was somehow not set to what you tried to set it to!')
        else:
            print('Usage: /usebot <value>\nValid settings are 0 (no confirmation) and 1 (public confirmation of sending) and 2 (private confirmation of sending)')

    elif word[0].upper() == 'LISTPREFS':
# list all the preferences
        hexchat.prnt('\nThis is a list of all the plugin preferences.\nIt will include preferences from other plugins if they exist.\nAny which start with \'tellMessage_\' are for this plugin.\n\n')
        for i in hexchat.list_pluginpref():
            hexchat.prnt(str(i))
        hexchat.prnt('\nEnd of list.')

def listmsgs_cb(word, word_eol, userdata):
# function to list all the nicknames which we have stored messages for
    print('Nicknames with messages in C:/tells/public/ awaiting delivery:')
    for i in os.listdir(sub1):
        print(str(i).replace('.txt', ''))
# print all the filenames, less the file extension (which are the nicknames)
    if os.listdir(sub1) == []:
        print(None)
# if there are no files there are no messages, so just print None
    print('Nicknames with messages in C:/tells/private/ awaiting delivery:')
# do it for both directories
    for i in os.listdir(sub2):
        print(str(i).replace('.txt', ''))
    if os.listdir(sub2) == []:
        print(None)
    print('The next time these nicknames speak in a channel you are in they will receive their messages.')
# also be informative

def unload_cb(userdata):
    hexchat.prnt("{} script v{} unloaded".format(__module_name__, __module_version__))
# on the unload event, give a message that we unloaded

EVENTS = [("Channel Message"),("Your Message"),("Your Action"),("Channel Action"),("Channel Msg Hilight"),("Channel Action Hilight")]
# all the print events which we want to look for messages to store in / look for nicknames with messages to deliver in
for event in EVENTS:
	hexchat.hook_print(event, public_cb_tell_store)
	hexchat.hook_print(event, public_cb_tell_return)
# for all the events listed above, hook in our functions
hexchat.hook_unload(unload_cb)
# on an unload event, hook in our function and run it
hexchat.hook_command("USEBOT", prefs_cb, help="/USEBOT <value>\nValue is either 0 or 1: if 0, stored messages are delivered by you, if 1, they are delivered by the channel bot\nUsed by tellMessage.py")
hexchat.hook_command("CONFIRM", prefs_cb, help="/CONFIRM <value>\nValue is either 0 or 1: if 0, there is no confirmation message, if 1, a confirmation message is given in public chat by the channel bot\nIf 2, the message is given by you privately with /notice\nUsed by tellMessage.py")
hexchat.hook_command("SINCE", prefs_cb, help="/SINCE <value>\nValue is either 0 or 1: if 0, no time is given, if 1, the time since the message was stored is given along with the message itself\nUsed by tellMessage.py")
hexchat.hook_command("LISTMSGS", listmsgs_cb, help="/LISTMSGS \nGives a list of the nicknames with messages awaiting delivery\nUsed by tellMessage.py")
hexchat.hook_command("LISTPREFS", prefs_cb, help="/LISTPREFS")
# hook in appropriate functions when we get commands
