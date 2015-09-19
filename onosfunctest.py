import os
import os.path
import time
import pexpect
import re
import sys

def DownLoadCode():
    print '\033[1;31;40m'
    print "Now loading test codes!Please wait in patient..."
    print "\033[0m"
    os.system("git clone https://github.com/sunyulin/OnosSystemTest.git")
    time.sleep(1)
    os.system("git clone https://gerrit.onosproject.org/onos")
    time.sleep(1)
    print "Done!"

def CleanEnv():
    print '\033[1;31;40m'
    print "Now Cleaning test environment"
    print "\033[0m"
    os.system("sudo apt-get install -y mininet")
    os.system("OnosSystemTest/TestON/bin/cleanup.sh")
    time.sleep(5)
    print "Done!"

def OnosPushKeys(cmd,password):

    print '\033[1;31;40m'
    print "Now Pushing Onos Keys:"+cmd
    print "\033[0m"
    Pushkeys = pexpect.spawn(cmd)
    Result = 0
    while Result != 2:
        Result = Pushkeys.expect(["yes","password",pexpect.EOF,pexpect.TIMEOUT])
        if (Result == 0):
            Pushkeys.sendline("yes")
        if (Result == 1):
            Pushkeys.sendline(password)
        if (Result == 3):
            print("Push keys Error!")
    print "Done!"

def SetEnvVar(masterpass,agentpass):
    print '\033[1;31;40m'
    print "Now Setting test environment"
    print "\033[0m"
    os.system("source onos/tools/dev/bash_profile")
    os.environ["OCT"] = "10.1.0.1"
    os.environ["OC1"] = "10.1.0.50"
    os.environ["OC2"] = "10.1.0.51"
    os.environ["OC3"] = "10.1.0.52"
    os.environ["OCN"] = "10.1.0.53"
    os.environ["OCN2"] = "10.1.0.54"
    os.environ["localhost"] = "10.1.0.1"
    os.system("sudo pip install configobj")
    OnosPushKeys("onos-push-keys 10.1.0.1",masterpass)
    OnosPushKeys("onos-push-keys 10.1.0.50",agentpass)
    OnosPushKeys("onos-push-keys 10.1.0.53",agentpass)
    OnosPushKeys("onos-push-keys 10.1.0.54",agentpass)

def Gensshkey():
    print '\033[1;31;40m'
    print "Now Generating SSH keys..."
    print "\033[0m"
    os.system("rm -rf ~/.ssh/*")
    keysub = pexpect.spawn("ssh-keygen -t rsa")
    Result = 0
    while Result != 2:
        Result = keysub.expect(["Overwrite","Enter",pexpect.EOF,pexpect.TIMEOUT])
        if Result == 0:
            keysub.sendline("y")
        if Result == 1:
            keysub.sendline("\n")
        if Result == 3:
            printf("Generate SSH key failed.")
    print "Done!"

def ChangeOnosName(user,password):
    print '\033[1;31;40m'
    print "Now Changing ONOS name&password"
    print "\033[0m"
    line = open("onos/tools/build/envDefaults",'r').readlines()
    lenall = len(line)-1
    for i in range(lenall):
       if "ONOS_USER=" in line[i]:
           line[i]=line[i].replace("sdn",user)
       if "ONOS_GROUP" in line[i]:
           line[i]=line[i].replace("sdn",user)
       if "ONOS_PWD" in line[i]:
           line[i]=line[i].replace("rocks",password)
    open("onos/tools/build/envDefaults",'w').writelines(line)
    print "Done!"

def ChangeTestCasePara(testcase,user,password):
    print '\033[1;31;40m'
    print "Now Changing " + testcase +  " name&password"
    print "\033[0m"
    filepath = "OnosSystemTest/TestON/tests/" + testcase + "/" + testcase + ".topo"
    line = open(filepath,'r').readlines()
    lenall = len(line)-1
    for i in range(lenall-2):
       if ("localhost" in line[i]) or ("OCT" in line[i]):
           line[i+1]=re.sub(">\w+",">"+user,line[i+1])
           line[i+2]=re.sub(">\w+",">"+password,line[i+2])
       if "OC1" in line [i] \
          or "OC2" in line [i] \
          or "OC3" in line [i] \
          or "OCN" in line [i] \
          or "OCN2" in line[i]:
           line[i+1]=re.sub(">\w+",">root",line[i+1])
           line[i+2]=re.sub(">\w+",">root",line[i+2]) 
    open(filepath,'w').writelines(line) 
    print "Done!"

def RunScript(testname,masterusername,masterpassword):
    ChangeTestCasePara(testname,masterusername,masterpassword)
    runtest = "OnosSystemTest/TestON/bin/cli.py run " + testname
    os.system(runtest)
    print "Done!"

if __name__=="__main__":

    #This is the compass run machine user&pass,you need to modify
    masterusername = "root"
    masterpassword = "root"

    #The config below you don't need to care
    agentusername = "root"
    agentpassword = "root"

    print "Test Begin...."
    ChangeOnosName(agentusername,agentpassword)
    Gensshkey() 
    DownLoadCode()
    CleanEnv()
    SetEnvVar(masterpassword,agentpassword)
    RunScript("FUNCvirNetNB",masterusername,masterpassword)
    RunScript("FUNCovsdbtest",masterusername,masterpassword) 
