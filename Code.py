from random import choices, randint, uniform
from typing import List
import numpy as np
import pandas as pd
from math import sqrt

Nilai_saham = List[int]
Kromosom = List[int]
Populasi = List[Kromosom]

# variabel global
max_pop = 100
max_generation = 1000   

def generate_kromosom() -> Kromosom:
    # generating [a0, a1, ..., a10]
    return [uniform(-2,2) for i in range(11)]

def hitung_harga(konstanta: Kromosom, nilai: Nilai_saham):
    # f(x) = a0 + a1.y1 + a2.y2 + a3.y3 + .... + a10.y10
    # a = konstanta, y = nilai
    nilai = np.insert(nilai, 0, 1)
    return sum(np.multiply(konstanta, nilai))

def fitness_kromosom(kromosom: Kromosom, nilai: Nilai_saham, harga: int) -> float :
    y = hitung_harga(kromosom, nilai)
    return 1/(0.00000000000000000000000000000000000000000001+abs(harga - y))

def fitness_jurnal(kromosom: Kromosom, saham: Nilai_saham) -> float:
    squared_error = 0
    for i in range(10):
        y = hitung_harga(kromosom,saham[i+1:i+11])
        error = saham[i] - y
        squared_error += error ** 2
    mse = sqrt(squared_error/10)
    return 1/(0.00000000000000000000000000000000000000000001+mse)


def initiate_pop() -> Populasi:
    return [generate_kromosom() for i in range(max_pop)]

def regen_pop(populasi: Populasi, parent: Populasi, pc: int) -> Populasi:
    populasi = populasi[:len(populasi)-pc]
    populasi += crossover(parent[0],parent[1], pc)
    return [mutasi(kromosom) for kromosom in populasi]

def parent_selection(populasi: Populasi, nilai: Nilai_saham, harga: int) -> Populasi:
    return choices(
        populasi,
        weights=[fitness_kromosom(kromosom, nilai, harga) for kromosom in populasi],
        k=2
    )

def parent_selection_jurnal(populasi: Populasi, saham: Nilai_saham, fit: Populasi) -> Populasi:
    return choices(
        populasi,
        weights=fit,
        k=2
    )
   

def crossover(parentA: Kromosom, parentB: Kromosom, pc: int) -> Populasi:
    offspring = []
    for x in range(0,pc-1,2):
        i = randint(1,10)
        offspring += [parentA[0:i] + parentB[i:], parentB[0:i] + parentA[i:]]
    if pc % 2:
        i = randint(1,10)
        offspring += choices([parentA[0:i] + parentB[i:], parentB[0:i] + parentA[i:]],k=1)
    return offspring
    

def mutasi(kromosom: Kromosom) -> Kromosom:
    for i in range(0,len(kromosom)):
        if np.random.random_sample() < pm:
            kromosom[i] = uniform(-2,2)
    return kromosom

#main

pm = 1/(max_pop*11) # probabilitas mutasi = 1 / banyak gen
pc = round(0.4 * max_pop)
gen = 0
jumlah_hari = 50
dataset = pd.read_excel('antam.xlsx', usecols='B')
awal = 60
saham = dataset.values[awal:awal+21]
harga = saham[0]
nilai = saham[1:11]
error = 0.1
forecast = []
for i in range(1, jumlah_hari+1):
    pop = initiate_pop()
    while gen < max_generation:
        gen += 1
        # sort berdasarkan fitness score
        fit = [fitness_jurnal(kromosom, saham) for kromosom in pop]
        pop = [x for _,x in sorted(zip(fit,pop),reverse=True)]
        fit = sorted(fit,reverse=True)
        # print(fit[0])
        if (fit[0] > error):
            break
        parent = parent_selection_jurnal(pop, saham, fit)
        pop = regen_pop(pop, parent, pc)
    fit = [fitness_jurnal(kromosom, saham) for kromosom in pop]
    pop = [x for _,x in sorted(zip(fit,pop),reverse=True)]
    best = pop[0]
    print('best kromosom hari ke-',i,': ', best)
    harga_prediksi = round(hitung_harga(best,saham[:10]))
    forecast += [[i,harga_prediksi,int(saham[0]), int(abs(saham[0] - harga_prediksi))]]
    saham = dataset.values[awal-i:awal+21-i]
print('forecast harga saham: ', forecast)
