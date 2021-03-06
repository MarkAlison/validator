import subprocess,re

# Clean up output from first scan results
cleanUp = re.compile(r"&gt;|&lt;|(\[0;33m)|(\[0;31m)|<|>|-|\/bin.*|\"|\'|.*.\[[0-9]{1,2}m|\^\[")

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Plugin Dictionary {Plugin{Regex,command}} key/(value,value) pairs
pluginList = {
    # PHP vulnerabilities
    '48244': {'regex': 'PHP', 'command': "''nikto --host {1} --port {0} -maxtime {2}''"},  # PHP Multiple Vulns
    '51139': {'regex': 'PHP', 'command': "''nikto --host {1} --port {0} -maxtime {2}''"},  # PHP Multiple Vulns 2
    '39480': {'regex': 'PHP', 'command': "''nikto --host {1} --port {0} -maxtime {2}''"},  # PHP Multiple Vulns 3
    '41014': {'regex': 'PHP', 'command': "''nikto --host {1} --port {0} -maxtime {2}''"},  # PHP Multiple Vulns 4
    '43351': {'regex': 'PHP', 'command': "''nikto --host {1} --port {0} -maxtime {2}''"},  # PHP Multiple Vulns 5
    '35067': {'regex': 'PHP', 'command': "''nikto --host {1} --port {0} -maxtime {2}''"},  # PHP Multiple Vulns 6
    '35750': {'regex': 'PHP', 'command': "''nikto --host {1} --port {0} -maxtime {2}''"},  # PHP Multiple Vulns 7
    '58966': {'regex': 'PHP', 'command': "''nikto --host {1} --port {0} -maxtime {2}''"},  # PHP Multiple Vulns 8
    '44921': {'regex': 'PHP', 'command': "''nikto --host {1} --port {0} -maxtime {2}''"},  # PHP Multiple Vulns 9
    '57537': {'regex': 'PHP', 'command': "''nikto --host {1} --port {0} -maxtime {2}''"},  # PHP Multiple Vulns 10
    '35043': {'regex': 'PHP', 'command': "''nikto --host {1} --port {0} -maxtime {2}''"},  # PHP Multiple Vulns 11
    '73289': {'regex': 'PHP', 'command': "''nikto --host {1} --port {0} -maxtime {2}''"},  # PHP Rshutdown Bypass
    '58987': {'regex': 'PHP', 'command': "''nikto --host {1} --port {0} -maxtime {2}''"},  # PHP Unsupported Version
    '58988': {'regex': 'PHP', 'command': "''nikto --host {1} --port {0} -maxtime {2}''"},  # PHP Query String CE
    '51439': {'regex': 'PHP', 'command': "''nikto --host {1} --port {0} -maxtime {2}''"},  # PHP Dub Conversion DOS

    # NTP Vulnerabilities
    '71783': {'regex': '(Vulnerable)','command': "''msfconsole -q -x 'use auxiliary/scanner/ntp/ntp_monlist;set rhosts {1};color false;run;exit -y'''",'UDPcommand': "''msfconsole -q -x 'use auxiliary/scanner/ntp/ntp_monlist;set rhosts {1};color false;run;exit -y'''"},  # VNC Default Password 'password'

    # VNC Vulnerabilities
    '61708': {'regex': '(LOGIN\sSUCCESSFUL)','command': "''msfconsole -q -x 'use auxiliary/scanner/vnc/vnc_login;set rhosts {1};set rport {0};set password password;color false;run;exit -y'''"},# VNC Default Password 'password'

    # ESXi Vulnerabilities
    '92949': {'regex': '(Identified.*.ESXi)', 'command': "''msfconsole -q -x 'use auxiliary/scanner/vmware/esx_firngerprint;set rhosts {1};color false;run;exit -y'''"},  # ESXi Version
    '81085': {'regex': '(Identified.*.ESXi)','command': "''msfconsole -q -x 'use auxiliary/scanner/vmware/esx_firngerprint;set rhosts {1};color false;run;exit -y'''"},  # ESXi Poodle
    '87942': {'regex': '(Identified.*.ESXi)','command': "''msfconsole -q -x 'use auxiliary/scanner/vmware/esx_firngerprint;set rhosts {1};color false;run;exit -y'''"},  # ESXi Guest Privesc
    '88906': {'regex': '(Identified.*.ESXi)','command': "''msfconsole -q -x 'use auxiliary/scanner/vmware/esx_firngerprint;set rhosts {1};color false;run;exit -y'''"},  # ESXi DNS Resolver
    '86947': {'regex': '(Identified.*.ESXi)','command': "''msfconsole -q -x 'use auxiliary/scanner/vmware/esx_firngerprint;set rhosts {1};color false;run;exit -y'''"},  # ESXi 5.5 RCE

    # SMB Vulnerabilities
    '57608': {'regex': 'message_signing:\s(disabled)','command': "''nmap --script=smb-security-mode -p{0} {1} & sleep {2};kill $!''",'UDPcommand': "''nmap -sU --script=smb-security-mode -p{0} {1} & sleep {2};kill $!''"}, # SMB Signing Disabled
    '42256': {'regex': '(nfs-showmount:)', 'command': "''nmap --script=nfs-showmount {1} & sleep {2};kill $!''"}, # NSF Shares World Readable
    '42411': {'regex': '(nfs-showmount:)', 'command': "''nmap --script=nfs-showmount {1} & sleep {2};kill $!''"}, # SMB Shares Unprivileged Access
    '26920': {'regex': '(allows\ssessions)', 'command': "''enum4linux {1} & sleep {2};kill $!''"}, # SMB Null Sessions

    # DNS Vulnerabilities
    '12217': {'regex': 'dns-cache-snoop:\s([1-9]+)\s','command': "''nmap --script=dns-cache-snoop -p{0} {1} & sleep {2};kill $!''",'UDPcommand': "''nmap -sU --script=dns-cache-snoop -p{0} {1} & sleep {2};kill $!''"},  # DNS Server allows cache snooping

    # MS Vulnerabilities
    '34477': {'regex': '(VULNERABLE)\s','command':"''nmap --script=smb-vuln-ms08-067 -p{0} {1} & sleep {2};kill $!''"},  # MS08-067
    '97833': {'regex': '(likely\sVULNERABLE)', 'command': "''msfconsole -q -x 'use auxiliary/scanner/smb/smb_ms17_010;set rhosts {1};color false;run;exit -y'''"}, # MS17-010
    '57690': {'regex': '(WEAK_RDP_ENCRYPTION_SUPPORTED)\s','command':"''perl rdp-sec-check/rdp-sec-check.pl {1} & sleep {2};kill $!''"},  # Terminal Services- Medium or Low
    '30218': {'regex': '(FIPS_SUPPORTED_BUT_NOT_MANDATED)\s','command': "''perl rdp-sec-check/rdp-sec-check.pl {1} & sleep {2};kill $!''"},# Not FIPS Compliant
    '13818': {'regex': '(SSL_SUPPORTED_BUT_NOT_MANDATED_MITM)\s','command': "''perl rdp-sec-check/rdp-sec-check.pl {1} & sleep {2};kill $!''"},  # Not FIPS Compliant
    '58453': {'regex': '(NLA_SUPPORTED_BUT_NOT_MANDATED_DOS)\s','command': "''perl rdp-sec-check/rdp-sec-check.pl {1} & sleep {2};kill $!''"},  # Not NLA Only

    # SSH Vulnerabilities
    '90317': {'regex': 'arcfour','command':"''nmap --script=ssh2-enum-algos -p{0} {1} & sleep {2};kill $!''"},  # Weak SSH Algorithms
    '70658': {'regex': 'cbc','command':"''nmap --script=ssh2-enum-algos -p{0} {1} & sleep {2};kill $!''"},  # CBC Mode Ciphers Enabled
    '71049': {'regex': 'hmac','command':"''nmap --script=ssh2-enum-algos -p{0} {1} & sleep {2};kill $!''"},  # Weak MAC Algorithms Enabled

    ## Dropbear;
    '93650': {'regex': 'dropbear', 'command': "''nmap -A -p{0} {1} & sleep {2};kill $!''"}, # DropBear SSH - Version Based
    '70545': {'regex': 'dropbear', 'command': "''nmap -A -p{0} {1} & sleep {2};kill $!''"}, # DropBear SSH - Version Based 2
    '58183': {'regex': 'dropbear', 'command': "''nmap -A -p{0} {1} & sleep {2};kill $!''"}, # DropBear SSH - UAF RCE

    ## OpenSSH
    '86122': {'regex': 'OpenSSH', 'command': "''nmap -A -p{0} {1} & sleep {2};kill $!''"},  # OpenSSH MaxAuthTries Bypass
    '44076': {'regex': 'OpenSSH', 'command': "''nmap -A -p{0} {1} & sleep {2};kill $!''"},  # OpenSSH SCP injection
    '10802': {'regex': 'OpenSSH', 'command': "''nmap -A -p{0} {1} & sleep {2};kill $!''"},  # OpenSSH Multiple Flaws
    '10823': {'regex': 'OpenSSH', 'command': "''nmap -A -p{0} {1} & sleep {2};kill $!''"},  # OpenSSH Multiple Vulnerabilities
    '10883': {'regex': 'OpenSSH', 'command': "''nmap -A -p{0} {1} & sleep {2};kill $!''"},  # OpenSSH Off by 1 Privesc
    '44072': {'regex': 'OpenSSH', 'command': "''nmap -A -p{0} {1} & sleep {2};kill $!''"},  # OpenSSH Netgroup Auth bypass
    '11031': {'regex': 'OpenSSH', 'command': "''nmap -A -p{0} {1} & sleep {2};kill $!''"},  # OpenSSH Multiple overflows
    '17702': {'regex': 'OpenSSH', 'command': "''nmap -A -p{0} {1} & sleep {2};kill $!''"},  # OpenSSH Multiple vulns 2
    '11712': {'regex': 'OpenSSH', 'command': "''nmap -A -p{0} {1} & sleep {2};kill $!''"},  # OpenSSH Reverse DNS Bypass
    '11837': {'regex': 'OpenSSH', 'command': "''nmap -A -p{0} {1} & sleep {2};kill $!''"},  # OpenSSH Multiple vulns 3
    '44075': {'regex': 'OpenSSH', 'command': "''nmap -A -p{0} {1} & sleep {2};kill $!''"},  # OpenSSH Host info disclosure
    '19592': {'regex': 'OpenSSH', 'command': "''nmap -A -p{0} {1} & sleep {2};kill $!''"},  # OpenSSH Multiple vulns 4
    '44077': {'regex': 'OpenSSH', 'command': "''nmap -A -p{0} {1} & sleep {2};kill $!''"},  # OpenSSH Multiple vulns 5
    '44078': {'regex': 'OpenSSH', 'command': "''nmap -A -p{0} {1} & sleep {2};kill $!''"},  # OpenSSH Cookie Bypass
    '44079': {'regex': 'OpenSSH', 'command': "''nmap -A -p{0} {1} & sleep {2};kill $!''"},  # OpenSSH Force Command Bypass
    '44065': {'regex': 'OpenSSH', 'command': "''nmap -A -p{0} {1} & sleep {2};kill $!''"},  # OpenSSH CBC Disclosure
    '10954': {'regex': 'OpenSSH', 'command': "''nmap -A -p{0} {1} & sleep {2};kill $!''"},  # OpenSSH Token Overflow
    '44073': {'regex': 'OpenSSH', 'command': "''nmap -A -p{0} {1} & sleep {2};kill $!''"},  # OpenSSH OpenPAM DOS
    '31737': {'regex': 'OpenSSH', 'command': "''nmap -A -p{0} {1} & sleep {2};kill $!''"},  # OpenSSH X11 Hijacking
    '44080': {'regex': 'OpenSSH', 'command': "''nmap -A -p{0} {1} & sleep {2};kill $!''"},  # OpenSSH X11 Forward Hijacking
    '44074': {'regex': 'OpenSSH', 'command': "''nmap -A -p{0} {1} & sleep {2};kill $!''"},  # OpenSSH Portable Multiple Vulns
    '53841': {'regex': 'OpenSSH', 'command': "''nmap -A -p{0} {1} & sleep {2};kill $!''"},  # OpenSSH Portable Info Disclosure


    # SSL/TLS Vulnerabilities
    '57582': {'regex': 'self-signed\s(\(NOT ok\))|NOT\sok\s(\(self signed\))|(self-signed)|self\ssigned|selfsigned','command':"''./testssl.sh/testssl.sh --quiet --color 0 -S {1}:{0} & sleep {2};kill $!''"},  # Self Signed Certificate
    '51192': {'regex': 'self-signed\s(\(NOT ok\))|NOT\sok\s(\(self signed\))|(self-signed)|self\ssigned|selfsigned|expired\!','command':"''./testssl.sh/testssl.sh --quiet --color 0 -S {1}:{0} & sleep {2};kill $!''"},  # Untrusted Certificate
    '45411': {'regex': 'self-signed\s(\(NOT ok\))|NOT\sok\s(\(self signed\))|(self-signed)|self\ssigned|selfsigned','command':"''./testssl.sh/testssl.sh --quiet --color 0 -S {1}:{0} & sleep {2};kill $!''"},  # Signed with wrong Hostname
    '15901': {'regex': '(expired\!)','command': "''./testssl.sh/testssl.sh --quiet --color 0 -S {1}:{0} & sleep {2};kill $!''"}, # Expired Certificate
    '20007': {'regex': 'SSLv3\s+offered\s\(NOT\sok\)|SSLv2\s+offered\s\(NOT\sok\)','command':"''./testssl.sh/testssl.sh --quiet --color 0 -p {1}:{0} & sleep {2};kill $!''"},  # SSLv2 or SSLv3
    '89058': {'regex': '[vV][uU][lL][nN][eE][rR][aA][bB][lL][eE]\s(\(NOT\sok\))','command':"''./testssl.sh/testssl.sh --quiet --color 0 -D {1}:{0} & sleep {2};kill $!''"},  # SSL Drown
    '78479': {'regex': '[vV][uU][lL][nN][eE][rR][aA][bB][lL][eE]\s(\(NOT\sok\))','command':"''./testssl.sh/testssl.sh --quiet --color 0 -O {1}:{0} & sleep {2};kill $!''"},  # SSL Poodle
    '80035': {'regex': '[vV][uU][lL][nN][eE][rR][aA][bB][lL][eE]\s(\(NOT\sok\))','command':"''./testssl.sh/testssl.sh --quiet --color 0 -O {1}:{0} & sleep {2};kill $!''"},  # SSL Poodle 2
    '35291': {'regex': 'SHA1\swith\sRSA|MD5|MD4|MD2','command':"''./testssl.sh/testssl.sh --quiet --color 0 -S {1}:{0} & sleep {2};kill $!''"},  # Weak Signature Algorithms
    '83738': {'regex': '[vV][uU][lL][nN][eE][rR][aA][bB][lL][eE]\s(\(NOT\sok\))','command':"''./testssl.sh/testssl.sh --quiet --color 0 -J {1}:{0} & sleep {2};kill $!''"},  # Logjam
    '83875': {'regex': '[vV][uU][lL][nN][eE][rR][aA][bB][lL][eE]\s(\(NOT\sok\))','command':"''./testssl.sh/testssl.sh --quiet --color 0 -J {1}:{0} & sleep {2};kill $!''"},  # Logjam 2
    '81606': {'regex': '[vV][uU][lL][nN][eE][rR][aA][bB][lL][eE]\s(\(NOT\sok\))','command':"''./testssl.sh/testssl.sh --quiet --color 0 -F {1}:{0} & sleep {2};kill $!''"},  # SSL Freak
    '65821': {'regex': '[vV][uU][lL][nN][eE][rR][aA][bB][lL][eE]\s(\(NOT\sok\))','command':"''./testssl.sh/testssl.sh --quiet --color 0 -4 {1}:{0} & sleep {2};kill $!''"},  # RC4
    '62565': {'regex': '[vV][uU][lL][nN][eE][rR][aA][bB][lL][eE]\s(\(NOT\sok\))','command':"''./testssl.sh/testssl.sh --quiet --color 0 -C {1}:{0} & sleep {2};kill $!''"},  # TLS Crime
    '73412': {'regex': '[vV][uU][lL][nN][eE][rR][aA][bB][lL][eE]\s(\(NOT\sok\))','command':"''./testssl.sh/testssl.sh --quiet --color 0 -B {1}:{0} & sleep {2};kill $!''"},  # OpenSSL Heartbleed
    '77200': {'regex': '[vV][uU][lL][nN][eE][rR][aA][bB][lL][eE]\s\(NOT\sok\)','command':"''./testssl.sh/testssl.sh --quiet --color 0 -I {0}:{1} & sleep {2};kill $!''"},  # OpenSSL CCS

    # Misc Vulnerabilities
    '25220': {'regex': 'tcpts=([1-9][0-9]*)','command':"''hping3 {1} -p {0} -S --tcp-timestamp -c 1 & sleep {2};kill $!''"},  # TCP Timestamp Response
    '41028': {'regex': '[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}','command':"''onesixtyone {1} public & sleep {2};kill $!''",'UDPcommand': "''onesixtyone {1} public & sleep {2};kill $!''"},  # SNMP Public Community String
    '10264': {'regex': '[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}','command':"''onesixtyone {1} public & sleep {2};kill $!''",'UDPcommand': "''onesixtyone {1} public & sleep {2};kill $!''"},  # SNMP Public Community String 2
    '80101': {'regex': '(Hash\sfound)','command': "''msfconsole -q -x 'use auxiliary/scanner/ipmi/ipmi_dumphashes;set rhosts {1};color false;run;exit -y'''",'UDPcommand': "''msfconsole -q -x 'use auxiliary/scanner/ipmi/ipmi_dumphashes;set rhosts {1};color false;run;exit -y'''"},# IPMI Hash disclosure
    '11213': {'regex': 'TRACE\sis\s(enabled)', 'command': "''nmap --script=http-trace -p{0} {1} & sleep {2};kill $!''"}, # HTTP TRACE
    ## 88098 NEEDS REVIEW
    '88098': {'regex': '[eE][tT]ag:','command':"''curl --insecure -I https://{0}:{1} & sleep {2};kill $!''"},  # Etag Headers Enabled
}


# Create an XML SubElement with selected text inside
def SubElementWithText(parent, tag, text):
    attrib = {}
    element = parent.makeelement(tag, attrib)
    parent.append(element)
    element.text = text
    return element


# Finding output control
def match(issue,regex,output,tag,verbose):
    pattern = re.compile('.*{}.*'.format(regex))
    issue_match = re.findall(pattern, output)
    plug_out = issue.findall('plugin_output')
    # If verbose then all plugin output will be printed to the screen
    if verbose:
        print bcolors.OKBLUE + "Output for issue, " + issue.get('pluginName') + ":" + bcolors.ENDC
        print output
    if issue_match:
        # Checking if Nessus plugin output already exists, if so, replace it! If not create a new plugin_output.
        if plug_out:
            for plug in plug_out:
                plug.text = output
        else:
            SubElementWithText(issue, 'plugin_output', output)
        print bcolors.FAIL + bcolors.BOLD + "Host is VULNERABLE to issue: " + issue.get('pluginName') + bcolors.ENDC
    else:
        print bcolors.OKGREEN + bcolors.BOLD + "Host NOT vulnerable to issue: " + issue.get('pluginName') + bcolors.ENDC
        if tag:
            print bcolors.WARNING + bcolors.BOLD + "Tagging as FALSE POSITIVE" + bcolors.ENDC
            if plug_out:
                for plug in plug_out:
                    plug.text = 'FALSE POSITIVE'
        else:
            SubElementWithText(issue, 'plug_out', 'FALSE POSITIVE')


# Initialize Finding check
def findingCheck(issue,pattern,cmd,ipaddress,port,timeout,tag,verbose):
    prep = cmd.format(str(port),str(ipaddress),str(timeout))
    command = subprocess.Popen(prep, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    output, err = command.communicate()
    output1 = re.sub(cleanUp, '', str(output))
    match(issue,pattern,output1,tag,verbose)


