# work with these variables
violinists = set(input().split(', '))
german_speakers = set(input().split(', '))

both_talents = violinists & german_speakers

print(both_talents)

