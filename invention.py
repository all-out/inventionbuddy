import math
import sys
from urllib.error import URLError, HTTPError

class BlueprintInvention():

	def __init__(self):
		#Load blueprint data into dictionary
		self.blueprint_data = _load_json()
		#Load typeID/name data into dictionary
		self.typeID_name_data = _load_csv()
		#Load name/typeID data into dictionary
		self.name_typeID_data = _load_csv_mirror()
	
	#This will need to be cleaned up
	def tech_two_invention(self):
		#Recieve typeID from input 
		bp_typeID = input('Enter the typeID of the tier 2 blueprint you wish to make \n>> ')
		product_typeID = str(self.blueprint_data[bp_typeID]['activities']['manufacturing']['products'][0]['typeID'])
		bp_mats = self.blueprint_data[bp_typeID]['activities']['manufacturing']['materials']
		#Create required material objects for use in setting price later on
		materials = _init_materials(bp_mats)
		#Create the typeid specific part of the url
		url_text = _create_marketstat_url(bp_mats, product_typeID)
		#Request XML data for materials and product, only returns product price, material prices set in materials dictionary
		productprice = _get_market_data(bp_mats, product_typeID, materials, url_text)
		#Create bp and product objects
		bp = Blueprint(self.typeID_name_data[bp_typeID], bp_mats)
		product = Product(self.typeID_name_data[product_typeID], productprice) 
		#Calculate outcome of invention with each decryptor
		outcomes = _calculate_outcomes(bp)
		#Creates average dictionary and initiates with keys
		averages = _init_averages(outcomes)
		#Amount of case scenarios to run
		_run_scenarios(outcomes, averages, product, materials)
		#Print results
		_print_results(product, averages)

	#Could use a better name
	#This will also need to be cleaned up
	def find_highest_revenue_blueprints(self, materials_owned):
		material_list = _parse_materials(materials_owned)
		materials = _create_material_list(material_list, self.name_typeID_data)
		url_text = _create_marketstat_url_ver2(materials)
		_get_market_data_ver2(materials, url_text)
		##Loop through bp database, checking if materials_owned matches materials for bp
		possible_products = {}
		_match_materials_to_blueprints(possible_products, self.typeID_name_data, self.blueprint_data, materials)
		new_url_text = _create_marketstat_url_ver3(possible_products, self.name_typeID_data)
		_get_product_market_data(possible_products, new_url_text, self.name_typeID_data)
		sorted_list = []
		_create_best_profit_list(sorted_list, possible_products)
		sorted_list.sort(key=lambda x: x.total, reverse=True)
		_print_profit_list(sorted_list)

#Class for the decryptor used to affect probability, max runs, material/time efficiency in invention
class Decryptor():

	def __init__(self, name, prob_multi, max_run_mod, mat_effic, time_effic):
		self.name = name
		self.prob_multi = prob_multi
		self.max_run_mod = max_run_mod
		self.mat_effic = mat_effic
		self.time_effic = time_effic

class Blueprint():

	def __init__(self, name, mats_required, runs=1, prob=34, mat_effic=2, time_effic=4):
		self.name = name
		self.runs = runs
		self.prob = prob
		self.mat_effic = mat_effic
		self.time_effic = time_effic
		self.mats_required = mats_required


	def outcome_bp(self, decryptor):
		new_prob = self.prob * decryptor.prob_multi
		max_run = self.runs + decryptor.max_run_mod
		new_mat_effic = self.mat_effic + decryptor.mat_effic
		new_time_effic = self.time_effic + decryptor.time_effic
		outcome_bp = Blueprint(self.name + " : " + decryptor.name, 
	                self.mats_required, max_run, new_prob, new_mat_effic, new_time_effic)
		return outcome_bp

class Material():

	def __init__(self, typeID, amount=1, name='', cost=0):
		self.typeID = typeID
		self.amount = amount
		self.name = name
		self.cost = cost

	def setprice(self, cost):
		self.cost = int(cost)

class Product():

	def __init__(self, name, typeID='', amount=1, sell_cost=0):
		self.name = name
		self.typeID = typeID
		self.amount = amount
		self.sell_cost = sell_cost

	def setprice(self, sell_cost):
		self.sell_cost = int(sell_cost)

	def calc_total(self):
		 self.total = math.floor((self.sell_cost * self.amount))

#Decryptors used in invention process
_decryptors = (
        Decryptor("Accelerant Decryptor", 1.2, 1, 2, 10),
        Decryptor("Attainment Decryptor", 1.8, 4, -1, 4),
        Decryptor("Augmentation Decryptor", 0.6, 9, -2, 2),
        Decryptor("Optimized Attainment Decryptor", 1.9, 2, 1, -2),
        Decryptor("Optimized Augmentation Decryptor", 0.9, 7, 2, 0),
        Decryptor("Parity Decryptor", 1.5, 3, 1, -2),
        Decryptor("Process Decryptor", 1.1, 0, 3, 6),
        Decryptor("Symmetry Decryptor", 1, 2, 1, 8)
)

###################################################################################
### definitions for tech_two_invention
###################################################################################

#Using the tier 2 blueprint and sell price of the rig to work out the profit
def _calc_profit(materials, product, blueprint, attempts=10):
	mat_cost = 0
	for i in range(0, len(blueprint.mats_required)):
		mat_cost += (math.ceil((blueprint.mats_required[i]['quantity'] * blueprint.runs) * \
			((100 - blueprint.mat_effic) / 100))) * \
			materials[blueprint.mats_required[i]['typeID']].cost
	successful_bps = 0
	from random import randrange
	for i in range(0, attempts):
		if randrange(0, 101) <= blueprint.prob : successful_bps += 1
	profit = ((product.sell_cost * blueprint.runs) * successful_bps) - (mat_cost * successful_bps)
	return profit

def _load_json():
	data = {}
	from json import load
	with open('blueprints.json', 'r') as fp:
		return load(fp)

def _load_csv():
	data = {}
	from csv import reader
	with open('typeids.csv', 'r') as fp:
		reader = reader(fp)
		return {rows[0]:rows[1] for rows in reader}

def _load_csv_mirror():
	data = {}
	from csv import reader
	with open('typeids.csv', 'r') as fp:
		reader = reader(fp)
		return {rows[1]:rows[2] for rows in reader}
	
def _init_materials(the_mats):
	materials = {}
	for mats in the_mats:
		if not mats['typeID'] in materials: 
			materials[mats['typeID']] = Material(mats['typeID'])
	return materials

def _create_marketstat_url(bp_mats, product_typeID=''):
	url_text = ""
	for i in range(0, len(bp_mats)):
		url_text = url_text + "typeid=" + str(bp_mats[i]['typeID']) + "&"
	return url_text + "typeid=" + product_typeID + "&"

def _get_market_data(bp_mats, product_typeID, materials, url_text):
	from urllib.request import urlopen
	with urlopen('http://api.eve-central.com/api/marketstat?' + url_text + 'regionlimit=10000002') as response:
		xml = response.read()
		from xml.etree import ElementTree as ET
		#Set price of each material by finding the typeid in the XML data
		for i in range(0, len(bp_mats)):
			materials[bp_mats[i]['typeID']].setprice(float(ET.fromstring(xml).find('marketstat/type[@id=\'' + \
				str(bp_mats[i]['typeID']) + '\']/sell/min').text))
		#Set product price in the same way
		return float(ET.fromstring(xml).find('marketstat/type[@id=\'' + product_typeID + '\']/sell/min').text)

def _calculate_outcomes(bp):
	outcomes = []
	for index in range(len(_decryptors)):
		outcomes.append(bp.outcome_bp(_decryptors[index]))
	return outcomes

def _init_averages(outcomes):
	averages = {}
	for index in range(len(outcomes)):
		averages[outcomes[index].name] = 0
	return averages

def _run_scenarios(outcomes, averages, product, materials, cycles=100):
	for i in range(0, cycles):
		for index in range(len(outcomes)):
			averages[outcomes[index].name] += _calc_profit(materials, product, outcomes[index])
	_calculate_averages(cycles, averages)

def _calculate_averages(cycles, averages):
	for name in averages:
		averages[name] /= cycles

def _print_results(product, averages):
	print('For creating: ' + product.name + ' \nThe projected profits are as follows:')
	for key, value in averages.items():
		print(key + " : " + "{:,}".format(math.floor(value)))
	input('Press enter to exit.')

###################################################################################
### definitions for find_highest_revenue_blueprints
###################################################################################

def _parse_materials(input_string):
	txt = input_string.split('\n')
	line_split_text = []
	for i in range(len(txt)):
		line_split_text.append(txt[i].split('\t'))
	parsed_text = []
	for i in range(len(line_split_text)):
		for x in range(len(line_split_text[i])):
			if line_split_text[i][x] != '': 
				parsed_text.append(line_split_text[i][x])
	return parsed_text

def _create_material_list(material_list, name_typeID_data):
	materials = {}
	for i in range(int(len(material_list) / 4)):
		materials[name_typeID_data[material_list[(i * 4)]]] = (Material(name_typeID_data[material_list[(i * 4)]], 
			material_list[((i * 4) + 1)], material_list[(i * 4)]))
	return materials

def _contains_correct_keys(value):
	if 'activities' in value:
		if 'manufacturing' in value['activities']:
			if 'materials' in value['activities']['manufacturing']:
				return True
	return False

def _contains_all_materials(bp_mats, materials_owned):
	for i in range(len(bp_mats)):
		if not str(bp_mats[i]['typeID']) in materials_owned:
			return False
	print(bp_mats)
	return True

def _calculate_bp_maxruns(bp_mats, materials_owned):
	max_runs = sys.maxsize
	for i in range(len(bp_mats)):
		runs = int(materials_owned[str(bp_mats[i]['typeID'])].amount) / bp_mats[i]['quantity']
		if runs < max_runs:
			max_runs = int(math.floor(runs))
	print(max_runs)
	return(max_runs)

def _create_marketstat_url_ver2(materials):
	url_text = ""
	for key, value in materials.items():
		url_text = url_text + "typeid=" + value.typeID + "&"
	return url_text

def _create_marketstat_url_ver3(products, data):
	url_text = ""
	for key, value in products.items():
		url_text = url_text + "typeid=" + data[key] + "&"
	return url_text

def _create_marketstat_split_url(products, data, start=0, end=0):
	url_text = "" 
	url_text_two = ""
	product_list = []
	for key, value in products.items():
		product_list.append(value)
	if end == 0:
		end = len(product_list)
	middle = int(math.floor(((end - start) / 2) + start))
	i = 0
	for i in range(start, middle):
			url_text = url_text + "typeid=" + product_list[i].typeID + "&"
	for i in range(middle + 1, end):
			url_text_two = url_text_two + "typeid=" + product_list[i].typeID + "&"
	try:
		_get_market_data_ver3(products, url_text)
		_get_market_data_ver3(products, url_text_two)
	except HTTPError as e:
		print('The server couldn\'t fulfill the request.')
		print('Error code: ', e.code)
		if e.code == 414:
			print("WE NEED TO GO DEEPER")
			_create_marketstat_split_url(products, data, start, middle)
			_create_marketstat_split_url(products, data, middle + 1, end)
	except URLError as e:
	    print('We failed to reach a server.')
	    print('Reason: ', e.reason)
	    sys.exit()
	print('end of the rabbit hole')

def _get_market_data_ver2(materials, url_text):
	from urllib.request import urlopen
	with urlopen('http://api.eve-central.com/api/marketstat?' + url_text + 'regionlimit=10000002') as response:
		xml = response.read()
		from xml.etree import ElementTree as ET
		#Set price of each material by finding the typeid in the XML data
		for key, value in materials.items():
			value.setprice(float(ET.fromstring(xml).find('marketstat/type[@id=\'' + \
				key + '\']/sell/min').text))
		#Set product price in the same way
		return

def _get_market_data_ver3(products, url_text):
	from urllib.request import urlopen
	with urlopen('http://api.eve-central.com/api/marketstat?' + url_text + 'regionlimit=10000002') as response:
		xml = response.read()
		from xml.etree import ElementTree as ET
		#Set price of each material by finding the typeid in the XML data
		for key, value in products.items():
			try:
				value.setprice(float(ET.fromstring(xml).find('marketstat/type[@id=\'' + \
					value.typeID + '\']/sell/min').text))
			except:
				continue
		#Set product price in the same way
		return

def _get_product_market_data(possible_products, new_url_text, name_typeID_data):
	try:
		_get_market_data_ver3(possible_products, new_url_text)
	except HTTPError as e:
	    print('The server couldn\'t fulfill the request.')
	    print('Error code: ', e.code)
	    if e.code == 414:
	    	#Here goes new method of getting urltext and market data
	    	print('WE NEED TO GO DEEPER')
	    	_create_marketstat_split_url(possible_products, name_typeID_data)
	except URLError as e:
	    print('We failed to reach a server.')
	    print('Reason: ', e.reason)

def _match_materials_to_blueprints(possible_products, typeID_name_data, blueprint_data, materials):
	for key, value in blueprint_data.items():
		if _contains_correct_keys(value):
			bp_mats = value['activities']['manufacturing']['materials']
			product_typeID = str(value['activities']['manufacturing']['products'][0]['typeID'])
			if _contains_all_materials(bp_mats, materials):
				#If yes, calculate how much can be made per bp, or if tech 2, 
				#first calculate best decryptor and then how many
				runs = _calculate_bp_maxruns(bp_mats, materials)
				if not runs == 0 :
					possible_products[typeID_name_data[product_typeID]] = \
					Product(typeID_name_data[product_typeID], product_typeID, runs)

def _create_best_profit_list(sorted_list, possible_products):
	for key, value in possible_products.items():
		value.calc_total()
		sorted_list.append(value)

def _print_profit_list(sorted_list):
	for value in sorted_list:
		print(value.name + " : " + "{:,}".format(value.total))