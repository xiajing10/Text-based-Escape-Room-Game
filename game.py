import time
import random
import sys
from abc import abstractmethod

class Base(object):
    def __init__(self, name, desc):
        self.__name = name
        self.__desc = desc
    
    def __str__(self):
        return self.__name
    
    def get_name(self):
        return self.__name 
    
    @abstractmethod
    def getInfo(self):
        return self.__desc

class House(Base):
    rooms = {}
    items = {}
    doors = {} 

        
    def __init__(self, txt):
        Base.__init__(self, name='blue house', desc='')
   

    def add_room(cls,room):
        cls.rooms[room.get_name()]=room
        return room

    def new_room(self,name,desc):
        return self.add_room(Room(name,desc))

    def add_door(cls,door):
        cls.doors[door.get_name()]=door
        return door

    def new_door(self,direction,state,first,second):
        direction = direction.split('-')
        return self.add_door(Door(direction,state,self.rooms[first],self.rooms[second]))
    
    def add_item(cls,item):
        cls.items[item.get_name()]=item
        return item

    def new_item(self,name,room,state,func=None):
        if state == 'STATIONARY':
            return self.add_item(STATIONARYitem(name,self.rooms[room],state,func))
        elif state == 'USE':
            return self.add_item(USEitem(name,self.rooms[room],state,func))
        elif state == 'MOVE':
            return self.add_item(MOVEitem(name,self.rooms[room],state,func))

    def set_door(self, door):
        room1,room2 = door.first, door.second
        dir2,dir1 = tuple(door.way)
        room1.exit_ways[dir1] = door
        room2.exit_ways[dir2] = door
    
    def set_item(self,item):
        if not isinstance(item, USEitem):
            item.get_loc().inventory.add(item)
        else:
            item.get_loc().unseen.add(item)

directions = ['N','S','W','E']
start=time.mktime((1990,1,1,0,0,0,0,0,0))    
end=time.mktime((2000,12,31,23,59,59,0,0,0)) 

def random_date(start,end):
    t=random.randint(start,end)    
    date_touple=time.localtime(t)          
    date=time.strftime("%Y-%m-%d",date_touple)  
    return date

date = random_date(start, end)

class Game(Base):

    def __init__(self,name='Adventure'):
        Base.__init__(self, name, desc='')
        self.player = None
    
    def new_player(self, location):
        self.player = Player()
        self.player.set_location(location)
        return self.player
    
    def tiny_game(self):
        win = ['rock-scissors', 'scissors-paper','paper-rock']
        t = 0
        for _ in range(5):
            print()
            print("         Game is on! Rock, paper or scissors?")
            computer = random.choice(['rock', 'paper', 'scissors'])
            player = input('            Your turn:')
            print ("            Your choice: %s; Computer's choice: %s" % (player, computer))
            if player == computer:
                print( '            Peace')
            else:
                result = player + '-' + computer
                if result in win:
                    t += 1
                    print("         You win!")
                else:
                    print("         You lose!") 
            if t > 1:
                return True
                break
        return False 
                           

    def run(self):
        
        while True:
            try:
                print("")
                user_input = input(">")
            except EOFError:
                break
            if user_input == 'quit' or user_input == 'q':
                raise SystemExit
            
            try:
                u = user_input.split()
                command = u[0]
                command = self.player.commands[command]
                try:
                    if len(u) > 1:
                        noun = u[1]
                        command(noun)
                    else:
                        command()
                except TypeError:
                    print("What do you want to {}?".format(u[0]))
            except Exception:
                print("I don't understand.")

class Inventory(Base):

    def __init__(self):
        self.__inventory_list = []

    def __str__(self):
        return "{0}".format(self.__inventory_list)

    def print_list(self):
        return ', '.join([i.get_name() for i in self.__inventory_list])
        
    def add(self, item):
        self.__inventory_list.append(item)

    def remove(self,item):
        if self.check(item):
            self.__inventory_list.remove(item)
            return item
        return None
    
    def pop(self):
        return self.__inventory_list.pop()

    def isempty(self):
        if len(self.__inventory_list) == 0:
            return True
        else:
            return False
    
    def check(self,item):
        if item in self.__inventory_list:
            return True
        else:
            return False

    def holding(self):
        if self.isempty():
            print("It's empty.")
        else:
            print("You have : {} ".format(self.print_list()))


class Player(Base):

    commands_help = {
            'show': 'the room info.',\
            'commands': 'all available commands in the game.',\
            'help': 'show details of command format and info',\
            'holding': 'lists all the items you are currently holding.',\
            'quit': 'ends the game.',\
            'go DIR': 'go to direction DIR.', \
            'open DIR': 'opens the door in direction DIR in the current room.', \
            'unlock DIR': 'when the door is locked and you have the key, you can use it to unlock the door.',\
            'take ITEM': 'take the thing from your current location.', \
            'release ITEM': 'drop the thing from you holdings.',\
            'check ITEM':"check stationary item", \
            'read ITEM': 'read readable item'}

    def __init__(self):
        Base.__init__(self,'You',desc='')
        self.inventory = Inventory()
        self.location = None
        self.game = Game()
        self.commands = {'go': self.act_go, 'show': self.act_show,\
                         'take': self.act_take, 'holding': self.act_holding,\
                        'commands': self.act_commands, 'help': self.act_help,\
                        'unlock': self.act_unlock, 'open': self.act_open, \
                        'check': self.act_check, 'read': self.act_read,\
                        'release': self.act_release
                        }

    def set_location(self,loc):
        self.location = loc
        # self.moved = True
        # if the actor moved, describe the room
        print("******You are now at the %s*******" %self.location.get_name())
        if self.location.get_name() == 'gate':
            print("Oh! What a great sunny day!")
            raise SystemExit

    

    # go DIR: Let’s the player move to the room in direction DIR, 
    # if there is an open door in that direction.
    def act_go(self, dire):
        if not dire in directions:
            print("I don't understand. You can try %s." % '/'.join(directions)) 
            return False
        loc = self.location.check_way(dire)
        if loc == None:
            print("You cannot go that way.")
            return False
        else:
            self.set_location(loc)
            return True
    
    #show the description of the room, including doors and seen items.
    def act_show(self):
        if self.location:
            self.location.getInfo()
    
    #check holdings
    def act_holding(self):
        return self.inventory.holding()
   
    # take ITEM
    def act_take(self, item):
        item = House.items[item]
        thing = self.location.inventory.remove(item)
        if thing and isinstance(thing, USEitem):
            self.inventory.add(item)
            print("Taken the %s." %thing.get_name())
            return True
        else:
            print("You cannot take the %s." %item.get_name())
            return False
        
    # release ITEM
    def act_release(self, item):
        item = House.items[item]
        thing = self.inventory.pop(item,None)
        loc = self.location
        if thing:
            self.location.inventory.add(thing)
            thing.change_loc(loc)
            print("Released the %s." %thing.get_name())
            return True
        else:
            print("You don't have %s."%thing.get_name())
            return False
    
    # look at stationary item
    def act_check(self, item):
        item = House.items[item]
        if not isinstance(item, USEitem):
            if item.unchecked:
                if not self.location.unseen.isempty():
                    thing = self.location.unseen.pop()
                    self.location.inventory.add(thing)
                    item.unchecked = False
                    print("{} on the {}." .format(thing.get_name(), item.get_name()))
                    return True
            else:
                print("Nothing found.")
                return False
        else:
            print("I don't understand.")
            return False

    # read readable item
    def act_read(self,item):
        item = House.items[item]
        if item not in self.inventory:
            print("You should take that first.")
            return False
        if  not isinstance(item, USEitem) or item.func != 'read':
            print("I don't understand.")
            return False
        if item.get_name() == "calendar":
            print("Today is {}. \nToday is marked as anniversary. \nSay 'I love you' to her.".format(date))
            return True
        if item.get_name() == "book":
            result = self.game.tiny_game()
            if result:
                print("Well done!")
                door = self.location.exit_ways['N']
                door.open()
                return True
            else:
                print("You've run out of try.")
                # raise SystemExit
                return False
        if item.get_name() == 'letter':
            print('''
            Dear,
                I've made your favorite chicken soup for you. Remember to call me if you like it :)
            Your love
            ''')
        if item.get_name() == 'diary':
            print('''
            Day 1:
                It was a snowy day. I said to her. She accepted. How happy was I!
            Day 2:
                Great party!
                ...
            Day 100:
                I almost forgot the day. I should mark it on the calendar.''')

    def act_commands(cls):
        for c in cls.commands_help:
            print(c + " | " + cls.commands_help[c])

    def act_help(self):
        print('''
        Try 'commands' to show all the commands I understand.
        Enjoy your journey!''')
        # if command in UI.commands_help:
        #     print(UI.commands_help[command])
        # else:
        #     print("I don't understand.")
        #     self.act_commands()

    def act_unlock(self, dire):
        door = self.location.exit_ways[dire]
        if door.state == 'keylocked':
            if self.inventory.check(House.items['key']):
                door.open()
                print("Opened the door!")
                return True
            else:
                print("You don't have the key.")
                return False
        elif door.state == 'codelocked':
            user_try = input("Please input the code:")
            code = ''.join(date.split('-'))
            if user_try == code[-4:]:
                door.open()
                print("Opened the door!")
                return True
            else:
                print("Failed. Code is wrong.")
                return False

    def act_open(self, dire):
        door = self.location.exit_ways[dire]
        if door.state == 'closed':
            door.open()
            print("Opened the door.")
            return True
        print("You cannot open it.")
        return False


class Room(Base):
    def __init__(self,name, desc=''):
        Base.__init__(self, name, desc)
        self.exit_ways = {'N':None,'S':None,'W':None,'E':None}
        self.inventory=Inventory()
        self.unseen = Inventory()
    
    def getInfo(self):
        if self.inventory.isempty():
            print(super().getInfo() + '\n' + \
            "You have found doors towards: {}".format(self.all_doors()))
        else:
            print(super().getInfo() + '\n' + \
                "Found doors towards: {}".format(self.all_doors())  + '\n' + \
                "There is {} here.".format(self.inventory.print_list()))

    def all_doors(self):
        d = []
        for i in self.exit_ways:
            if self.exit_ways[i]:
                d.append(i)
        return ', '.join(d)

    def check_way(self,dire):
        door = self.exit_ways[dire]
        if door:
            if door.isopen():
                return door.way_to(dire)
            else:
                print("The door is %s." %door.state)
                return None
        return None
    
    def go(self,dire):
        loc = self.exit_ways[dire]
        if loc == None:
            print("You cannot go that way.")
            return False
        else:
            Player.set_location(loc)
            return True
    
class Door(Base):
    def __init__(self, direction,state,first,second, desc=''):
        self.__name = first.get_name() + '-' + second.get_name()
        Base.__init__(self, self.__name, desc)
        self.way = direction
        self.__directions = {'N':None,'S':None,'W':None,'E':None}
        self.state = state
        self.first = first
        self.second = second
        self.__directions[direction[0]] = self.first
        self.__directions[direction[1]] = self.second

    def open(self):
        self.state = 'open'

    def isopen(self):
        if self.state == 'open':
            return True
        return False
    
    def islocked(self):
        if self.state == 'locked':
            return True
        return False

    def way_to(self,dire):
        return self.__directions[dire]


class Item(Base):
    def __init__(self,name,room,state,func=None,desc=''):
        Base.__init__(self, name, desc)
        self.__location = room
        self.__state=state

    def get_loc(self):
        return self.__location
    
    def getInfo(self):
        print(super().getInfo())


class USEitem(Item):

    def __init__(self,name,room,state,func,desc=''):
        super().__init__(name,room,state,func,desc='')
        self.func = func

    def change_loc(self, loc):
        self.__location = loc
    
    def getInfo(self):
        print(super().getInfo())


class STATIONARYitem(Item):

    def __init__(self,name,room,state,desc=''):
        super().__init__(name,room,state,func=None,desc='')
        self.unchecked = True

    def getInfo(self):
        print(super().getInfo())


class MOVEitem(Item):

    def __init__(self,name,room,state,desc=''):
        super().__init__(name,room,state,func=None,desc='')
        self.unchecked = True



'''----------------------------------------------------------------------'''
if __name__ == "__main__":
    print('''Welcome to my house!
    if you need any 'help' please tell me!''')

    txt = sys.argv[1]
    house = House(txt) 
    game = Game()
    player = game.new_player(house.start)
    game.player = player

    game.run()
    
