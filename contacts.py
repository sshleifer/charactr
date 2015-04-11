

def getData():
  '''returns a series of <firstname> <lastname> <phonenumber> <phonenumber> strings.'''
  path = "~/Library/Application Support/AddressBook/AddressBook-v22.abcddb"
  ADDRESS_DB = os.path.expanduser(path)
  ad_db = sqlite3.connect(ADDRESS_DB)
  ad_curs = ad_db.cursor()
  adtabs = getTabs(ad_curs)
  query = "SELECT ZSTRINGFORINDEXING FROM ZABCDCONTACTINDEX"
  contact_list = pd.read_sql(query, ad_db)
  return contact_list


def orig_addresses():
  '''Attempt to make table where names can be looked up using phone numbers.'''
  src = os.listdir(os.path.expanduser("~/Library/Application Support/AddressBook/Sources"))[0]
  database = os.path.expanduser(os.path.join("~/Library/Application Support",
    "AddressBook/Sources", src,
    "AddressBook-v22.abcddb"))
  connection = sqlite3.connect(database)
  ad = connection.cursor()
  adtabs = getTabs(ad) #For debugging
  numtab = pd.read_sql("""SELECT * FROM ZABCDPHONENUMBER""", connection)
  nametab = pd.read_sql("""SELECT * FROM ZABCDRECORD""",connection)

  nt = numtab[['ZFULLNUMBER','ZFIRSTNAME','ZLASTNAME']]
  nt.colums=['number','fname','lname']
  return nt

# addresses() takes no parameters and returns a dictionary (nn_map) mapping
# phone numbers to contact names
def addresses():
  contact_list = getData() 
  name_pattern = re.compile("[a-z]* [a-z]*")
  num_pattern = re.compile("[2-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]")
  print adtabs
  # name, number dictionary
  nn_map = {}
  for i in range(2, len(contact_list)):
    # get string
    t = contact_list.ix[i]
    s = t[0]
    print 'HERE' 

    # match name
    m = name_pattern.search(s)
    name = s[m.start():m.end()]
    # match number
    m2 = num_pattern.search(s)
    if m2:
      num = s[m.start():m.end()]
      nn_map[num] = name
    else:
      print "error, number not found"              # should not happen
      continue 
  return nn_map
