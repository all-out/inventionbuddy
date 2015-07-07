import invention

inventor = invention.BlueprintInvention()

#inventor.tech_two_invention()

#Assortment of salvage, method requires tech 2 bp implementation
input_string = """Alloyed Tritanium Bar	107	Salvaged Materials			1.07 m3
Armor Plates	66	Salvaged Materials			0.66 m3
Artificial Neural Network	30	Salvaged Materials			0.30 m3
Burned Logic Circuit	190	Salvaged Materials			1.90 m3
Capacitor Console	20	Salvaged Materials			0.20 m3
Charred Micro Circuit	422	Salvaged Materials			4.22 m3
Contaminated Nanite Compound	59	Salvaged Materials			0.59 m3
Damaged Artificial Neural Network	473	Salvaged Materials			4.73 m3
Defective Current Pump	4	Salvaged Materials			0.04 m3
Enhanced Ward Console	45	Salvaged Materials			0.45 m3
Fried Interface Circuit	260	Salvaged Materials			2.60 m3
Impetus Console	17	Salvaged Materials			0.17 m3
Intact Armor Plates	12	Salvaged Materials			0.12 m3
Intact Shield Emitter	5	Salvaged Materials			0.05 m3
Interface Circuit	27	Salvaged Materials			0.27 m3
Logic Circuit	59	Salvaged Materials			0.59 m3
Malfunctioning Shield Emitter	170	Salvaged Materials			1.70 m3
Micro Circuit	35	Salvaged Materials			0.35 m3
Power Circuit	66	Salvaged Materials			0.66 m3
Power Conduit	17	Salvaged Materials			0.17 m3
Scorched Telemetry Processor	87	Salvaged Materials			0.87 m3
Single-crystal Superalloy I-beam	5	Salvaged Materials			0.05 m3
Smashed Trigger Unit	88	Salvaged Materials			0.88 m3
Tangled Power Conduit	130	Salvaged Materials			1.30 m3
Telemetry Processor	23	Salvaged Materials			0.23 m3
Thruster Console	85	Salvaged Materials			0.85 m3
Trigger Unit	3	Salvaged Materials			0.03 m3
Tripped Power Circuit	413	Salvaged Materials			4.13 m3
Ward Console	167	Salvaged Materials			1.67 m3"""

#This makes a very large amount of results, which aren't very useful right now
input_string_two = """Isogen	100000	Mineral			0.01 m3
Megacyte	100000	Mineral			0.01 m3
Mexallon	100000	Mineral			0.01 m3
Morphite	100000	Mineral			0.01 m3
Pyerite	100000	Mineral			0.01 m3
Tritanium	100000	Mineral			0.01 m3
Zydrine	100000	Mineral			0.01 m3"""

inventor.find_highest_revenue_blueprints(input_string)