import population
import time


if __name__ == '__main__':
    cities = []
    coordinates = {}

    # Read map file
    with open('map.txt', 'r') as map_file:
        lines = map_file.readlines()
        lines = [line.strip('\n') for line in lines]

        for row_number, line in enumerate(lines):
            for col_number, value in enumerate(line):
                if value != '-':
                    cities.append(value)
                    coordinates[value] = (col_number, row_number)

    population = population.Population(coordinates, population=1000, interval=150)
    result = population.next()
    try:
        while result == -1:          
            result = population.next()       
    except KeyboardInterrupt:
        result = population.next(True)

        