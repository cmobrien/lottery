import csv
import copy


class Unit:
      def __init__(self, uid, last, prefs):
            self.uid = uid
            self.last = last
            self.current = last
            self.prefs = prefs
      

class Person(Unit):
      def __init__(self, name, kerberos, last, prefs):
            Unit.__init__(self, kerberos, last, prefs)
            self.name = name
            self.size = 1

      def __str__(self):
            return self.name + \
                   " (" + self.uid + "): " + \
                   repr(self.last) + " " + \
                   str(self.prefs) + " -> " + \
                   repr(self.current)

      def __repr__(self):
            return self.name + " (" + self.uid + ")"

class Duet(Unit):
      def __init__(self, person1, person2):
            if len(person1.prefs) <= len(person2.prefs):
                  Unit.__init__(self, person1.kerberos, person1.last, person1.prefs)
            else:
                  Unit.__init__(self, person1.kerberos, person2.last, person2.prefs)
            self.person1 = person1
            self.person2 = person2
            self.size = 2


class Trio(Unit):
      def __init__(self, person1, person2, person3):
            l = min(len(person1.prefs), len(person2.prefs), len(person3.prefs))
            if l == len(person1.prefs):
                  Unit.__init__(self, person1.kerberos, person1.last, person1.prefs)
            elif l == len(person2.prefs):
                  Unit.__init__(self, person1.kerberos, person2.last, person2.prefs)
            else:
                  Unit.__init__(self, person1.kerberos, person3.last, person3.prefs)
            self.person1 = person1
            self.person2 = person2
            self.person3 = person3
            self.size = 3


class Quad(Unit):
      def __init__(self, person1, person2, person3, person4):
            l = min(len(person1.prefs), len(person2.prefs), len(person3.prefs), len(person4.prefs))
            if l == len(person1.prefs):
                  Unit.__init__(self, person1.kerberos, person1.last, person1.prefs)
            elif l == len(person2.prefs):
                  Unit.__init__(self, person1.kerberos, person2.last, person2.prefs)
            elif l == len(person3.prefs):
                  Unit.__init__(self, person1.kerberos, person3.last, person3.prefs)
            else:
                  Unit.__init__(self, person1.kerberos, person4.last, person4.prefs)
            self.person1 = person1
            self.person2 = person2
            self.person3 = person3
            self.person4 = person4
            self.size = 4

            

class Room:
      def __init__(self, resident, occupancy, number):
            self.resident = resident
            self.occupancy = occupancy
            self.number = number

      def __repr__(self):
            return str(self.number)

      def __str__(self):
            return "[" + str(self.number) + \
                  " (" + str(self.occupancy) + "): " + \
                  repr(self.resident) + "]"

      def is_open(self):
            return self.resident == None

#ROOMS = {1: Room(None, 1, 1), 2: Room(None, 1, 2), 3: Room(None, 1, 3), 4: Room(None, 1, 4)}

def build_rooms(filename):
      rooms = {}
      with open(filename, 'rb') as docfile:
            reader = csv.reader(docfile.read().split('\n'), delimiter=',')
            for row in reader:
                  if len(row) > 0:
                        number = int(row[0])
                        if row[1] == 'Single':
                              size = 1
                        elif row[1] == 'Double':
                              size = 2
                        elif row[1] == 'Triple':
                              size = 3
                        elif row[1] == 'Quad':
                              size = 4
                        rooms[number] = Room(None, size, number)
      return rooms


def build_people(filename):
      people = {}
      with open(filename, 'rb') as docfile:
            reader = csv.reader(docfile.read().split('\n'), delimiter=',')
            for row in reader:
                  if len(row) > 0:
                        kerberos = row[0]
                        name = row[1] + " " + row[2]
                        people[kerberos] = Person(name, kerberos, None, [])
      return people

def assign_current_rooms(people, rooms, filename):
      assignments = {}
      with open(filename, 'rb') as docfile:
            reader = csv.reader(docfile.read().split('\n'), delimiter=',')
            for row in reader:
                  if len(row) > 0:
                        kerberos = row[4]
                        room = int(row[1])
                        if kerberos != '':
                              assignments[kerberos] = room
            for person in people.values():
                  if person.uid in assignments:
                        person.last = assignments[person.uid]
                        person.current = assignments[person.uid]
                        rooms[person.last].resident = person.uid
      return people, rooms

PEOPLE, ROOMS = assign_current_rooms(build_people('residents.csv'), build_rooms('rooms.csv'), 'current.csv')


def populate_preferences(filename, people, rooms):
      with open(filename, 'rb') as docfile:
            reader = csv.reader(docfile.read().split('\n'), delimiter=',')
            for row in reader:
                  if len(row) > 0:
                        kerberos = row[0]
                        prefs = [int(r) for r in row[1:]]
                        people[kerberos].prefs = prefs
      return people


def available_room(person, rooms):
      for n in person.prefs:
            room = rooms[n]
            if room.is_open():
                  return True
      return False

def free_room(room_number, people, rooms, waiting):
      room = rooms[room_number]
      if room.number in waiting and waiting[room.number] != []:
            nex = people[waiting[room.number][0]]
            waiting[room.number].remove(nex.uid)
            found = False
            for r in nex.prefs:
                  if found:
                        if r in waiting and nex in waiting[r.number]:
                              waiting[r.number].remove(nex.uid)
                  if r == room:
                        found = True
            old_room = rooms[nex.current]
            old_person = people[room.resident]
            nex.current = room.number
            room.resident = nex.uid
            old_person.current = None
            old_room.resident = None
            free_room(old_room.number, people, rooms, waiting)
            return True, people, rooms, waiting
      if room.resident != None:
            people[room.resident].current = None
      room.resident = None
      return False, people, rooms, waiting

def match(people, rooms, order):
      waiting = {}
      for kerberos in order:
            person = people[kerberos]
            # See what happens if we freed their room
            placed, new_people, new_rooms, new_waiting = free_room(
                  rooms[person.current].number,
                  copy.deepcopy(people),
                  copy.deepcopy(rooms),
                  copy.deepcopy(waiting))
            # Make changes if there is still somwehere for them to go
            if available_room(new_people[person.uid], new_rooms):
                  people = new_people
                  person = people[kerberos]
                  rooms = new_rooms
                  waiting = new_waiting
            else:
                  person.current = person.last
                  rooms[person.last].resident = person.uid
            for n in person.prefs:
                  room = rooms[n]
                  if room.is_open():
                        person.current = room.number
                        room.resident = person.uid
                        break
                  else:
                        if room in waiting:
                              waiting[room.number].append(person.uid)
                        else:
                              waiting[room.number] = [person.uid]
      return people, rooms



## Error Codes:
##
## ERROR 0: name room -> name was assigned to room even when they didn't pref or squat it
## ERROR 1: name room -> name should have been assigned to room but it was empty
## ERROR 2: name1 name2 room -> name2 got room over name1, but name2 was lower in the lottery
## ERROR 3: name1 name2 -> name1 and name2 should switch rooms
## ERROR 4: name1 namd2 room -> name1 and name2 were both assigned to room but did not pref each other
def validate(people, rooms, order):
      for p in people.values():
            if p.current != None and rooms[p.current].resident != p.uid:
                  print "ROOMS AND PEOPLE DON'T MATCH"
                  return
      checked = {}
      for kerberos in order:
            person = people[kerberos]
            room = rooms[person.current]
            # Someone is assigned to a room they didn't pref or squat
            if room.number not in person.prefs and room.number != person.last:
                  print "ERROR 0:", person.uid, room.number
            for n in person.prefs:
                  pref_room = rooms[n]
                  if pref_room == room:
                        break
                  # Someone should have been assigned to a room which was empty
                  if pref_room.resident == None:
                        print "ERROR 1:", person.uid, pref_room.number
                  else:
                        holder = people[pref_room.resident]
                        # Someone lower in the lottery got the room without squatting
                        if holder.uid != person.uid and not holder.uid in checked:
                              if pref_room.number != holder.last:
                                    print "ERROR 2:", person.uid, holder.uid, pref_room.number
                        else:
                              # Two people should switch rooms to make everyone happier
                              if room.number in holder.prefs and \
                                 (rooms[holder.current].number == rooms[holder.last].number \
                                  or holder.prefs.index(room.number) < holder.prefs.index(holder.current)):
                                    print "ERROR 3:", person.uid, holder.uid
            checked[person.uid] = True
      print "VALIDATION COMPLETE"

def lottery(order, people, rooms):
      people = populate_preferences('data.csv', people, rooms)
      people, rooms = match(people, rooms, order)
      print_results(order, people)
      #for room in rooms:
      #      print rooms[room]
      #validate(people, rooms, order)

def print_results(order, people):
      print '---------'
      for kerberos in order:
            person = people[kerberos]
            print '| ' + person.uid + ' | ' + str(person.current) + ' |'
      print '---------'

##lottery(["a", "b", "c", "d"], ROOMS)
##
##
##a = Person('A', 'a', 3, [1,2])
##a.current = 4
##b = Person('B', 'b', 2, [1,3])
##b.current = 1
##c = Person('C', 'c', 1, [2,3])
##c.current = 2
##
##r1 = Room('b', 1, 1)
##r2 = Room('c', 1, 2)
##r3 = Room(None, 1, 3)
##r4 = Room('a', 1, 4)
##
##validate({'a':a, 'b':b, 'c':c}, {1:r1, 2:r2, 3:r3, 4:r4}, ['a', 'b', 'c'])
##                  
