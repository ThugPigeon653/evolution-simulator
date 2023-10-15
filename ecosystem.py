#TODO: 
# - calculate odds of pregnancy, and birth. As it stands, all interactions with a posssible birth do result in birth
# - implement mutation 
import sqlite3
import json
import random
import os
from db_connection import Connection
import logger as log
from logger import logging 

logger=log.MyLogger('ecosystem.txt')

if os.path.exists('animal_database.db'):
    os.remove('animal_database.db')
conn = Connection.get_connection()

class Terrain:
    def __init__(self):
        self.cursor = conn.cursor()
        self.cursor.execute('''
            CREATE TABLE terrain (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                temperature REAL,
                precipitation REAL,
                vegetation_density REAL,
                terrain_type TEXT,
                area REAL,
                color TEXT
            )
        ''')
        conn.commit()

    def create_new_terrain(self, name, temperature, precipitation, vegetation_density, terrain_type, area, color):
        self.cursor.execute('''
            INSERT INTO terrain (name, temperature, precipitation, vegetation_density, terrain_type, area)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, temperature, precipitation, vegetation_density, terrain_type, area))
        conn.commit()
        return self.cursor.lastrowid

    def get_terrain_attributes(self, terrain_id):
        self.cursor.execute('SELECT * FROM terrain WHERE id = ?', (terrain_id,))
        terrain_data = self.cursor.fetchone()
        if terrain_data:
            id, name, temperature, precipitation, vegetation_density, terrain_type, area = terrain_data

            return {
                'id': id,
                'name': name,
                'temperature': temperature,
                'precipitation': precipitation,
                'vegetation_density': vegetation_density,
                'terrain_type': terrain_type,
                'area': area
            }
        else:
            return None

class Animals:

    __this_year:int=0

    def __init__(self):
        self.cursor = conn.cursor()
        self.cursor.execute('''
            CREATE TABLE animals (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                num_legs INTEGER,
                eye_size REAL,
                mouth_size REAL,
                weight REAL,
                energy_capacity REAL,
                endurance REAL,
                num_teeth INTEGER,
                avg_old_age REAL,
                old_age REAL,
                breeding_lifecycle REAL,
                eye_injury INTEGER,
                leg_injury INTEGER,
                mouth_injury INTEGER,
                general_injury INTEGER,
                prey_relationships TEXT,
                terrain_id INTEGER,
                birth_rate REAL,
                litter_size INTEGER,
                born INTEGER,
                ear_size REAL,
                ear_injury INTEGER,
                is_male BOOL CHECK(is_male=True or is_male=False)
            )
        ''')
        conn.commit()

    @property
    def this_year(self):
        return self.__this_year
    
    @this_year.setter
    def this_year(self, year):
        self.__this_year=year

    def create_new_animal(self, name:str, num_legs:int, eye_size:float, mouth_size:float, weight:float, energy_capacity:float, endurance:float,
                          num_teeth:int, avg_old_age:float, old_age:float, breeding_lifecycle:float, eye_injury:int, leg_injury:int, mouth_injury:int, general_injury:int, prey_relationships:list[str],
                          terrain_id, birth_rate, litter_size, born, ear_size, ear_injury, is_male:bool=None):
        if(is_male==None):
            is_male=random.choice([True, False])
        self.cursor.execute('''
            INSERT INTO animals (name, num_legs, eye_size, mouth_size, weight, energy_capacity, endurance,
            num_teeth, avg_old_age, old_age, breeding_lifecycle, eye_injury, leg_injury, mouth_injury, general_injury, prey_relationships, terrain_id, birth_rate, litter_size, born, ear_size, ear_injury, is_male)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, num_legs, eye_size, mouth_size, weight, energy_capacity, endurance, num_teeth, avg_old_age,
              old_age, breeding_lifecycle, eye_injury, leg_injury, mouth_injury, general_injury, json.dumps(prey_relationships), terrain_id, birth_rate, litter_size, born, ear_size, ear_injury, is_male))

        conn.commit()
        logger.log("Created "+name+" ("+str(self.cursor.lastrowid)+")\033[0m", logging.INFO)
        return self.cursor.lastrowid

    def get_animal_attributes(self, animal_id):
        self.cursor.execute('SELECT * FROM animals WHERE id = ?', (animal_id,))
        animal_data = self.cursor.fetchone()
        if animal_data:
            id, name, num_legs, eye_size, mouth_size, weight, energy_capacity, endurance, num_teeth, avg_old_age, old_age, breeding_lifecycle, eye_injury, leg_injury, mouth_injury, general_injury, prey_relationships_json, terrain_id, birth_rate, litter_size, born, ear_size, ear_injury, is_male = animal_data

            prey_relationships = json.loads(prey_relationships_json) if prey_relationships_json else None

            return {
                'id': id,
                'name': name,
                'num_legs': num_legs,
                'eye_size': eye_size,
                'mouth_size': mouth_size,
                'weight': weight,
                'energy_capacity': energy_capacity,
                'endurance': endurance,
                'num_teeth': num_teeth,
                'avg_old_age': avg_old_age,
                'old_age': old_age,
                'breeding_lifecycle': breeding_lifecycle,
                'injuries': {
                    'eye_injury': eye_injury,
                    'leg_injury': leg_injury,
                    'mouth_injury': mouth_injury,
                    'general_injury': general_injury
                },
                'prey_relationships': prey_relationships,
                'terrain_id': terrain_id,
                'birth_rate': birth_rate,
                'litter_size': litter_size,
                'born':born,
                'ear_size':ear_size,
                'ear_injury':ear_injury
            }
        else:
            return None
    
    def combine_prey_relationships(self, prey1, prey2):
        combined_prey = list(set(prey1) | set(prey2))
        return combined_prey
    
    @staticmethod
    def average(parent1_attr, parent2_attr):
        total = float(parent1_attr) + float(parent2_attr)
        total = total / 2
        if total % 1 == 0.5:
            if random.randint(0, 1) == 1:
                total = total + 0.5
            else:
                total = total - 0.5
        return total
    
    def create_child_animal(self, parent1_id, parent2_id):
        parent1_attributes = self.get_animal_attributes(parent1_id)
        parent2_attributes = self.get_animal_attributes(parent2_id)
        is_male=random.choice([True, False])
        weight=Animals.average(parent1_attributes['weight'] , parent2_attributes['weight'])
        weight_offset=(random.uniform(0.001, 0.300)*weight)
        if(is_male):
            weight+=weight_offset
        else:
            weight-=weight_offset 
        if parent1_attributes and parent2_attributes:
            child_attributes = {
                'name': parent1_attributes['name'],
                'num_legs': Animals.average(parent1_attributes['num_legs'], parent2_attributes['num_legs']),
                'eye_size': Animals.average(parent1_attributes['eye_size'] , parent2_attributes['eye_size']),
                'mouth_size': Animals.average(parent1_attributes['mouth_size'] , parent2_attributes['mouth_size']),
                'weight': weight,
                'energy_capacity': Animals.average(parent1_attributes['energy_capacity'] , parent2_attributes['energy_capacity']),
                'endurance': Animals.average(parent1_attributes['endurance'] , parent2_attributes['endurance']),
                'num_teeth': int(Animals.average(parent1_attributes['num_teeth'] , parent2_attributes['num_teeth'])),
                'avg_old_age': Animals.average(parent1_attributes['avg_old_age'] , parent2_attributes['avg_old_age']),
                'old_age': Animals.average(parent1_attributes['old_age'] , parent2_attributes['old_age']),
                'breeding_lifecycle': Animals.average(parent1_attributes['breeding_lifecycle'] , parent2_attributes['breeding_lifecycle']),
                'eye_injury': 0, 
                'leg_injury':0,
                'mouth_injury':0,
                'general_injury':0,
                'prey_relationships': self.combine_prey_relationships(parent1_attributes['prey_relationships'], parent2_attributes['prey_relationships']),
                'terrain_id': parent1_attributes['terrain_id'],
                'birth_rate': Animals.average(parent1_attributes['birth_rate'] , parent1_attributes['birth_rate']),
                'litter_size': Animals.average(parent1_attributes['litter_size'] , parent2_attributes['litter_size']),
                'born':self.this_year,
                'ear_size':Animals.average(parent1_attributes['ear_size'],parent2_attributes['ear_size']),
                'ear_injury':0,
                'is_male':is_male
            }

            self.create_new_animal(**child_attributes)

            return f"\033[92mChild animal created with ID {self.cursor.lastrowid}\033[0m"
        else:
            return "Failed to create child animal: Parent animals not found"
    
    def get_all_animals(self):
        self.cursor.execute('SELECT * FROM animals')
        all_animals = self.cursor.fetchall()

        animals_list = []
        for animal_data in all_animals:
            id, name, num_legs, eye_size, mouth_size, weight, energy_capacity, endurance, num_teeth, avg_old_age, old_age, breeding_lifecycle, eye_injury, leg_injury, mouth_injury, general_injury, prey_relationships_json, terrain_id, birth_rate, litter_size, born, ear_size, ear_injury, is_male = animal_data

            prey_relationships = json.loads(prey_relationships_json) if prey_relationships_json else None

            animal = {
                'id': id,
                'name': name,
                'num_legs': num_legs,
                'eye_size': eye_size,
                'mouth_size': mouth_size,
                'weight': weight,
                'energy_capacity': energy_capacity,
                'endurance': endurance,
                'num_teeth': num_teeth,
                'avg_old_age': avg_old_age,
                'old_age': old_age,
                'breeding_lifecycle': breeding_lifecycle,
                'injuries': {
                    'eye_injury': eye_injury,
                    'leg_injury': leg_injury,
                    'mouth_injury': mouth_injury,
                    'general_injury': general_injury,
                    'ear_injury':ear_injury
                },
                'prey_relationships': prey_relationships,
                'terrain_id': terrain_id,
                'birth_rate': birth_rate,
                'litter_size': litter_size,
                'born':born,
                'ear_size':ear_size,
                'is_male':is_male
            }
            animals_list.append(animal)

        return animals_list

    def get_age_modifier(self, animal_id)->float:
        self.cursor.execute('SELECT old_age, born FROM animals WHERE id = ?', (animal_id,))
        animal_data = self.cursor.fetchone()
        old_age, born = animal_data
        mid_age=old_age/2
        current_age=self.this_year-born
        # if theyre younger...
        if(self.this_year<=(old_age/2)+born):
            modifier:float=current_age/mid_age
        else:
            modifier:float=(old_age-current_age)/mid_age
        # This buffer has been added to flatten each end of the double-gradient. This is because young animals
        # still have partial capabilities due to their parents. Older animals will become as ineffective as 
        # an infant, but have learned enough by now to partially compensate for their physical incapabilities.
        # Without this modifier, infants and elderly would be guaranteed death. 
        if modifier<0.15:
            modifier=0.15
        return modifier

    def get_distance_travelled_in_day(self, animal_id)->float:
        self.cursor.execute('SELECT eye_size, weight, endurance, terrain_id FROM animals WHERE id = ?', (animal_id,))
        animal_data = self.cursor.fetchone()
        eye_size, weight, endurance, terrain_id = animal_data
        self.cursor.execute('SELECT vegetation_density from terrain WHERE id = ?', (terrain_id,))
        vegetation=self.cursor.fetchone()[0]
        distance=weight*endurance*0.4*eye_size*self.get_age_modifier(animal_id)/(1+vegetation)
        return distance
    
    def get_species(self, animal_id):
        self.cursor.execute('SELECT name FROM Animals WHERE id = ?', (animal_id,))
        return self.cursor.fetchone()[0]

    def get_land_covered_in_day(self, animal_id)->float:
        self.cursor.execute('SELECT eye_size, eye_injury, ear_size, ear_injury from Animals WHERE id = ?', (animal_id,))
        eye_size, eye_injury, ear_size, ear_injury=self.cursor.fetchone()
        distance:float=self.get_distance_travelled_in_day(animal_id)
        search_radius=max(ear_size/((1-ear_injury)/10), eye_size/((1-eye_injury)/10))
        return distance*search_radius

    def get_encounter_odds_in_day(self, animal_id) -> float:
        self.cursor.execute('SELECT terrain_id FROM Animals WHERE id = ?', (animal_id,))
        terrain_id = self.cursor.fetchone()[0]
        self.cursor.execute('SELECT area FROM Terrain WHERE id = ?', (terrain_id,))
        terrain_area = self.cursor.fetchone()[0]
        self.cursor.execute('SELECT count(*) FROM Animals WHERE terrain_id = ?', (terrain_id,))
        animal_count = self.cursor.fetchone()[0]
        population_density = animal_count / terrain_area
        land_covered = self.get_land_covered_in_day(animal_id)
        return population_density*land_covered

    def get_encounters_in_day(self, animal_id:int)->list[int]:
        self.cursor.execute('SELECT terrain_id FROM Animals WHERE id = ?', (animal_id,))
        terran_tuple=self.cursor.fetchone()
        animals_encountered:list[int]=[]
        if(terran_tuple!=None):
            terrain_id=terran_tuple[0]
            odds=self.get_encounter_odds_in_day(animal_id)
            luck_factor=random.uniform(0.10, 1.90)
            odds=odds*luck_factor
            discreet_encounters:int=int(odds)
            self.cursor.execute('SELECT id from Animals WHERE terrain_id = ? AND id != ? ORDER BY RANDOM() LIMIT ?',(terrain_id, animal_id, discreet_encounters))
            animals_encountered=self.cursor.fetchall()
        return animals_encountered

    def get_does_see_animal(self, predator_id:int, prey_id:int)->(bool, bool):
        self.cursor.execute('SELECT eye_size, weight, eye_injury, leg_injury, general_injury, terrain_id, ear_size, ear_injury from Animals WHERE id = ?', (predator_id,))
        eye_size, weight, eye_injury, leg_injury, general_injury, terrain_id, ear_size, ear_injury=self.cursor.fetchone()
        terrain_density=self.cursor.execute('SELECT vegetation_density from terrain WHERE id = ?', terrain_id)
        predator_defense_score:float=((((eye_size*((10-eye_injury)/10)+(ear_size*((10-ear_injury)/10)))-((10-leg_injury)/10)*1.1)-(weight/1000))/(1+terrain_density))
        predator_offense_score:float=predator_defense_score*((10-general_injury)/10)

        self.cursor.execute('SELECT eye_size, weight, eye_injury, leg_injury, general_injury, terrain_id, ear_size, ear_injury from Animals WHERE id = ?', (prey_id,))
        eye_size, weight, eye_injury, leg_injury, general_injury, terrain_id, ear_size, ear_injury=self.cursor.fetchone()
        prey_defense_score:float=(((eye_size*((10-eye_injury)/10)+(ear_size*((10-ear_injury)/10)))-((10-leg_injury)/10)*0.8)-(weight/1000))/(1+terrain_density)
        prey_offense_score:float=prey_defense_score*((10-general_injury)/10)
        predator_offense_score=random.uniform(0.000, predator_offense_score)
        prey_defense_score=random.uniform(0.000, prey_defense_score)
        if(predator_offense_score>prey_defense_score):
            prey_seen=True
        else:
            prey_seen=False
        predator_defense_score=random.uniform(0.000, predator_defense_score)
        prey_offense_score=random.uniform(0.000, prey_offense_score)
        if(prey_offense_score>predator_defense_score):
            predator_seen:bool=True
        else:
            predator_seen:bool=False
        return (prey_seen, predator_seen)

    def get_does_chase_animal(self, predator_id:int, prey_id:int)->bool:
        will_chase:bool=None
        if(predator_id!=None and prey_id!=None):
            self.cursor.execute('SELECT prey_relationships, weight FROM Animals WHERE id = ?', (predator_id,))
            result=self.cursor.fetchone()
            if(result!=None):
                prey_relationships, weight = result
                self.cursor.execute('SELECT name, weight FROM Animals WHERE id = ?', (prey_id,))
                animal_data=self.cursor.fetchone()
                if(animal_data!=None):
                    name,prey_weight=animal_data
                    if(name in prey_relationships.split(',')):
                        will_chase=True
                    else:
                        weight=random.uniform(0.000, weight)
                        prey_weight=random.uniform(0.000, prey_weight)
                        if(weight>prey_weight):
                            will_chase=True
                        else:
                            will_chase=False
        return will_chase

    def get_does_catch_animal(self, predator_id:int, prey_id:int)->bool:
        self.cursor.execute('SELECT num_legs, weight, energy_capacity, endurance, leg_injury, general_injury, terrain_id FROM Animals WHERE id = ?', (predator_id,))
        num_legs, weight, energy_capacity, endurance, leg_injury, general_injury, terrain_id=self.cursor.fetchone()
        self.cursor.execute('SELECT vegetation_density FROM terrain WHERE id = ?', (terrain_id,))
        vegetation_density=self.cursor.fetchone()[0]
        predator_score=((((num_legs**0.5)*energy_capacity)/(weight*((22-leg_injury-general_injury)/20)))*endurance)/(1+vegetation_density)
        self.cursor.execute('SELECT num_legs, weight, energy_capacity, endurance, leg_injury, general_injury FROM Animals WHERE id = ?', (prey_id,))
        num_legs, weight, energy_capacity, endurance, leg_injury, general_injury = self.cursor.fetchone()
        try:
            prey_score=((((num_legs**0.5)*energy_capacity)/(weight*((22-leg_injury-general_injury)/20)))*endurance)/(1+vegetation_density)
        except Exception as e:
            pass
        predator_score=random.uniform(predator_score/2.00, predator_score)
        prey_score=random.uniform(prey_score/2.00, prey_score)
        catches_prey:bool
        if(predator_score>prey_score):
            catches_prey=True
        else:
            catches_prey=False
        return catches_prey

    def get_combat_outcome(self, predator_id:int, prey_id:int)->str:
        outcome:float=False
        return_value=None
        if(predator_id!=None and prey_id!=None):
            predator_age=self.get_age_modifier(predator_id)
            prey_age=self.get_age_modifier(prey_id)
            self.cursor.execute('SELECT name, num_legs, mouth_size, weight, energy_capacity, endurance, num_teeth from Animals WHERE id = ?', (predator_id,))
            predator_name, num_legs, mouth_size, weight, energy_capacity, endurance, num_teeth = self.cursor.fetchone()
            predator_score:float = random.uniform(0.00, (num_legs**0.5)*mouth_size*(num_teeth**1.1)*(endurance**0.9)*(energy_capacity**0.9)*(weight**0.5))
            self.cursor.execute('SELECT name, num_legs, mouth_size, weight, energy_capacity, endurance, num_teeth from Animals WHERE id = ?', (prey_id,))
            prey_name, num_legs, mouth_size, weight, energy_capacity, endurance, num_teeth = self.cursor.fetchone()
            prey_score:float = random.uniform(0.00, (num_legs**0.55)*(mouth_size**0.9)*(num_teeth**0.9)*(endurance**1.1)*energy_capacity*(weight**0.5))
            outcome = predator_score-prey_score
            final_result=(outcome/predator_score)
            if(abs(final_result)>0.1 and abs(final_result)<7):
                injury_types=["eye", "leg", "mouth", "ear", "general"]
                injury_roll=random.randint(0, len(injury_types)-1)
                if(predator_score>prey_score):
                    victim=prey_id
                else:
                    victim=predator_id
                column_name = injury_types[injury_roll] + "_injury"
                query = 'SELECT {} FROM Animals WHERE id = ?'.format(column_name)
                self.cursor.execute(query, (victim,))
                injury=self.cursor.fetchone()[0]
                if((injury+final_result)<10):
                    injury=injury+final_result
                else:
                    injury=10
                column_name = injury_types[injury_roll] + "_injury"
                query = 'UPDATE Animals SET {} = ? WHERE id = ?'.format(column_name)
                self.cursor.execute(query, (injury, victim))
                return_value=("\n\033[93m"+str(victim)+ " has been injured\033[0m("+str(final_result))
            elif(abs(outcome)>=0.7):
                if(outcome>0):
                    victim=prey_id
                else:
                    victim=predator_id
                self.cursor.execute('DELETE FROM Animals WHERE id = ?', (victim,))
                return_value=("\n\033[91m"+str(victim)+ " has been killed\033[0m")
        return return_value

    def execute_interaction(self, predator_id:int, prey_id:int):
        self.cursor.execute('SELECT name, is_male FROM Animals WHERE id = ?', (predator_id,))
        data=self.cursor.fetchone()
        outcome=None
        if(data!=None):
            predator_name, predator_is_male=data
            self.cursor.execute('SELECT name, is_male FROM Animals WHERE id = ?', (prey_id,))
            prey_name, prey_is_male=self.cursor.fetchone()
            status:str=f"No interaction eventuated between {predator_name} and {prey_name}. "
            logger.log(predator_name + " found a "+prey_name,logging.INFO)
            if(predator_name==predator_name and predator_is_male!=prey_is_male and (random.randint(0,1)==1)):
                self.create_child_animal(predator_id, prey_id)
                status=None
            else:
                chase_decision=(self.get_does_chase_animal(predator_id, prey_id),self.get_does_chase_animal(prey_id, predator_id))
                if(chase_decision==(True,True)):
                    status=f"A fight ensued between {predator_name} and {prey_name}"
                    outcome = self.get_combat_outcome(predator_id, prey_id)
                elif(chase_decision==(True,False)):
                    status=f"A chase ensued between {predator_name} and {prey_name}. "
                    if(self.get_does_catch_animal(predator_id, prey_id)):
                        status+="The animal was caught."
                        outcome=self.get_combat_outcome(predator_id, prey_id)
                    else:
                        status+="The animal got away."
                elif(chase_decision==(False, True)):
                    status=f"Prey fought back: {predator_name} and {prey_name}. "
                    if(self.get_does_catch_animal(prey_id, predator_id)):
                        status+= "successful catch"
                        outcome=self.get_combat_outcome(prey_id, predator_id)
                else:
                    status=None
        else:
            status=None
        if(outcome!=None):
            status+=outcome
        return status

    def get_feeding_order(self):
        self.cursor.execute('SELECT id FROM Animals ORDER BY RANDOM()')
        return self.cursor.fetchall()

def load_json_data(path):
    with open(path, "r") as json_data:
        data=json.load(json_data)
        return data

def initialize():
    terrain_manager = Terrain()
    terrain_data = load_json_data("terrain.json")

    biomes:list[int]=[]
    for terrain_name, terrain_attributes in terrain_data.items():
        logger.log(terrain_attributes, logging.info)
        terrain_id = terrain_manager.create_new_terrain(**terrain_attributes)
        biomes.append(terrain_id)
    animal_manager = Animals()
    animal_data=load_json_data("animals.json")
    animals=["Deer", "Wolf", "Bear", "Lion", "Rabbit", "Fox"]
    for animal in animals:
        data=animal_data[animal]
        i=0
        while i<50:
            terrain_id=biomes[random.randint(0,len(biomes)-1)]
            data["terrain_id"]=terrain_id
            animal_manager.create_new_animal(**data)
            i+=1
    i=0
    try:
        while i<1000:
            animal_manager.this_year=i
            for animal_id in animal_manager.get_feeding_order():
                encounters_for_animal=animal_manager.get_encounters_in_day(animal_id[0])
                for encounter in encounters_for_animal:
                    interaction=animal_manager.execute_interaction(animal_id[0], encounter[0])
                    if(interaction!=None):
                        logger.log(str(i)+" "+interaction, logging.INFO)
            logger.log(animal_manager.get_all_animals(), logging.INFO)
            i+=1
    finally:
        conn.close()
        logger.log("Database connection closed.", logging.INFO)
