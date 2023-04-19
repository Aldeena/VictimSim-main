## EXPLORER AGENT
### @Author: Tacla, UTFPR
### It walks randomly in the environment looking for victims.

import sys
import os
import random
from abstract_agent import AbstractAgent
from physical_agent import PhysAgent
from abc import ABC, abstractmethod


class Explorer(AbstractAgent):

    result = {}
    untried = {}
    unbacktracked = {}
    walls = {}
    victims = {}
    #antAction = None
    action = None
    #inverter valor das tuplas na vertical, pois o grid sobe quando y é negativo
    directions = {'U':(0,-1), 'UR':(1,-1), 'R':(1,0), 'DR':(1,1), 'D':(0,1), 'DL':(-1, 1), 'L':(-1,0), 'UL':(-1, -1)}
    actions = ['U', 'UR', 'R', 'DR', 'D', 'DL', 'L', 'UL']
    #actions = ['U', 'R', 'D', 'L']
    #actions = ['UR', 'DR', 'DL', 'UL']
    #actions = ['U', 'R', 'D', 'L', 'UR', 'DR', 'UL', 'DL']

    def __init__(self, env, config_file, resc):
        """ Construtor do agente random on-line
        @param env referencia o ambiente
        @config_file: the absolute path to the explorer's config file
        @param resc referencia o rescuer para poder acorda-lo
        """

        super().__init__(env, config_file)
        
        # Specific initialization for the rescuer
        self.resc = resc           # reference to the rescuer agent
        self.rtime = self.TLIM     # remaining time to explore
        self.x = 0
        self.y = 0
        self.last_x = 0
        self.last_y = 0
        #self.passos = 0

    def dfs_Online(self):

        # Movement variables
        dx = 0
        dy = 0
        movimento = -1

        if (self.x, self.y) not in self.untried:
            self.untried[(self.x, self.y)] = self.actions.copy()
        if self.action is not None:
            #if len(self.untried[(self.x, self.y)]) > 0: #pegar sempre a primeira direcao possivel
             #   self.action = self.untried[(self.x, self.y)].pop(0)
            movement = self.directions[self.action]
            dx = movement[0]
            dy = movement[1]
            # If the position was already tested then there is nothing to be done, so we'll just pass by
            if (self.x+dx, self.y+dy) not in self.result:
                # Priority based direction
                movimento = self.body.walk(dx,dy)
                if dx != 0 and dy != 0:
                    self.rtime -= self.COST_DIAG
                else:
                    self.rtime -= self.COST_LINE
                #print(self.rtime)
                #self.passos += 1
                self.result[(self.x+dx,self.y+dy)] = movimento
                self.unbacktracked[(self.x,self.y)] = (self.last_x,self.last_y)
        if self.untried[(self.x,self.y)] == []:
            if self.unbacktracked is None or (all(self.untried) == {}):
                return
            else:
                last_dx = self.last_x - self.x
                last_dy = self.last_y - self.y
                self.body.walk(last_dx,last_dy)
                if dx != 0 and dy != 0:
                    self.rtime -= self.COST_DIAG
                else:
                    self.rtime -= self.COST_LINE
                #print(self.rtime)
                #self.passos += 1
                self.x = self.last_x
                self.y = self.last_y
                if (self.x == 0 and self.y == 0) and ((0,0) not in self.unbacktracked):
                    #print(self.passos)
                    self.resc.go_save_victims([], [])
                    return
                lastMov = self.unbacktracked.pop((self.x, self.y))
                self.last_x = lastMov[0]
                self.last_y = lastMov[1]
                #self.x = self.x + dx
                #self.y = self.y + dy
        else:
            if len(self.untried[(self.x, self.y)]) > 0:
                self.action = self.untried[(self.x, self.y)].pop(0)
        if movimento == PhysAgent.EXECUTED:
            self.last_x = self.x
            self.last_y = self.y
            self.x = self.x + dx
            self.y = self.y + dy
            seq = self.body.check_for_victim()
            if seq >= 0:
                vs = self.body.read_vital_signals(seq)
                self.rtime -= self.COST_READ
                print("exp: read vital signals of " + str(seq))
                print(vs)
        else:
            walls = 1

        return
    
    def deliberate(self) -> bool:
        """ The agent chooses the next action. The simulator calls this
        method at each cycle. Must be implemented in every agent"""

        # No more actions, time almost ended
        if self.rtime < 10.0: 
            # time to wake up the rescuer
            # pass the walls and the victims (here, they're empty)
            print(f"{self.NAME} I believe I've remaining time of {self.rtime:.1f}")
            self.resc.go_save_victims([],[])
            return False
        
        """# Movement variables
        dx = 0
        dy = 0
        movimento = -1

        if (self.x, self.y) not in self.untried:
            self.untried[(self.x, self.y)] = self.actions.copy()
        if self.action is not None:
            #if len(self.untried[(self.x, self.y)]) > 0: #pegar sempre a primeira direcao possivel
             #   self.action = self.untried[(self.x, self.y)].pop(0)
            movement = self.directions[self.action]
            dx = movement[0]
            dy = movement[1]
            # If the position was already tested then there is nothing to be done, so we'll just pass by
            if (self.x+dx, self.y+dy) in self.result:
                pass
            else:
                # Priority based direction
                movimento = self.body.walk(dx,dy)
                if dx != 0 and dy != 0:
                    self.rtime -= self.COST_DIAG
                else:
                    self.rtime -= self.COST_LINE
                #print(self.rtime)
                #self.passos += 1
                self.result[(self.x+dx,self.y+dy)] = movimento
                self.unbacktracked[(self.x,self.y)] = (self.last_x,self.last_y)
        if self.untried[(self.x,self.y)] == []:
            if self.unbacktracked is None or (all(self.untried) == {}):
                return
            else:
                last_dx = self.last_x - self.x
                last_dy = self.last_y - self.y
                self.body.walk(last_dx,last_dy)
                if dx != 0 and dy != 0:
                    self.rtime -= self.COST_DIAG
                else:
                    self.rtime -= self.COST_LINE
                #print(self.rtime)
                #self.passos += 1
                self.x = self.last_x
                self.y = self.last_y
                if (self.x == 0 and self.y == 0) and ((0,0) not in self.unbacktracked):
                    #print(self.passos)
                    self.resc.go_save_victims([], [])
                    return
                lastMov = self.unbacktracked.pop((self.x, self.y))
                self.last_x = lastMov[0]
                self.last_y = lastMov[1]
                #self.x = self.x + dx
                #self.y = self.y + dy
        else:
            if len(self.untried[(self.x, self.y)]) > 0:
                self.action = self.untried[(self.x, self.y)].pop(0)
        if movimento == PhysAgent.EXECUTED:
            self.last_x = self.x
            self.last_y = self.y
            self.x = self.x + dx
            self.y = self.y + dy
            seq = self.body.check_for_victim()
            if seq >= 0:
                vs = self.body.read_vital_signals(seq)
                self.rtime -= self.COST_READ
                print("exp: read vital signals of " + str(seq))
                print(vs)
        else:
            walls = 1"""

        
        self.dfs_Online()
        
        """dx = random.choice([-1, 0, 1])

        if dx == 0:
           dy = random.choice([-1, 1])
        else:
           dy = random.choice([-1, 0, 1])
        
        # Moves the body to another position
        result = self.body.walk(dx, dy)

        # Update remaining time
        if dx != 0 and dy != 0:
            self.rtime -= self.COST_DIAG
        else:
            self.rtime -= self.COST_LINE

        # Test the result of the walk action
        if result == PhysAgent.BUMPED:
            walls = 1  # build the map- to do
            # print(self.name() + ": wall or grid limit reached")

        if result == PhysAgent.EXECUTED:
            # check for victim returns -1 if there is no victim or the sequential
            # the sequential number of a found victim
            seq = self.body.check_for_victim()
            if seq >= 0:
                vs = self.body.read_vital_signals(seq)
                self.rtime -= self.COST_READ
                # print("exp: read vital signals of " + str(seq))
                # print(vs)"""
                
        return True

