import dropbox
import requests
import json
from mongoDBClient import update_number_of_storage, get_company_list, create_new_company, get_product_number_by_companyID_and_productID


home_address_name = '/simple storage JD'
product_list_name = 'product_list.txt'
company_list_name = 'company_list.txt'
slash = '/'
text_file_extension ='.txt'
companyList_array = None
productList_array = None
dbx = None

def get_file_content(file_path):
	try:
		company_list = requests.get(get_temporary_file_preview_url_by_path(file_path))
		company_list_content = company_list.content
		
		return company_list_content
	except Exception as e:
		return None


def get_temporary_file_preview_url_by_path(file_path):

	temporary_link_all = dbx.files_get_temporary_link(file_path)
	temporary_link = temporary_link_all.link
	
	return temporary_link

def set_Valid_JSON_Array_Format(rawDataFromDB):
	if rawDataFromDB is None:
		return '[]'
	else:
		rawDataFromDB = rawDataFromDB.replace('{},', '')
		rawDataFromDB = rawDataFromDB[:-1]

		return '['+rawDataFromDB+']'


def get_array_from_JSON_String(JSON_string):
	while True:
	    try:
	        normal_array=json.loads(JSON_string)   # try to parse...
	        break                    # parsing worked -> exit loop
	    except Exception as e:
	        # "Expecting , delimiter: line 34 column 54 (char 1158)"
	        # position of unexpected character after '"'
	        unexp = int(re.findall(r'\(char (\d+)\)', str(e))[0])
	        # position of unescaped '"' before that
	        unesc = s.rfind(r'"', 0, unexp)
	        s = s[:unesc] + r'\"' + s[unesc+1:]
	        # position of correspondig closing '"' (+2 for inserted '\')
	        closg = s.find(r'"', unesc + 2)
	        s = s[:closg] + r'\"' + s[closg+1:]

	return normal_array

def sync_work(product_list_array, company_name):
	global text_file_extension
	global home_address_name
	global slash
	json_size = len(product_list_array)

	for i in range(0, json_size, +1):
		product_detail_file_path = home_address_name+slash+company_name+slash+product_list_array[i]['name']+text_file_extension
		number_in_storage = get_last_update_storage_number_in_log(product_detail_file_path)

		belingcompanyID = product_list_array[i]['belingcompanyID']
		product_ID = product_list_array[i]['ID']
		name = product_list_array[i]['name']

		if(is_DB_need_to_update(belingcompanyID,product_ID,number_in_storage, name)):
			update_number_of_storage(belingcompanyID, product_ID, number_in_storage, name)
			print '##############################'
			print name + ' need to update ' + number_in_storage
			print '##############################'
	
def get_last_update_storage_number_in_log(product_detail_file_path):
	product_detail_raw = get_file_content(product_detail_file_path)
	product_detail_array = get_array_from_JSON_String(set_Valid_JSON_Array_Format(product_detail_raw))

	json_size = len(product_detail_array)
	return product_detail_array[json_size-1]['howmany']

def is_DB_need_to_update(belingcompanyID, product_ID, number_in_storage, name):
	number = get_product_number_by_companyID_and_productID(belingcompanyID, product_ID, name)
	if number is None:
		return True
	elif number is "Duplicate":
		return True
	else:
		if number != number_in_storage:
			return True
		else:
			return False

def sync_storage_number_between_log_and_mongoDB(company_name):
	print '##########################################################################################'
	print company_name
	
	global home_address_name
	global slash
	global product_list_name

	product_list_file_path = home_address_name+slash+company_name+slash+product_list_name
	
	#print '##### '+product_list_file_path

	product_list_raw = get_file_content(product_list_file_path)
	if product_list_raw is not None:
		product_list_array = get_array_from_JSON_String(set_Valid_JSON_Array_Format(product_list_raw))
		sync_work(product_list_array,company_name)

def check_Company_List(companyList_array):
	company_list_size_in_dropbox = len(companyList_array)
	companyList_array_from_MongoDB = get_company_list()
	company_list_size_in_MongoDB = len(companyList_array_from_MongoDB)

	if company_list_size_in_dropbox == company_list_size_in_MongoDB:
		print "# 5-1. Check Company List: Up to date, NO NEED TO SYNCHRONIZE"
	else:
		print "# 5-1. Check Company List: It is different, NEED TO SYNCHRONIZE"
		sync_company_list(companyList_array, companyList_array_from_MongoDB)

def sync_company_list(companyList_array, companyList_array_from_MongoDB):
	company_list_size_in_dropbox = len(companyList_array)
	company_list_size_in_MongoDB = len(companyList_array_from_MongoDB)

	count = company_list_size_in_MongoDB
	while count < company_list_size_in_dropbox:
		dropbox_company = companyList_array[count]
		create_new_company(dropbox_company['ID'], dropbox_company['name'])
		#print dropbox_company['ID']
		#print dropbox_company['name']
		count += 1 


def storage_number_sync_main_job():
	global home_address_name
	global slash
	global product_list_name
	global company_list_name
	global companyList_array
	global dbx

	STG = ''
	PROD = ''
	print '# 1. Start DropBox'
	dbx=dropbox.Dropbox(PROD)

	print '# 2. Get company list in String'
	companyList_string = get_file_content(home_address_name+slash+company_list_name)
	print '# 3. Format String of company list into JSON'
	companyList_in_JSON_string = set_Valid_JSON_Array_Format(companyList_string)
	print '# 4. Convert JSON Array into Array'
	companyList_array = get_array_from_JSON_String(companyList_in_JSON_string)
	json_size = len(companyList_array)
	print '# 5. Check Company List'
	check_Company_List(companyList_array)

	print '# 6. Get Product list by company name'
	for i in range(0, json_size, +1):
		sync_storage_number_between_log_and_mongoDB(companyList_array[i]['name'])
