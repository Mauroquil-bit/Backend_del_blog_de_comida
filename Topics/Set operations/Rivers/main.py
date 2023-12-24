# work with these variables
rivers = set(input().split())
states = set(input().split())

unique_rivers = rivers - states

print(unique_rivers)

