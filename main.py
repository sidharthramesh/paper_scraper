import robobrowser,os,scholarly
import time
import cPickle as pickle
url = 'http://10.10.0.1/24online/webpages/client.jsp'
def check_status():
    br = robobrowser.RoboBrowser()
    br.open(url)
    form=br.get_forms()[0]
    string = form.serialize().to_requests()['params'][22][0]
    if string == 'logout':
        return 1
    if string == 'loginotp':
        return 0
    else:
        return -1
def login():
    if check_status() == 0:
        br = robobrowser.RoboBrowser()
        br.open(url)
        form=br.get_forms()[0]
        form['username']= '150101312' #Change this
        form['password']= 'tornadoalert' #Change this too
        form.serialize()
        br.submit_form(form)
    if check_status() == -1:
        print "error!"
    if check_status() == 1:
        print "Logged in!"
def logout():
    if check_status() == 1:
        br = robobrowser.RoboBrowser()
        br.open(url)
        form=br.get_forms()[0]
        form['mode'] = '193'
        form['isAccessDenied'] = 'False'
        form.serialize()
        br.submit_form(form)
    if check_status() == -1:
        print "error!"
    if check_status() == 0:
        print "Logged out!"
def check_save():
    return 'cites.pkl' in os.listdir('.')
def check_data():
    return 'kmc_data.pkl' in os.listdir('.')
def load_save():
    with open('cites.pkl','rb') as f:
        save = pickle.load(f)
        return save
def load_data():
    with open('kmc_data.pkl','rb') as f:
        save = pickle.load(f)
        return save
def init_save():
    cit_data = {}
    citations = []
    status =[]
    for i in range(len(load_data())):
        citations.append(0)
        status.append(0)

    cit_data['citations'] = citations
    cit_data['status'] = status
    return cit_data
def write_save(object):
    with open('cites.pkl','wb') as f:
        pickle.dump(object,f)
        print "Save complete"
def querry(bibtex):
    return bibtex['title']
def get_citedby(bibtex):
    results=scholarly.search_pubs_query(querry(bibtex))
    first_result=results.next()
    return first_result.citedby
def captcha_test():
    try:
        results=scholarly.search_pubs_query('Einstien')
        first_result=results.next()
        first_result.citedby
    except StopIteration:
        return True
    return False

if check_data():
    papers = load_data()
else:
    print "No data file"

if check_save():
    cit_data = load_save()
    print "Loaded Save"


else:
    print "No save found...Creating one"
    cit_data = init_save()
    write_save(cit_data)

if check_status() == 0:
    print "Not logged in. Logging in..."
    login()
for i in range(len(papers)):

    while cit_data['status'][i] == 0:
        print i+1,'of ',len(papers)
        try:
            cit_data['citations'][i] = get_citedby(papers[i])
            cit_data['status'][i] = 1
        except AttributeError:
            print "No cites on G.S"
            cit_data['citations'][i] = 0
            cit_data['status'][i] = 1
        except StopIteration:
                print "No results found. Running Captcha test..."
                if captcha_test():
                    print "Shit! Google is pissed!"
                    print "Logging out..."
                    logout()
                    time.sleep(3)
                    print "Now logging back in..."
                    login()
                    time.sleep(3)
                    cit_data['status'][i] = 0
                    print "Exiting..."
                    exit()
                else:
                    print "Not robot yet"
                    cit_data['status'][i] = 1
        if i % 5 == 0:
            write_save(cit_data)
