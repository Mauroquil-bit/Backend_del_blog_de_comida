# work with these variables
eugene = set(input().split())
rose = set(input().split())

potential_countries = eugene.symmetric_difference(rose)

print(potential_countries)
