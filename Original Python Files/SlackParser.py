#Note, all variables have their type as the last word, are in a format with descriptive words seperated by an '_' underscore.
#ie: the variable json_files_list is a list of strings containing json files.

#Import statements
import os, sys, time, re, json, csv
from datetime import datetime



#msgObj are objects storing information related to individual Slack messages.
class msgObj(object):
   #init method
   def __init__(self, msg_element_dict, users_list):
      for key in msg_element_dict:
         setattr(self, key, msg_element_dict[key])
      if 'user' not in self.__dict__ or 'ts' not in self.__dict__:
         print('[ERROR] message object missing critical element.')

   #Getter function that returns the entire contents of the object.
   def getContent(self):
      return self.__dict__
   
   #Getter function that returns parsed message content in a readable form.
   def getMsg(self, users_list):
      time_str = getattr(self, 'ts')
      user_str = getattr(self, 'user')
      img_link_str = ''
      if 'attachments' in dir(self):
         try:
            full_attch_dict = getattr(self, 'attachments')[0]
         except:
            print('[ERROR] Unable to get "attachment" element while creating message object.')
         if 'from_url' in full_attch_dict:
            attch_link_str = full_attch_dict.get('from_url')
         elif 'url_private' in full_attch_dict:
            attch_link_str = full_attch_dict.get('url_private')
         if 'image_url' in full_attch_dict:
            img_link_str = full_attch_dict.get('image_url')
         attch_link_str = '<a href=' + attch_link_str + '><img border="0" alt="ATTACHMENT TYPE DOES NOT SUPPORT A PREVIEW" src=' + img_link_str + ' width="100" height="100"></a>'
      elif 'files' in dir(self):
         try:
            full_attch_dict = getattr(self, 'files')[0]
         except:
            print('[ERROR] Unable to get "files" element while creating message object.')
         if 'url_private' in full_attch_dict:
            attch_link_str = full_attch_dict.get('url_private')
         elif 'permalink' in full_attch_dict:
            attch_link_str = full_attch_dict.get('permalink')
         if 'thumb_pdf' in full_attch_dict:
            img_link_str = full_attch_dict.get('thumb_pdf')
         elif 'thumb_64' in full_attch_dict:
            img_link_str = full_attch_dict.get('thumb_64')
         elif 'thumb_80' in full_attch_dict:
            img_link_str = full_attch_dict.get('thumb_80')
         attch_link_str = '<a href=' + attch_link_str + '><img border="0" alt="ATTACHMENT TYPE DOES NOT SUPPORT A PREVIEW" src=' + img_link_str + ' width="100" height="100"></a>'
      try:
         return str(timeConverter(float(time_str)) + "<br>" + str(readUserName(user_str, users_list)) + "<br>" + getattr(self, 'text') + attch_link_str)
      except:
         return str(timeConverter(float(time_str)) + "<br>" + str(readUserName(user_str, users_list)) + "<br>" + getattr(self, 'text'))

   #Getter function that returns the name of the person who posted the message.
   def getName(self):
      return getattr(self, 'user') 


#slackUser are objects storing information related to Slack user profiles.
class slackUser(object):
   #Init function
   def __init__(self, user_element_dict):
      for key in user_element_dict:
         if 'profile' not in key:
            setattr(self, key, user_element_dict[key])
         else:
            nested_attributes = user_element_dict['profile']
            for nested_key in nested_attributes:
               setattr(self, nested_key, nested_attributes[nested_key])
      if 'id' not in self.__dict__ or 'real_name' not in self.__dict__ or 'image_24' not in self.__dict__:
         print('[ERROR] Slack user object is missing critical element(s).')

   #Getter function that returns the unique ID used by Slack that is associated with the user object.
   def getID(self):
      return getattr(self, 'id')

   #Getter function that returns the name of the user. 
   def getName(self):
      return getattr(self, 'real_name')
         
   #Getter function that returns the Slack profile picture of a user. 
   def getIcon(self):
      return getattr(self, 'image_24')



#channelObj are objects storing information related to channels in the exported Slack server.
class channelObj(object):
   def __init__(self, channel_element_dict):
      for key in channel_element_dict:
         setattr(self, key, channel_element_dict[key])
      if 'creator' not in self.__dict__ or 'created' not in self.__dict__ or 'members' not in self.__dict__:
         print('[ERROR] channel object is missing critical element.')
         

   #Getter function that returns a string containing a description of the channel.
   def getChannelDesc(self, users_list):
      ts_str = timeConverter(float(getattr(self, 'created')))
      for slack_user_obj in users_list:
         if getattr(self, 'creator') in slack_user_obj.getID():
            creator_str = slack_user_obj.getName()
            break
         else:
            creator_str = '[Error] Check "user.json" file.'
      members_list = []
      for user_str in getattr(self, 'members'):
         for slack_user_obj in users_list:
            if user_str in slack_user_obj.getID():
               members_list.append(slack_user_obj.getName())
      channel_desc = str('<p>Channel name: ' + getattr(self, 'name') + '<br>Created on: ' + ts_str + ' by: ' + creator_str + '.<br> Members: ' + str(members_list) + '</p>')
      return channel_desc

   #Getter function that returns the name of the channel.
   def getName(self):
      return getattr(self, 'name')


#Creates a CSV file for each channel in the Slack Server
def createCSV(file_str, file_names_list, working_dir_str):
   file_str = file_str.replace('.html', '')
   csv_data_list = []
   csv_keys_list = []
   
   for directory_str in file_names_list:
      if 'index' not in directory_str:
         os.chdir(directory_str.replace('.html', ''))
         json_files_list = os.listdir()
         output_file = open(directory_str.replace('.html', '') + '.csv', 'w', newline='')
         for file_str in json_files_list:
            if '.json' in file_str:
               with open(file_str) as input_file:
                  csv_data_list = json.load(input_file)
               for entry in csv_data_list:
                  for key in entry.keys():
                     if key not in csv_keys_list:
                        csv_keys_list.append(key)
         output_writer = csv.writer(output_file)
         output_writer.writerow(csv_keys_list)
         
         for file_str in json_files_list:
            if '.json' in file_str:
               with open(file_str, 'r') as csv_file:
                  csv_writer = csv.DictWriter(output_file, fieldnames= csv_keys_list, restval='', extrasaction='raise')
                  csv_data_list = json.load(csv_file)
                  for row in csv_data_list:
                     csv_writer.writerow(row)
               for key in csv_keys_list:
                  for row in csv_data_list:
                     for value in row:
                        if key in value:
                           row.pop(value)
                           break
               csv_data_list.clear()
         output_file.close()
         os.chdir('..')
         print('Finished creating CSV for ' + directory_str)



#Function that create the HTML index file.
def createIndex(channels_list, file_names_list):
   html_doc_file = open('index.html', 'w')
   print("Creating index.html")
   nav_bar_text_str = addNavBar(channels_list, file_names_list)
   html_doc_file = open('index.html', 'w')
   html_doc_file.write('<!DOCTYPE html>\n<html>\n<head>\n<meta name="viewport" content="width=device-width, initial-scale=1">\n<style> li { display: inline; } </style>\n\n' + nav_bar_text_str)


#Function that is given two lists containing data about the channels, and returns a string containing the HTML code to create the navigation bar.
def addNavBar(channels_list, file_names_list):
   nav_bar_str = '<ul>'
   for item in file_names_list:
      nav_bar_str += '<li><a href=' + item + '>' + item.replace('.html', '') + '</a></li>\n'
   nav_bar_str += '<ul>'
   return nav_bar_str


#Function that returns a string containing the channel description for any given HTML file.
def addChannelDesc(file_str, channels_list, users_list):
   file_str = file_str[:-5]
   for channel_obj in channels_list:
      if file_str in channel_obj.getName():
         return channel_obj.getChannelDesc(users_list)
   

#Function that creates an HTML file with a number of arguments.
def createHTML(file_str, channels_list, users_list, file_names_list):
   html_doc_file = open(file_str, 'w')
   nav_bar_str = addNavBar(channels_list, file_names_list)
   channel_desc_str = addChannelDesc(file_str, channels_list, users_list)
   message_str = """<!DOCTYPE html>\n\t<html>\n\t<head>\n\t<meta name="viewport" content="width=device-width, initial-scale=1"> \n\t<style> \n\tli { \n\tdisplay: inline; \n\t} \n\t.clps { \n\tborder-radius: 8px; \n\tbackground-color: rgb(229, 231, 234); \n\tcolor: black; \n\tcursor: pointer; \n\tpadding: 18px; \n\tmargin:5px; \n\twidth: 100%; \n\tborder: 1px solid black; \n\ttext-align: left; \n\toutline: none; \n\tfont-size: 15px; \n\t}\n \n\t.active, .collapsible:hover { \n\tbackground-color: rgb(229, 231, 234); \n\t}\n \n\t.content { \n\tborder-radius: 8px; \n\tpadding: 0 18px; \n\tdisplay: none; \n\toverflow: hidden; \n\tbackground-color: rgb(242, 230, 128); \n\tborder: 1px solid black; \n\t} \n\t</style> \n\t</head>""" + nav_bar_str + '<br>' + str(channel_desc_str) + '<body>'
   
   html_doc_file.write(message_str)
   html_doc_file.close()


#Function calls several other functions, writing to the given HTML file and adding message content.
def addToReport(msg_list, names_dict, file_str, working_dir_str):
   html_doc_file = open((os.path.join(working_dir_str + '\\' + file_str)), 'a')
   picture_url_str = ''
   msg_display_str = ''
   msg_content_str = ''
   for msg_item in msg_list:
      picture_url_str = userIcons(msg_item.getName(), names_dict)
      msg_display_str = msg_item.getMsg(names_dict)
      msg_content_str = msg_item.getContent()
      html_doc_file.write('<button class="clps">' + "<img src=" + str(picture_url_str) + ' padding= 5px align="middle">' + str(msg_display_str) + '</button>\n')
         
      html_doc_file.write('<div class="content"> <p>'+ str(msg_content_str) + '</p></div>\n')
   html_doc_file.close()


#Function called as the last step in writing to any non-index HTML file.
def finalizeReport(file_name_str, html_files_list, working_dir_str):
   print('Finalizing report for ' + file_name_str)
   html_doc_file = open((os.path.join(working_dir_str + '\\' + file_name_str)), 'a')
   message = """\n<script> \n\t var col = document.getElementsByClassName("clps"); \n\tvar i; \n\tfor (i = 0; i < col.length; i++) {  \n\tcol[i].addEventListener("click", function() {  \n\tthis.classList.toggle("active");  \n\tvar content = this.nextElementSibling;  \n\tif (content.style.display === "block") {  \n\tcontent.style.display = "none";  \n\t} else {  \n\tcontent.style.display = "block";  \n\t}  \n\t});  \n\t} </script></body></html>"""
   html_doc_file.write(message)
   html_doc_file.close()


#Function that is called to convert a UNIX timestamp into an easily readable time using datatime library.
def timeConverter(time_str):
   return datetime.utcfromtimestamp(time_str).strftime('%Y-%m-%d %H:%M:%S')


#Function that is called to return a user name for a given user ID.
def readUserName(user_str, users_list):
   for item in users_list:
      if user_str in item.getID():
         return item.getName()


#Function that returns the correctly parsed permanent link to a Slack user's profile picture.
def userIcons(user_str, users_list):
   for item in users_list:
      if user_str in item.getID():
         return item.getIcon()


#Function reads the "user" JSON file and returns a list of slackUser objects.
def readUser(users_file_str):
   users_list = []
   full_user_list = []
   with open(users_file_str, 'r') as users_file:
      user_file_list = json.load(users_file)
   for user_dict in user_file_list:
      users_list.append(slackUser(user_dict))
   return users_list


#Function reads the "channels" JSON file and returns a list of channelObj objects.
def readChannel(channels_file_str):
   channels_list = []
   with open(channels_file_str, 'r') as channels_file:
      channels_file_dict = json.load(channels_file)
   for channels_dict in channels_file_dict:
      channels_list.append(channelObj(channels_dict))
   return channels_list


#Function is given a number of arguments, and executes the addToReport function using the list of message objects it created.
def readJSON(json_file_str, users_list, file_str, working_dir_str):
   messages_list = []
   with open(json_file_str, 'r') as json_file:
      json_file_list = json.load(json_file)
   for msg_dict in json_file_list:
      messages_list.append(msgObj(msg_dict, users_list))
   addToReport(messages_list, users_list, file_str, working_dir_str)


#Main function. Main logical structure of the program. It is called by the last two lines of code below.
def slackMain(absolute_directory):
   os.chdir(absolute_directory)
   
   working_dir_str = os.getcwd()
   json_dirs_str = os.listdir()
   file_names_list = ['index.html']
   users_list = readUser('users.json')
   channels_list = readChannel('channels.json')
   
   for file in json_dirs_str:
      if(os.path.isdir(file)):
         file_names_list.append(file + '.html')
   for file in file_names_list:
      createHTML(file, channels_list, users_list, file_names_list)
      print('Creating ' + file + ' file')
   
   for file in json_dirs_str:
      if(os.path.isdir(file)):
         os.chdir(file)
         file_name_str = file + '.html'
         for file in os.listdir():
            for item in os.listdir():
               if '.html' in item:
                  file_name_str = item
            if ".json" in file:
               if "-" in file:
                  readJSON(file, users_list, file_name_str, working_dir_str)
         finalizeReport(file_name_str, file_names_list, working_dir_str)
         os.chdir(working_dir_str)
   
   createIndex(channels_list, file_names_list)
   
   createCSV(file, file_names_list, working_dir_str)
   print('Parsing Complete!')

#This part of the program runs first and calls the slackMain function.
if __name__ == '__SlackMain__':
   slackMain(sys.argv[1:])
