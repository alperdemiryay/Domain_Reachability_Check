import pythonping, datetime, time, socket, sqlite3

kontrolEdilecekDomainler = ['www.google.com.tr', 'www.twitter.com', 'www.facebook.com', 'www.instagram.com']

def connectDbAndWriteData(domainListDict, date):
    db = sqlite3.connect('domainCheckDB.sqlite')
    cursor = db.cursor()
    createTableSql = '''CREATE TABLE IF NOT EXISTS domain_check_results (domain_name CHAR, latency_ms INT, date INT);'''
    cursor.execute(createTableSql)
    for domain in domainListDict.keys():
        insertDataSql = '''INSERT INTO domain_check_results VALUES('{}', '{}', '{}')'''.format(domain, str(domainListDict[domain]), date.strftime('%Y%m%d%H%M%S'))
        cursor.execute(insertDataSql)
        db.commit()

def checkHttpConnection(domainList):
    socket.setdefaulttimeout(2)
    domainListDict = {}
    date = datetime.datetime.now()
    for domain in domainList:
        connectionRequired = True
        while connectionRequired:
            retryCounter = 0
            start = time.time()
            domainIp = socket.gethostbyname(domain)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            httpConnectionResult = s.connect_ex((domainIp, 80))
            if (httpConnectionResult == 0) or (retryCounter >= 100):
                end = time.time()
                s.close()
                print('{} domain connection time is: '.format(domain) + str(end - start))
                connectionRequired = False
                domainListDict[domain] = round(float(end-start),3)*1000
            else:
                retryCounter += 1
                s.close()
    pingResult = str(pythonping.ping('8.8.8.8', timeout=1))
    if len(pingResult) >= 50 :
        pingResult = pingResult.split('/')[3].split('.')[0]
    elif 'Request timed out' in pingResult:
        pingResult = '100000'
    else:
        pingResult = '99999'
    print('Google DNS ping result is: ' + pingResult)
    domainListDict['GoogleDNS'] = pingResult
    connectDbAndWriteData(domainListDict, date)


while True:
    checkHttpConnection(kontrolEdilecekDomainler)
    time.sleep(5)