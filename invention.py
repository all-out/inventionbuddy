import math
import random
import json
import urllib.request

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

	def outcome_bp(self, input_material):
		new_prob = self.prob * input_material.prob_multi
		max_run = self.runs + input_material.max_run_mod
		new_mat_effic = self.mat_effic + input_material.mat_effic
		new_time_effic = self.time_effic + input_material.time_effic
		outcome_bp = Blueprint(self.name + " : " + input_material.name, 
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
	
def init_materials(materials):
	for mats in bp_mats:
		if not mats['typeID'] in materials: 
			materials[mats['typeID']] = Material(mats['typeID'])
	return materials
	

#To hold BP dictionary
bp_json_data = load_json()

#Take typeID from input 
the_bp_typeID = input('Enter the typeID of the tier 2 blueprint \n>> ')
#Collect the materials required information
bp_mats = bp_json_data[the_bp_typeID]['activities']['manufacturing']['materials']

#Create required material objects for use in setting price later on
materials = {}
materials = init_materials(materials)
#Redo this garbage code

#Create the typeid specific part of the url
text = ""
for i in range(0, len(bp_mats)):
	text = text + "typeid=" + str(bp_mats[i]['typeID']) + "&"

product_typeID = str(bp_json_data[the_bp_typeID]['activities']['manufacturing']['products'][0]['typeID'])
text = text + "typeid=" + product_typeID + "&"

productprice = 0
#Request XML data
with urllib.request.urlopen('http://api.eve-central.com/api/marketstat?' + text + 'regionlimit=10000002') as response:
	xml = response.read()
	from xml.etree import ElementTree as ET
	#Set price of each material by finding the typeid in the XML data
	for i in range(0, len(bp_mats)):
		materials[bp_mats[i]['typeID']].setprice(float(ET.fromstring(xml).find('marketstat/type[@id=\'' + str(bp_mats[i]['typeID']) + '\']/sell/min').text))
	#Set product price in the same way
	productprice = float(ET.fromstring(xml).find('marketstat/type[@id=\'' + product_typeID + '\']/sell/min').text)

test_bp = Blueprint("N/A", bp_mats)
test_product = Product("N/A", productprice) 

#Decryptors
input_mats = (Decryptor("Accelerant Decryptor", 1.2, 1, 2, 10),
			  Decryptor("Attainment Decryptor", 1.8, 4, -1, 4),
			  Decryptor("Augmentation Decryptor", 0.6, 9, -2, 2),
			  Decryptor("Optimized Attainment Decryptor", 1.9, 2, 1, -2),
			  Decryptor("Optimized Augmentation Decryptor", 0.9, 7, 2, 0),
			  Decryptor("Parity Decryptor", 1.5, 3, 1, -2),
			  Decryptor("Process Decryptor", 1.1, 0, 3, 6),
			  Decryptor("Symmetry Decryptor", 1, 2, 1, 8))

outcomes = []
for index in range(len(input_mats)):
	outcomes.append(test_bp.outcome_bp(input_mats[index]))

#Creates average dictionary and initiates with keys
averages = {}
for index in range(len(outcomes)):
	averages[outcomes[index].name] = 0

#Amount of case scenarios to run
cycles = 100
for i in range(0, cycles):
	for index in range(len(outcomes)):
		averages[outcomes[index].name] += calc_profit(test_product, outcomes[index])

#Calculate the average
for name in averages:
	averages[name] /= cycles

for key, value in averages.items():
	print(key + " : " + "{:,}".format(math.floor(value)))
