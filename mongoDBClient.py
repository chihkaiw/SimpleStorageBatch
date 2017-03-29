import sys
import pymongo
import json
from bson.objectid import ObjectId
from bson.json_util import dumps


MONGODB_URI = ''
client = pymongo.MongoClient(MONGODB_URI)
db = client.get_default_database()

def update_number_of_storage(belingcompanyID, product_ID, howmany, name):
    product_in_storage = get_product_info(belingcompanyID, product_ID)
    size_of_cursor = len(product_in_storage)

    if size_of_cursor > 0:
         update_old_item_in_storage(belingcompanyID, product_ID, howmany)
         print 'UPDATE_OLD'
    elif size_of_cursor == 0:
        create_new_item_in_storage(belingcompanyID, product_ID, howmany, name)
        print 'CREATE_NEW'
    else:
        print 'ERROR'

def update_old_item_in_storage(belingcompanyID, product_ID, howmany):
    product_storage_number = db['product_storage_number']
    query = {'belingcompanyID': belingcompanyID,'product_ID': product_ID}
    product_storage_number.update(query, {'$set': {'howmany': howmany}})

def create_new_item_in_storage(belingcompanyID, product_ID, howmany, name):
    product_storage_number = db['product_storage_number']
    product_storage_number.insert(get_new_item_Json_Array(belingcompanyID, product_ID, howmany, name))

def get_new_item_Json_Array(belingcompanyID, product_ID, howmany, name):
    result = [{'belingcompanyID':belingcompanyID, 'product_ID':product_ID, 'howmany': howmany, 'name': name}]
    return result

def get_product_info(belingcompanyID, product_ID):
    product_storage_number = db['product_storage_number']
    cursor = product_storage_number.find({'belingcompanyID':belingcompanyID,'product_ID':product_ID})
    #for doc in cursor:
        #print 'PRODUCT: ', doc

    return get_array_from_JSON_String(dumps(cursor))

def get_company_list():
    companyList_Collection = db['company_list']
    c_id = []
    c_name = []
    for post in companyList_Collection.find():
        c_id.append(post['company_id'])
        c_name.append(post['company_name'])
    
    return c_id
   
def get_company_info_by_company_id(company_id):
    companyList_Collection = db['company_list']
    company_info = companyList_Collection.find_one({'company_id': company_id})

    return company_info

def create_new_company(company_id, company_name):
    product_storage_number = db['company_list']
    product_storage_number.insert(get_new_company_Json_Array(company_id, company_name))

def get_new_company_Json_Array(company_id, company_name):
    result = [{'company_id':company_id, 'company_name':company_name}]
    return result

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

def close_connection():
    client.close()

#def update_company_list():


#update_number_of_storage(1, 999, 4000, 'A\u578b\u63a5\u6536\u5668\u5929\u7dda\u9ed1\u8272')
#update_old_item_in_storage('57e2bc0c44dce8036dc24152', 2000)
#create_new_item_in_storage(1, 123, 4000, 'A\u578b\u63a5\u6536\u5668\u5929\u7dda\u9ed1\u8272')
#print 'OK'
