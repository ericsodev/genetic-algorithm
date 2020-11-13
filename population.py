from random import randint
import math


class Individual: 
    ORDERED_CROSSOVER_SWATH_LENGTH = 0.4  
    length = 0

    def __init__(self, city_coordinates: dict, chromosome=''):
        self.chromosome = ''
        self.city_coordinates = city_coordinates
        self.cities = list(city_coordinates.keys())
        self.length = len(self.cities)        

        # If chromosome parameter is empty, generate random sequence
        if not chromosome:                           
            chromosome_positions = [x for x in range(self.length)]

            for _ in range(self.length):
                self.chromosome += self.cities[chromosome_positions.pop(randint(0, len(chromosome_positions) -1))]
        else:
            self.chromosome = chromosome            

    def ordered_crossover(self, partner):
        mating_chromosome = partner.chromosome
        new_chromosome = ['-'] * self.length

        # Copy a block of DNA from first parent 
        swap_position = randint(0, self.length - (1 + math.floor(self.length * self.ORDERED_CROSSOVER_SWATH_LENGTH)))     
        for position in range(swap_position, swap_position + math.floor(self.length * self.ORDERED_CROSSOVER_SWATH_LENGTH), 1):
            new_chromosome[position] = self.chromosome[position]

        # Fill in remaining positions in chromosome with second parent's genes
        unused_parent_2_genes = [gene for gene in mating_chromosome if gene not in new_chromosome]
        for index in range(self.length):
            if new_chromosome[index] == '-':                
                new_chromosome[index] = unused_parent_2_genes.pop(0)

        # Chance to mutate:
        for _ in range(0, self.length):
            if randint(0, 100) > 95:
                new_chromosome = self.mutate(new_chromosome)

        return "".join(new_chromosome)    

    def mutate(self, chromosome):
        pos_a, pos_b = randint(0, self.length-1), randint(0, self.length-1)
        new_chromosome = chromosome
        new_chromosome[pos_a], new_chromosome[pos_b] = new_chromosome[pos_b], new_chromosome[pos_a]
        
        return new_chromosome

    def fitness(self):
        distance = 0
        for index in range(self.length):
            current_pos, old_pos = self.city_coordinates[self.chromosome[index]], self.city_coordinates[self.chromosome[index-1]]
            distance += math.sqrt((current_pos[0] - old_pos[0]) ** 2  + (current_pos[1] - old_pos[1]) ** 2)

        self.distance = distance
        return distance

    def __add__(self, partner):
        return Individual(self.city_coordinates, chromosome=self.ordered_crossover(partner))
    
    def __repr__(self):
        return self.chromosome


class Population:  
    BREEDING_CUTOFF = 0.15

    def __init__(self, coordinates, population=1000, interval=200, stop=50000):
        self.size = population    
        self.average_fitness = -1  
        self.coordinates = coordinates
        self.pool = [Individual(coordinates) for _ in range(self.size)]
        self.generation = 0
        self.print_interval = interval
        self.stop = stop

    def next(self, exit=False):
        candidates = []
        
        # Calculate fitness and sort candidates
        new_average_fitness = 0
        last_pool_size = len(self.pool)
        for chromosome in self.pool:
            fitness = chromosome.fitness()
            new_average_fitness += fitness

            fillable_position = 0
            try:
                fillable_position = min([position for position, value in enumerate(candidates) if value.distance > fitness])
            except ValueError:
                fillable_position = -1
            if fillable_position == -1:
                candidates.append(chromosome)
            else:
                candidates.insert(fillable_position, chromosome)

        # Cutoff candidates
        candidates = candidates[0:math.ceil(len(candidates) * self.BREEDING_CUTOFF / 2) * 2]
        self.pool = candidates

        # Calculate average fitness and change
        new_average_fitness /= last_pool_size
        change = (new_average_fitness) / self.average_fitness - 1 if self.average_fitness != -1 else 5

        self.average_fitness = new_average_fitness    
        if self.generation % self.print_interval == 0:
            print(f'Gen {self.generation}: Average {round(self.average_fitness, 6)}, Highest: {round(candidates[0].distance, 6)}')
        self.generation += 1

        # End program if change to last generation was negligible
        if (0 < change < 0.0001 and self.generation > self.stop and abs(self.average_fitness / candidates[0].distance - 1) < 0.03) or exit:
            print(f'Gen {self.generation}: Average {self.average_fitness}, Highest: {candidates[0].distance}')
            print(f'Optimal Route: {candidates[0]}')
            return candidates[0].distance        
        else:            
            # Breed chromosomes
            for index in range(1, math.ceil(len(candidates) * 0.6), 2):
                parent_a, parent_b = candidates[0], candidates[index]
                if len(self.pool) >= self.size:
                        break
                else:
                    self.pool.append(parent_a + parent_b)

            for index in range(1, len(candidates)-2, 2):
                for x in range(1, 3, 1):
                    parent_a, parent_b = candidates[index], candidates[index+x]
                    if len(self.pool) >= self.size:
                        break
                    else:
                        self.pool.append(parent_a + parent_b)

            return -1
