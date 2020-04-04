#!/us/bin/python
import os
import sys
from pathlib import Path
import subprocess
try:    import argparse
except: print('argparse required, run: pip install argparse');    sys.exit(1)
import ftplib
import time

version    =    "0.1"


#---------------------------------------------------------------------------    
def main():
    argument_parser =   argparse.ArgumentParser(usage=None,add_help=False)
    argument_parser.add_argument('-h','--help'                ,action='store_true',default=False                 ,dest='help'      ,required=False  )
    argument_parser.add_argument('-v','--version'             ,action='store_true',default=False                 ,dest='version'   ,required=False  )
    argument_parser.add_argument('-d','--debug'               ,action='store_true',default=False                 ,dest='debug'     ,required=False  )
    argument_parser.add_argument('-t','--target'              ,action='store'     ,default=None                  ,dest='target'    ,required=True   )
    argument_parser.add_argument('-u','--user'                ,action='store'     ,default=None                  ,dest='user'      ,required=False  )
    argument_parser.add_argument('-p','--password'            ,action='store'     ,default=None                  ,dest='password'  ,required=False  )
    argument_parser.add_argument('-f','--destination-folder'  ,action='store'     ,default=None                  ,dest='folder'    ,required=True   )
    
    argument_parser_result      =   argument_parser.parse_args()
    option_help                 =   argument_parser_result.help
    option_version              =   argument_parser_result.version
    debug                       =   argument_parser_result.debug
    target                      =   argument_parser_result.target
    user                        =   argument_parser_result.user
    password                    =   argument_parser_result.password
    destination_folder          =   argument_parser_result.folder

    if(option_version):
        print(version)
        sys.exit(0)
    elif(option_help):
        print_usage()
        sys.exit(0)
    else:
        if(user==None):     user        =   'anonymous'
        if(password==None): password    =   ''
        #create destination folder if it does not exist
        if(destination_folder!=None):
            create_folder_if_not_exists(destination_folder)
        ftp_handle  =   ftplib.FTP(target)
        ftp_handle.login(user, password)

        seen_objects    =   []
        downloadFiles(ftp_handle,'/',destination_folder,seen_objects,debug)
        seen_objects.sort(key=lambda tup: tup[1])
        for i in seen_objects:
            if(i[0]=='D'):  print(i[0]+' '+i[1])
            else:           print(' '+' '+i[1])
        print('#DONE')
#---------------------------------------------------------------------------    
def print_usage():
    result    =    "ftpdump.py"
    result    +=    "-t|--target             :  specify target (hostname or ip)"
    result    +=    "-f|--destination-folder :  Specify absolute folder path to be dumped in"
    result    +=    "-u|--user               :  Optional. Specify user. anoymous if not specified"
    result    +=    "-p|--password           :  Optional. Specify password (yes, nice 'n clear in your history!). Empty if not specified"
    result    +=    "-h|--help               :  Prints this help"
    result    +=    "-v|--version            :  Prints version"
    result    +=    "-d|--debug              :  Prints process traces"
    print(result)
#---------------------------------------------------------------------------    
def downloadFiles(ftp_handle,path, destination,seen_objects,debug):
    try:
        ftp_handle.cwd(path)
        os.chdir(destination)
        create_folder_if_not_exists(destination[0:len(destination)-1] + path)
        if(debug):  print("#D " + path)
        seen_objects.append(("D",path))
    except OSError:     
        pass
    except ftplib.error_perm:       
        print("ERROR: could not chdir to " + path)
        print('ABORTING!')
        sys.exit(1)
    
    filelist=ftp_handle.nlst()
    for file_or_dir in filelist:
        time.sleep(0.05)
        try:
            #cwd
            ftp_handle.cwd(path + file_or_dir + "/")          
            downloadFiles(ftp_handle,path+file_or_dir+"/",destination,seen_objects,debug)
        except ftplib.error_perm:
            #hack! if cwd failed, then, it's a file!!!
            new_chdir   =   destination[0:len(destination)-1] + path
            os.chdir(new_chdir)
            try:
                with open(new_chdir+'/'+file_or_dir,'wb') as fp:
                    ftp_handle.retrbinary('RETR '+file_or_dir , fp.write)
                if(debug):  print("#  " + path+file_or_dir)
                seen_objects.append(("f",path+file_or_dir))
            except Exception as e:
                print("#Error: could not download " + path+file_or_dir)
                print(str(e))
    return
#---------------------------------------------------------------------------    
def create_folder_if_not_exists(absolute_path):
    fd = Path(absolute_path)
    if(not fd.is_dir()):
        os.mkdir(absolute_path)
#---------------------------------------------------------------------------    
if(__name__ == '__main__'):
    main()
#---------------------------------------------------------------------------    
    
    
