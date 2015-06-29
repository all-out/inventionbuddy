import math
import random
import json
import urllib.request
import csv

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

	def __init__(self, typeid, cost=0):
		self.typeid = typeid
		self.cost = cost

	def setprice(self, cost):
		self.cost = int(cost)

class Product():

	def __init__(self, name, sell_cost):
		self.name = name
		self.sell_cost = sell_cost

#Using the tier 2 blueprint and sell price of the rig to work out the profit
def calc_profit(product, blueprint, attempts=10):
	mat_cost = 0
	for i in range(0, len(blueprint.mats_required)):
		mat_cost += (math.ceil((blueprint.mats_required[i]['quantity'] * blueprint.runs) * ((100 - blueprint.mat_effic) / 100))) * materials[blueprint.mats_required[i]['typeID']].cost

	successful_bps = 0
	for i in range(0, attempts):
		if random.randrange(0, 101) <= blueprint.prob : successful_bps += 1
	profit = ((product.sell_cost * blueprint.runs) * successful_bps) - (mat_cost * successful_bps)
	return profit

def load_json():
	data = {}
	with open('blueprints.json', 'r') as fp:
		return json.load(fp)

def load_csv():
	data = {}
	with open('typeids.csv', 'r') as fp:
		reader = csv.reader(fp)
		return {rows[0]:rows[1] for rows in reader}
	
def init_materials(the_mats):
	materials = {}
	for mats in the_mats:
		if not mats['typeID'] in materials: 
			materials[mats['typeID']] = Material(mats['typeID'])
	return materials

def create_marketstat_url():
	text = ""
	for i in range(0, len(bp_mats)):
		text = text + "typeid=" + str(bp_mats[i]['typeID']) + "&"
	return text + "typeid=" + product_typeID + "&"

def get_market_data():
	with urllib.request.urlopen('http://api.eve-central.com/api/marketstat?' + text + 'regionlimit=10000002') as response:
		xml = response.read()
		from xml.etree import ElementTree as ET
		#Set price of each material by finding the typeid in the XML data
		for i in range(0, len(bp_mats)):
			materials[bp_mats[i]['typeID']].setprice(float(ET.fromstring(xml).find('marketstat/type[@id=\'' + str(bp_mats[i]['typeID']) + '\']/sell/min').text))
		#Set product price in the same way
		return float(ET.fromstring(xml).find('marketstat/type[@id=\'' + product_typeID + '\']/sell/min').text)

def calculate_outcomes():
	outcomes = []
	for index in range(len(decryptors)):
		outcomes.append(bp.outcome_bp(decryptors[index]))
	return outcomes

def init_averages():
	averages = {}
	for index in range(len(outcomes)):
		averages[outcomes[index].name] = 0
	return averages

def run_scenarios(cycles=100):
	for i in range(0, cycles):
		for index in range(len(outcomes)):
			averages[outcomes[index].name] += calc_profit(product, outcomes[index])
	calculate_averages(cycles)

def calculate_averages(cycles):
	for name in averages:
		averages[name] /= cycles

def print_results():
	print('For creating: ' + product.name + ' \nThe projected profits are as follows:')
	for key, value in averages.items():
		print(key + " : " + "{:,}".format(math.floor(value)))
	input('Press enter to exit.')

#Decryptors used in invention process
decryptors = (
	Decryptor("Accelerant Decryptor", 1.2, 1, 2, 10),
	Decryptor("Attainment Decryptor", 1.8, 4, -1, 4),
	Decryptor("Augmentation Decryptor", 0.6, 9, -2, 2),
	Decryptor("Optimized Attainment Decryptor", 1.9, 2, 1, -2),
	Decryptor("Optimized Augmentation Decryptor", 0.9, 7, 2, 0),
	Decryptor("Parity Decryptor", 1.5, 3, 1, -2),
	Decryptor("Process Decryptor", 1.1, 0, 3, 6),
	Decryptor("Symmetry Decryptor", 1, 2, 1, 8)
)

#Load blueprint data into dictionary
blueprint_data = load_json()

#Load typeID/name data into dictionary
typeID_name_data = load_csv()

#Recieve typeID from input 
bp_typeID = input('Enter the typeID of the tier 2 blueprint you wish to make \n>> ')

#Retrieve product typeID
product_typeID = str(blueprint_data[bp_typeID]['activities']['manufacturing']['products'][0]['typeID'])

#Collect the materials required information
bp_mats = blueprint_data[bp_typeID]['activities']['manufacturing']['materials']

#Create required material objects for use in setting price later on
materials = init_materials(bp_mats)

#Create the typeid specific part of the url
text = create_marketstat_url()

#Request XML data for materials and product, only returns product price, material prices set in materials dictionary
productprice = get_market_data()

#Create bp and product objects
bp = Blueprint(typeID_name_data[bp_typeID], bp_mats)
product = Product(typeID_name_data[product_typeID], productprice) 

#Calculate outcome of invention with each decryptor
outcomes = calculate_outcomes()

#Creates average dictionary and initiates with keys
averages = init_averages()

#Amount of case scenarios to run
run_scenarios()

#Print results
print_results()