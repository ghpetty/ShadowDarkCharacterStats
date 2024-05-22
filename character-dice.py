# -*- coding: utf-8 -*-
"""
Created on Tue May 21 15:15:10 2024

@author: gordo
"""

import numpy as np

all_stats = np.array(['STR','DEX','CON','INT','WIS','CHA'])

def nd6(n: int):
    x = np.sum(np.random.randint(1,7,n))
    return x

def roll_raw_stats(n_dice=3,n_stats=6):
    stats  = np.array([nd6(n_dice) for i in range(n_stats)])
    return stats
    
def recursive_convolve(dists:list):
    if len(dists) == 2:
        conv = np.convolve(dists[0],dists[1])
    else:
        conv = np.convolve(dists[0],recursive_convolve(dists[1:]))        
    return conv

def stats_sum_p_dist(n_dice=3,n_stats=6):
    dice_p_dist = np.ones(6)/6;
    n_recursions = n_dice * n_stats;
    probs = recursive_convolve(np.tile(dice_p_dist,[n_recursions,1]))
    percentiles = np.cumsum(probs) * 100
    vals = [i for i in range(n_dice*n_stats , n_dice*n_stats*6 + 1)]
    return dict(zip(vals,probs)), dict(zip(vals,percentiles))

def prompt_stat_priority():
    top_stats = input("Input up to two stats to prioritize, separated by a comma:\n").upper()
    if top_stats:
        top_stats = np.array([stat.strip() for stat in top_stats.split(',')])
        check_stat_name_input(top_stats)
    else: 
        top_stats = np.array([])
    bottom_stats = input("Input up to two stats to deprioritize, separated by a comma:\n").upper()
    if bottom_stats:
        bottom_stats = np.array([stat.strip() for stat in bottom_stats.split(',')])
        check_stat_name_input(bottom_stats)
    else:
        bottom_stats = np.array([])
        
    if np.any(np.isin(top_stats,bottom_stats)) or np.any(np.isin(bottom_stats,top_stats)):
        raise ValueError('a stat cannot be both prioritized and deprioritized')
    remaining_stats = all_stats[~np.isin(all_stats,np.concatenate([top_stats,bottom_stats]))]
    np.random.shuffle(remaining_stats)
    stat_priority = np.concatenate([top_stats,remaining_stats,bottom_stats])
    return stat_priority

def get_stats():
    stat_order = prompt_stat_priority()
    reroll = True
    while reroll:
        stat_vals = roll_raw_stats();
        stat_vals_sorted = np.sort(stat_vals)[::-1]
        stats_dict = dict(zip(stat_order,stat_vals_sorted))
        stats_dict = {stat:stats_dict[stat] for stat in all_stats}
        if np.any(stat_vals > 13):
            reroll = False
        else:
            print_stats(stats_dict)
            inp = input('No stat values greater than or equal to 14. Reroll? ([Y]/N):\n')
            if (not inp) or (inp.lower == "y"):
                reroll = True
            else:
                reroll = False

    # print_stats(stat_dict)
    return stats_dict
        
def print_stats(stats_dict: dict):
    print(*((stat+': '+str(stats_dict[stat])) for stat in all_stats),sep='\n')

def check_stat_name_input(words:list):
    if np.array_equal(words,[""]):
        return
    if len(words) > 2:
        raise ValueError('expected maximum of two stats separated by commas')
    wrong_inds = ~np.isin(words,all_stats)
    if np.any(wrong_inds):
        first_wrong_ind = np.argmax(wrong_inds)
        wrong_word = words[first_wrong_ind]
        raise ValueError("invalid stat name: "+wrong_word)

p_dist,percentiles = stats_sum_p_dist()
stats_dict = get_stats()
stats_total = sum(stats_dict.values())
prct = int(np.round(percentiles[stats_total],2))

print('-----')
print('Your stat block:')
print_stats(stats_dict)
if prct < 50:
    print('Your character is in the bottom '+str(prct)+'% of possible stat totals.')
else:
     print('Your character is in the top '+str(100-prct)+'% of possible stat totals.')   

