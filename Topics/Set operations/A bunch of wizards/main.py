gryffindor = set(input().split())
ravenclaw = set(input().split())
slytherin = set(input().split())
hufflepuff = set(input().split())

all_students = gryffindor.union(ravenclaw, slytherin, hufflepuff)

print(all_students)